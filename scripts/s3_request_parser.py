# AGENT_CONTEXT: Read .agent/README.md for rules
#!/usr/bin/env python3
"""
---
id: SCRIPT-0037
type: script
owner: platform-team
status: active
maturity: 1
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0037.py
  evidence: declared
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
---
"""
from __future__ import annotations

# Owner: platform
"""
S3 Request parser/generator (Contract-Driven).

Maps:
  docs/20-contracts/s3-requests/<env>/<s3-id>.yaml
to:
  envs/<env>/s3/generated/<s3-id>.auto.tfvars.json
and:
  generated/iam/<application>-s3-policy.json

Modes:
  validate  - schema validation + guardrail enforcement
  generate  - writes tfvars + IAM policy output files

Reference: ADR-0170, schemas/requests/s3.schema.yaml
"""

import argparse
import csv
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# Hardcoded enums (S3 buckets are persistent, no ephemeral)
VALID_ENVIRONMENTS = {"dev", "test", "staging", "prod"}
VALID_PURPOSE_TYPES = {"logs", "uploads", "backups", "data-lake", "static-assets"}
VALID_STORAGE_CLASSES = {"standard", "intelligent-tiering", "standard-ia", "glacier"}
VALID_ENCRYPTION_TYPES = {"sse-s3", "sse-kms"}
VALID_PUBLIC_ACCESS = {"blocked", "exception-approved"}
VALID_RETENTION_TYPES = {"indefinite", "time-bounded", "compliance-driven"}

ID_PATTERN = re.compile(r"^S3-[0-9]{4}$")
APP_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,30}$")
BUCKET_PATTERN = re.compile(r"^goldenpath-[a-z]+-[a-z0-9-]+-[a-z0-9-]+$")
KMS_ALIAS_PATTERN = re.compile(r"^alias/[a-z0-9-]+$")
LOGGING_TARGET_PATTERN = re.compile(r"^goldenpath-[a-z]+-logs$")


