#!/usr/bin/env python3
"""
---
id: SCRIPT-0034
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0034.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

from __future__ import annotations

# Owner: platform
"""
RDS Request parser/generator (Adapted Standard).

Maps:
  docs/20-contracts/rds-requests/<env>/<rds-id>.yaml
to:
  envs/<env>-rds/generated/<rds-id>.auto.tfvars.json
and:
  gitops/kustomize/overlays/<env>/apps/<service>/externalsecrets/<rds-id>.yaml

Modes:
  validate  - schema-ish validation + enum enforcement
  generate  - writes tfvars + ExternalSecret output files
"""


import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


# Size to AWS instance class mapping
SIZE_TO_INSTANCE = {
    "small": "db.t3.micro",
    "medium": "db.t3.small",
    "large": "db.t3.medium",
    "xlarge": "db.r6g.large",
}


@dataclass(frozen=True)
class RdsRequest:
    """RDS database request contract fields."""

    rds_id: str
    service: str
    environment: str
    databaseName: str
    username: str
    size: str
    domain: str
    owner: str
    requester: str
    risk: str

    # Optional fields with defaults
    storageGb: int = 20
    maxStorageGb: int = 50
    backupRetentionDays: int = 7
    multiAz: bool = False
    performanceInsights: bool = True


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_enums(enums_path: Path) -> Dict[str, List[str]]:
    """Load RDS-specific enums from metadata."""
    data = load_yaml(enums_path)
    rds = data.get("rds", {})

    def values(key: str) -> List[str]:
        node = rds.get(key, {})
        return list(node.get("values", []))

    return {
        "size": values("instance_sizes"),
        "engine": values("engines"),
        "requestStatus": values("request_status"),
        "environment": data.get("environments", []),
        "domain": data.get("domains", []),
        "owner": data.get("owners", []),
        "risk": data.get("risk_profile_security_risk", []),
    }


def parse_request(doc: Dict[str, Any], src_path: Path) -> RdsRequest:
    """Parse and validate RDS request YAML structure."""
    md = doc.get("metadata", {})
    spec = doc.get("spec", {})

    # Top-level field mapping (support both flat and nested structures)
    rds_id = doc.get("id") or md.get("id")
    service = doc.get("service") or md.get("service") or "postgres"
    environment = doc.get("environment") or md.get("environment")
    owner = doc.get("owner") or md.get("owner")
    requester = doc.get("requester") or md.get("requester")

    # Spec fields (camelCase from contract)
    database_name = spec.get("databaseName")
    username = spec.get("username")
    size = spec.get("size", "small")
    domain = spec.get("domain")
    risk = spec.get("risk", "low")

    # Storage configuration
    storage_gb = spec.get("storageGb", 20)
    max_storage_gb = spec.get("maxStorageGb", 50)

    # Backup and HA configuration
    backup_retention_days = spec.get("backupRetentionDays", 7)
    multi_az = spec.get("multiAz", False)
    performance_insights = spec.get("performanceInsights", True)

    # Required field validation
    missing = [
        k
        for k, v in {
            "id": rds_id,
            "environment": environment,
            "owner": owner,
            "requester": requester,
            "spec.databaseName": database_name,
            "spec.username": username,
            "spec.domain": domain,
        }.items()
        if not v
    ]

    if missing:
        raise ValueError(f"{src_path}: missing required fields: {', '.join(missing)}")

    return RdsRequest(
        rds_id=str(rds_id),
        service=str(service),
        environment=str(environment),
        databaseName=str(database_name),
        username=str(username),
        size=str(size),
        domain=str(domain),
        owner=str(owner),
        requester=str(requester),
        risk=str(risk),
        storageGb=int(storage_gb),
        maxStorageGb=int(max_storage_gb),
        backupRetentionDays=int(backup_retention_days),
        multiAz=bool(multi_az),
        performanceInsights=bool(performance_insights),
    )


def validate_enums(
    req: RdsRequest, enums: Dict[str, List[str]], src_path: Path
) -> None:
    """Validate enum fields against allowed values."""

    def check(field: str, value: str, allowed: List[str]) -> None:
        if value not in allowed:
            raise ValueError(
                f"{src_path}: invalid {field}='{value}'. Allowed: {allowed}"
            )

    check("size", req.size, enums["size"])
    check("environment", req.environment, enums["environment"])
    check("domain", req.domain, enums["domain"])
    check("owner", req.owner, enums["owner"])
    check("risk", req.risk, enums["risk"])

    # Conditional validation rules
    if req.environment == "prod" and not req.multiAz:
        print(
            f"[WARN] {src_path}: Production database without Multi-AZ may have availability gaps"
        )

    if req.environment == "prod" and req.backupRetentionDays < 14:
        raise ValueError(f"{src_path}: Production requires backup_retention_days >= 14")

    if req.environment == "dev" and req.size not in ["small"]:
        raise ValueError(f"{src_path}: Dev environment limited to size='small'")

    if req.maxStorageGb <= req.storageGb:
        raise ValueError(f"{src_path}: maxStorageGb must be greater than storageGb")


def derive_secret_key(req: RdsRequest) -> str:
    """Derive AWS Secrets Manager key for RDS credentials."""
    return f"goldenpath/{req.environment}/{req.databaseName}/postgres"


def tfvars_output_path(tfvars_out_root: Path, req: RdsRequest) -> Path:
    """Generate tfvars output path."""
    return (
        tfvars_out_root
        / f"{req.environment}-rds"
        / "generated"
        / f"{req.rds_id}.auto.tfvars.json"
    )


def externalsecret_output_path(externalsecret_out_root: Path, req: RdsRequest) -> Path:
    """Generate ExternalSecret manifest output path."""
    return (
        externalsecret_out_root
        / "kustomize"
        / "overlays"
        / req.environment
        / "apps"
        / req.databaseName
        / "externalsecrets"
        / f"{req.rds_id}.yaml"
    )


def generate_tfvars(req: RdsRequest) -> Dict[str, Any]:
    """Generate Terraform variables for RDS provisioning."""
    return {
        "rds_databases": {
            req.databaseName: {
                "identifier": f"{req.environment}-{req.databaseName}",
                "database_name": req.databaseName,
                "username": req.username,
                "instance_class": SIZE_TO_INSTANCE.get(req.size, "db.t3.micro"),
                "allocated_storage": req.storageGb,
                "max_allocated_storage": req.maxStorageGb,
                "backup_retention_period": req.backupRetentionDays,
                "multi_az": req.multiAz,
                "performance_insights_enabled": req.performanceInsights,
                "metadata": {
                    "id": req.rds_id,
                    "owner": req.owner,
                    "domain": req.domain,
                    "risk": req.risk,
                    "requester": req.requester,
                },
            }
        }
    }


def generate_externalsecret(req: RdsRequest) -> Dict[str, Any]:
    """Generate ExternalSecret manifest for K8s credential sync."""
    return {
        "apiVersion": "external-secrets.io/v1beta1",
        "kind": "ExternalSecret",
        "metadata": {
            "name": f"{req.databaseName}-credentials-sync",
            "namespace": req.databaseName,
            "labels": {
                "goldenpath.idp/id": req.rds_id,
                "platform.idp/service": req.databaseName,
                "platform.idp/env": req.environment,
                "platform.idp/type": "rds-credentials",
            },
        },
        "spec": {
            "refreshInterval": "1h",
            "secretStoreRef": {
                "name": "aws-secretsmanager",
                "kind": "ClusterSecretStore",
            },
            "target": {
                "name": f"{req.databaseName}-db-credentials",
                "creationPolicy": "Owner",
            },
            "dataFrom": [{"extract": {"key": derive_secret_key(req)}}],
        },
    }


def write_yaml(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, sort_keys=False)


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="RDS Request Parser - Generate Terraform and ExternalSecret artifacts"
    )
    p.add_argument(
        "--mode",
        choices=["validate", "generate"],
        required=True,
        help="validate: check schema; generate: create output files",
    )
    p.add_argument("--enums", required=True, help="Path to schemas/metadata/enums.yaml")
    p.add_argument(
        "--input-files", nargs="+", required=True, help="RDS request YAML files"
    )
    p.add_argument(
        "--tfvars-out-root",
        default="envs",
        help="Root for tfvars outputs (default: envs)",
    )
    p.add_argument(
        "--externalsecret-out-root",
        default="gitops",
        help="Root for ExternalSecret outputs (default: gitops)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without writing files",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    enums_path = Path(args.enums)
    enums = load_enums(enums_path)

    tfvars_root = Path(args.tfvars_out_root)
    externalsecret_root = Path(args.externalsecret_out_root)

    failures: List[str] = []

    for f in args.input_files:
        src = Path(f)
        try:
            doc = load_yaml(src)
            req = parse_request(doc, src)
            validate_enums(req, enums, src)

            if args.mode == "generate":
                tfvars_path = tfvars_output_path(tfvars_root, req)
                es_path = externalsecret_output_path(externalsecret_root, req)

                tfvars_content = generate_tfvars(req)
                es_content = generate_externalsecret(req)

                if args.dry_run:
                    print(f"[DRY-RUN] Would write tfvars to: {tfvars_path}")
                    print(json.dumps(tfvars_content, indent=2))
                    print(f"[DRY-RUN] Would write ExternalSecret to: {es_path}")
                    print(yaml.safe_dump(es_content, sort_keys=False))
                else:
                    write_json(tfvars_path, tfvars_content)
                    write_yaml(es_path, es_content)
                    print(f"[OK] {src} -> {tfvars_path}")
                    print(f"[OK] {src} -> {es_path}")
            else:
                print(f"[OK] {src} validated")

        except Exception as e:
            failures.append(f"{src}: {e}")

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