@dataclass(frozen=True)
class S3Request:
    """Parsed S3 bucket request contract."""

    s3_id: str
    environment: str
    bucket_name: str
    owner: str
    application: str
    requester: str
    created_date: Optional[str]

    # Purpose
    purpose_type: str
    purpose_description: str

    # Configuration
    storage_class: str
    encryption_type: str
    kms_key_alias: Optional[str]
    versioning: bool
    public_access: str

    # Retention
    retention_type: str
    retention_rationale: str

    # Lifecycle (optional)
    lifecycle_expire_days: Optional[int]
    lifecycle_transition_ia_days: Optional[int]
    lifecycle_transition_glacier_days: Optional[int]

    # Access logging
    access_logging_enabled: bool
    access_logging_target: Optional[str]

    # Cost
    cost_alert_gb: int
    cost_center: str

    # Other
    cors_enabled: bool


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file and return dict."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def parse_request(doc: Dict[str, Any], src_path: Path) -> S3Request:
    """Parse S3 request YAML into dataclass."""
    md = doc.get("metadata", {})
    spec = doc.get("spec", {})

    # Top-level fields
    s3_id = doc.get("id") or md.get("id")
    environment = doc.get("environment") or md.get("environment")
    owner = doc.get("owner") or md.get("owner")
    application = doc.get("application") or md.get("application")
    requester = doc.get("requester") or md.get("requester")
    created_date = md.get("created") or md.get("created_date") or md.get("createdDate")

    # Spec fields
    bucket_name = spec.get("bucketName")

    # Purpose (nested object)
    purpose = spec.get("purpose", {})
    purpose_type = purpose.get("type")
    purpose_description = purpose.get("description")

    # Configuration
    storage_class = spec.get("storageClass", "standard")

    encryption = spec.get("encryption", {})
    encryption_type = encryption.get("type", "sse-s3")
    kms_key_alias = encryption.get("kmsKeyAlias")

    versioning = spec.get("versioning", True)
    public_access = spec.get("publicAccess", "blocked")

    # Retention
    retention = spec.get("retentionPolicy", {})
    retention_type = retention.get("type")
    retention_rationale = retention.get("rationale")

    # Lifecycle (optional)
    lifecycle = spec.get("lifecycle", {})
    lifecycle_expire_days = lifecycle.get("expireDays")
    lifecycle_transition_ia_days = lifecycle.get("transitionToIaDays")
    lifecycle_transition_glacier_days = lifecycle.get("transitionToGlacierDays")

    # Access logging
    access_logging = spec.get("accessLogging", {})
    access_logging_enabled = access_logging.get("enabled", False)
    access_logging_target = access_logging.get("targetBucket")

    # Cost
    cost_alert_gb = spec.get("costAlertGb")
    tags = spec.get("tags", {})
    cost_center = tags.get("costCenter")

    # Other
    cors_enabled = spec.get("corsEnabled", False)

    # Validate required fields
    missing = [k for k, v in {
        "id": s3_id,
        "environment": environment,
        "owner": owner,
        "application": application,
        "requester": requester,
        "spec.bucketName": bucket_name,
        "spec.purpose.type": purpose_type,
        "spec.purpose.description": purpose_description,
        "spec.encryption.type": encryption_type,
        "spec.retentionPolicy.type": retention_type,
        "spec.retentionPolicy.rationale": retention_rationale,
        "spec.costAlertGb": cost_alert_gb,
        "spec.tags.costCenter": cost_center,
    }.items() if not v]

    if missing:
        raise ValueError(f"{src_path}: missing required fields: {', '.join(missing)}")

    return S3Request(
        s3_id=str(s3_id),
        environment=str(environment),
        bucket_name=str(bucket_name),
        owner=str(owner),
        application=str(application),
        requester=str(requester),
        created_date=str(created_date) if created_date else None,
        purpose_type=str(purpose_type),
        purpose_description=str(purpose_description),
        storage_class=str(storage_class),
        encryption_type=str(encryption_type),
        kms_key_alias=str(kms_key_alias) if kms_key_alias else None,
        versioning=bool(versioning),
        public_access=str(public_access),
        retention_type=str(retention_type),
        retention_rationale=str(retention_rationale),
        lifecycle_expire_days=int(lifecycle_expire_days) if lifecycle_expire_days else None,
        lifecycle_transition_ia_days=int(lifecycle_transition_ia_days) if lifecycle_transition_ia_days else None,
        lifecycle_transition_glacier_days=int(lifecycle_transition_glacier_days) if lifecycle_transition_glacier_days else None,
        access_logging_enabled=bool(access_logging_enabled),
        access_logging_target=str(access_logging_target) if access_logging_target else None,
        cost_alert_gb=int(cost_alert_gb),
        cost_center=str(cost_center),
        cors_enabled=bool(cors_enabled),
    )


def validate_enums(req: S3Request, src_path: Path) -> None:
    """Validate enum values against hardcoded allowed lists."""
    errors = []

    if req.environment not in VALID_ENVIRONMENTS:
        errors.append(f"environment='{req.environment}' not in {VALID_ENVIRONMENTS}")

    if req.purpose_type not in VALID_PURPOSE_TYPES:
        errors.append(f"purpose.type='{req.purpose_type}' not in {VALID_PURPOSE_TYPES}")

    if req.storage_class not in VALID_STORAGE_CLASSES:
        errors.append(f"storageClass='{req.storage_class}' not in {VALID_STORAGE_CLASSES}")

    if req.encryption_type not in VALID_ENCRYPTION_TYPES:
        errors.append(f"encryption.type='{req.encryption_type}' not in {VALID_ENCRYPTION_TYPES}")

    if req.public_access not in VALID_PUBLIC_ACCESS:
        errors.append(f"publicAccess='{req.public_access}' not in {VALID_PUBLIC_ACCESS}")

    if req.retention_type not in VALID_RETENTION_TYPES:
        errors.append(f"retentionPolicy.type='{req.retention_type}' not in {VALID_RETENTION_TYPES}")

    if errors:
        raise ValueError(f"{src_path}: invalid enum values: {'; '.join(errors)}")


def validate_guardrails(req: S3Request, src_path: Path) -> List[str]:
    """Validate guardrails and return warnings."""
    errors = []
    warnings = []

    # SSE-KMS required in staging/prod
    if req.environment in ("staging", "prod") and req.encryption_type != "sse-kms":
        errors.append(f"SSE-KMS encryption required for {req.environment} environment")

    # KMS key alias required when using SSE-KMS
    if req.encryption_type == "sse-kms" and not req.kms_key_alias:
        errors.append("kmsKeyAlias required when encryption.type is sse-kms")
    if req.kms_key_alias and not KMS_ALIAS_PATTERN.match(req.kms_key_alias):
        errors.append("kmsKeyAlias must match alias/<name> pattern")

    # Access logging required in staging/prod
    if req.environment in ("staging", "prod") and not req.access_logging_enabled:
        errors.append(f"accessLogging required for {req.environment} environment")
    if req.access_logging_enabled and not req.access_logging_target:
        errors.append("accessLogging.targetBucket required when accessLogging.enabled is true")
    if req.access_logging_target and not LOGGING_TARGET_PATTERN.match(req.access_logging_target):
        errors.append("accessLogging.targetBucket must match goldenpath-<env>-logs pattern")

    # Lifecycle required for time-bounded/compliance-driven retention
    if req.retention_type in ("time-bounded", "compliance-driven"):
        if not req.lifecycle_expire_days and not req.lifecycle_transition_ia_days and not req.lifecycle_transition_glacier_days:
            errors.append("lifecycle rules required when retentionPolicy.type is not 'indefinite'")

    # Bucket naming convention
    if not BUCKET_PATTERN.match(req.bucket_name):
        errors.append("bucketName must match goldenpath-{env}-{app}-{purpose} pattern")
    if not req.bucket_name.startswith(f"goldenpath-{req.environment}-"):
        errors.append("bucketName must use the requested environment prefix")

    # Request/application identifier hygiene
    if not ID_PATTERN.match(req.s3_id):
        errors.append("id must match S3-0000 format")
    if not APP_PATTERN.match(req.application):
        errors.append("application must match ^[a-z][a-z0-9-]{2,30}$")

    # Cost alert bounds
    if not 1 <= req.cost_alert_gb <= 10000:
        errors.append("costAlertGb must be between 1 and 10000")

    # Public access exception warning
    if req.public_access == "exception-approved":
        warnings.append("Public access exception requires platform-approval label on PR")

    # Static assets warning
    if req.purpose_type == "static-assets":
        warnings.append("Static asset buckets require platform review for CDN/public access")

    if errors:
        raise ValueError(f"{src_path}: guardrail violations: {'; '.join(errors)}")

    return warnings


def validate_request(req: S3Request, src_path: Path) -> List[str]:
    """Run all validations and return warnings."""
    validate_enums(req, src_path)
    return validate_guardrails(req, src_path)


def generate_tfvars(req: S3Request) -> Dict[str, Any]:
    """Generate Terraform tfvars for S3 bucket."""
    lifecycle_rules = []

    if req.lifecycle_expire_days:
        lifecycle_rules.append({
            "id": "expire-objects",
            "enabled": True,
            "expiration": {"days": req.lifecycle_expire_days},
        })

    if req.lifecycle_transition_ia_days:
        lifecycle_rules.append({
            "id": "transition-to-ia",
            "enabled": True,
            "transition": [{
                "days": req.lifecycle_transition_ia_days,
                "storage_class": "STANDARD_IA",
            }],
        })

    if req.lifecycle_transition_glacier_days:
        lifecycle_rules.append({
            "id": "transition-to-glacier",
            "enabled": True,
            "transition": [{
                "days": req.lifecycle_transition_glacier_days,
                "storage_class": "GLACIER",
            }],
        })

    return {
        "s3_bucket": {
            "bucket_name": req.bucket_name,
            "versioning_enabled": req.versioning,
            "encryption": {
                "type": req.encryption_type.upper().replace("-", "_"),
                "kms_key_alias": req.kms_key_alias,
            },
            "public_access_block": {
                "block_public_acls": True,
                "block_public_policy": True,
                "ignore_public_acls": True,
                "restrict_public_buckets": req.public_access == "blocked",
            },
            "lifecycle_rules": lifecycle_rules,
            "logging": {
                "enabled": req.access_logging_enabled,
                "target_bucket": req.access_logging_target,
            } if req.access_logging_enabled else None,
            "tags": {
                "Environment": req.environment,
                "Owner": req.owner,
                "Application": req.application,
                "Purpose": req.purpose_type,
                "CostCenter": req.cost_center,
                "ManagedBy": "terraform",
                "RequestId": req.s3_id,
            },
        },
        "cost_alert": {
            "threshold_gb": req.cost_alert_gb,
            "alarm_name": f"{req.bucket_name}-storage-alert",
        },
    }


def generate_iam_policy(req: S3Request) -> Dict[str, Any]:
    """Generate IAM policy snippet for application access."""
    bucket_arn = f"arn:aws:s3:::{req.bucket_name}"
    statements = [
        {
            "Sid": f"S3Access{req.s3_id.replace('-', '')}",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
            ],
            "Resource": [
                bucket_arn,
                f"{bucket_arn}/*",
            ],
        }
    ]

    if req.encryption_type == "sse-kms":
        statements.append(
            {
                "Sid": f"KmsAccess{req.s3_id.replace('-', '')}",
                "Effect": "Allow",
                "Action": [
                    "kms:Decrypt",
                    "kms:Encrypt",
                    "kms:GenerateDataKey",
                    "kms:DescribeKey",
                ],
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "kms:EncryptionContext:aws:s3:arn": [
                            bucket_arn,
                            f"{bucket_arn}/*",
                        ]
                    }
                },
            }
        )

    return {
        "Version": "2012-10-17",
        "Statement": statements,
    }


def generate_audit_record(req: S3Request, action: str, status: str, approver: str) -> Dict[str, Any]:
    """Generate audit record for governance registry."""
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "request_id": req.s3_id,
        "bucket_name": req.bucket_name,
        "owner": req.owner,
        "environment": req.environment,
        "purpose": req.purpose_type,
        "action": action,
        "approver": approver,
        "status": status,
    }


def read_catalog_documents(path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Read catalog YAML with optional frontmatter document."""
    if not path.exists():
        return {}, {
            "version": "1.0",
            "domain": "platform-core",
            "owner": "platform-team",
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "managed_by": "platform-team",
            "buckets": {},
        }

    docs = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    if len(docs) == 1:
        return {}, docs[0] or {}
    frontmatter = docs[0] or {}
    body = docs[1] or {}
    return frontmatter, body


def write_catalog_documents(path: Path, frontmatter: Dict[str, Any], body: Dict[str, Any], dry_run: bool) -> None:
    """Write catalog YAML, preserving frontmatter as a separate document."""
    payload = [frontmatter, body] if frontmatter else [body]
    if dry_run:
        print(f"[DRY-RUN] Would write catalog: {path}")
        print(yaml.safe_dump_all(payload, sort_keys=False))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump_all(payload, sort_keys=False, explicit_start=True),
        encoding="utf-8",
    )


def update_s3_catalog(
    req: S3Request,
    catalog_path: Path,
    region: str,
    status: str,
    dry_run: bool,
) -> None:
    """Update the shared S3 catalog with this request."""
    frontmatter, body = read_catalog_documents(catalog_path)
    body.setdefault("buckets", {})
    body["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    bucket_key = req.bucket_name
    created_date = req.created_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    body["buckets"][bucket_key] = {
        "metadata": {
            "id": req.s3_id,
            "owner": req.owner,
            "application": req.application,
            "requested_by": req.requester,
            "purpose": req.purpose_type,
            "environment": req.environment,
            "status": status,
            "created_date": created_date,
        },
        "aws": {
            "bucket_name": req.bucket_name,
            "region": region,
            "arn": f"arn:aws:s3:::{req.bucket_name}",
        },
        "governance": {
            "versioning": req.versioning,
            "encryption": req.encryption_type,
            "public_access_block": req.public_access == "blocked",
            "access_logging": req.access_logging_enabled,
        },
        "retention": {
            "type": req.retention_type,
            "expire_days": req.lifecycle_expire_days,
            "transition_to_ia_days": req.lifecycle_transition_ia_days,
            "transition_to_glacier_days": req.lifecycle_transition_glacier_days,
        },
        "cost": {
            "cost_center": req.cost_center,
            "alert_threshold_gb": req.cost_alert_gb,
        },
    }

    write_catalog_documents(catalog_path, frontmatter, body, dry_run)


def append_audit_record(path: Path, record: Dict[str, Any], dry_run: bool) -> None:
    """Append an audit record to a CSV file."""
    header = [
        "timestamp_utc",
        "request_id",
        "bucket_name",
        "owner",
        "environment",
        "purpose",
        "action",
        "approver",
        "status",
    ]
    if dry_run:
        print(f"[DRY-RUN] Would append audit record: {path}")
        print(record)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        if not exists:
            writer.writeheader()
        writer.writerow({k: record.get(k, "") for k in header})


def tfvars_output_path(output_root: Path, req: S3Request) -> Path:
    """Get output path for tfvars file."""
    return output_root / req.environment / "s3" / "generated" / f"{req.s3_id}.auto.tfvars.json"


def iam_policy_output_path(output_root: Path, req: S3Request) -> Path:
    """Get output path for IAM policy file."""
    return output_root / "generated" / "iam" / f"{req.application}-s3-policy.json"


def write_json(path: Path, data: Dict[str, Any], dry_run: bool) -> None:
    """Write JSON file (or print in dry-run mode)."""
    if dry_run:
        print(f"[DRY-RUN] Would write: {path}")
        print(json.dumps(data, indent=2))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="S3 Request Parser (SCRIPT-0037)")
    parser.add_argument(
        "--mode",
        choices=["validate", "generate"],
        required=True,
        help="validate: check contract; generate: write tfvars + IAM policy",
    )
    parser.add_argument(
        "--input-files",
        nargs="+",
        required=True,
        help="S3 request YAML files to process",
    )
    parser.add_argument(
        "--output-root",
        default="envs",
        help="Root directory for output files (default: envs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output instead of writing files",
    )
    parser.add_argument(
        "--catalog-path",
        default="",
        help="Optional S3 catalog path to update",
    )
    parser.add_argument(
        "--catalog-region",
        default="",
        help="Region to record in the S3 catalog (defaults to AWS_REGION)",
    )
    parser.add_argument(
        "--catalog-status",
        default="active",
        help="Catalog status to write (default: active)",
    )
    parser.add_argument(
        "--audit-path",
        default="",
        help="Optional audit CSV path to append",
    )
    parser.add_argument(
        "--audit-action",
        default="apply",
        help="Audit action to record (default: apply)",
    )
    parser.add_argument(
        "--audit-status",
        default="success",
        help="Audit status to record (default: success)",
    )
    parser.add_argument(
        "--audit-approver",
        default="",
        help="Audit approver (defaults to GITHUB_ACTOR)",
    )
    args = parser.parse_args()

    exit_code = 0

    for input_file in args.input_files:
        path = Path(input_file)
        try:
            doc = load_yaml(path)
            req = parse_request(doc, path)
            warnings = validate_request(req, path)

            for warning in warnings:
                print(f"[WARN] {path}: {warning}")

            if args.mode == "generate":
                # Generate tfvars
                tfvars = generate_tfvars(req)
                tfvars_path = tfvars_output_path(Path(args.output_root), req)
                write_json(tfvars_path, tfvars, args.dry_run)

                # Generate IAM policy
                iam_policy = generate_iam_policy(req)
                iam_path = iam_policy_output_path(Path(args.output_root), req)
                write_json(iam_path, iam_policy, args.dry_run)

                if not args.dry_run:
                    print(f"[OK] {path} -> {tfvars_path}, {iam_path}")
                else:
                    print(f"[DRY-RUN] {path} -> {tfvars_path}, {iam_path}")

                if args.catalog_path:
                    region = (
                        args.catalog_region
                        or os.environ.get("AWS_REGION")
                        or os.environ.get("AWS_DEFAULT_REGION")
                        or "unknown"
                    )
                    update_s3_catalog(
                        req,
                        Path(args.catalog_path),
                        region,
                        args.catalog_status,
                        args.dry_run,
                    )

                if args.audit_path:
                    approver = args.audit_approver or os.environ.get("GITHUB_ACTOR", "unknown")
                    record = generate_audit_record(req, args.audit_action, args.audit_status, approver)
                    append_audit_record(Path(args.audit_path), record, args.dry_run)
            else:
                print(f"[OK] {path} validated")

        except ValueError as e:
            print(f"[ERROR] {e}")
            exit_code = 1
        except Exception as e:
            print(f"[ERROR] {path}: unexpected error: {e}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
