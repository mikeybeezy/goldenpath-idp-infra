#!/usr/bin/env python3
"""
Generate a lightweight AWS inventory report using Resource Groups Tagging API.

Note:
- This surfaces tagged (and previously tagged) resources only.
- Resources that have never been tagged may not appear.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "inventory-config.yaml"
ENUMS_PATH = ROOT / "schemas/metadata/enums.yaml"
COST_CENTER_KEYS = ["CostCenter", "cost_center", "cost-center", "Cost-Center"]

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def run_aws(cmd: list[str], env: dict) -> dict:
    result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(result.stdout)

def base_env() -> dict:
    env = os.environ.copy()
    env["AWS_PAGER"] = ""
    return env

def assume_role(role_arn: str, session_name: str, env: dict) -> dict:
    data = run_aws(
        [
            "aws", "sts", "assume-role",
            "--role-arn", role_arn,
            "--role-session-name", session_name,
            "--output", "json",
        ],
        env,
    )
    creds = data["Credentials"]
    assumed = env.copy()
    assumed.update({
        "AWS_ACCESS_KEY_ID": creds["AccessKeyId"],
        "AWS_SECRET_ACCESS_KEY": creds["SecretAccessKey"],
        "AWS_SESSION_TOKEN": creds["SessionToken"],
    })
    return assumed

def get_caller_identity(env: dict) -> dict:
    return run_aws(["aws", "sts", "get-caller-identity", "--output", "json"], env)

def get_all_regions(env: dict) -> list[str]:
    data = run_aws(
        ["aws", "ec2", "describe-regions", "--all-regions", "--output", "json"],
        env,
    )
    return sorted([r["RegionName"] for r in data.get("Regions", [])])

def resolve_regions(regions_cfg: dict, env: dict) -> list[str]:
    include = regions_cfg.get("include", []) or []
    exclude = set(regions_cfg.get("exclude", []) or [])

    if include in [["all"], ["*"]] or "all" in include or "*" in include:
        include = get_all_regions(env)
    elif not include:
        include = get_all_regions(env)

    return [r for r in include if r not in exclude]

def load_owner_enums() -> set[str]:
    enums = load_yaml(ENUMS_PATH)
    return set(enums.get("owners", []) or [])

def is_placeholder(value: str) -> bool:
    return not value or "000000000000" in value or "ACCOUNT_ID" in value

def extract_service(arn: str) -> str:
    # arn:partition:service:region:account-id:resource
    parts = arn.split(":")
    if len(parts) > 2 and parts[0] == "arn":
        return parts[2]
    return "unknown"

def extract_resource_name(arn: str) -> str:
    parts = arn.split(":", 5)
    if len(parts) < 6:
        return arn
    resource = parts[5]
    if "/" in resource:
        return resource.split("/")[-1]
    if ":" in resource:
        return resource.split(":")[-1]
    return resource

def pick_tag_value(tags: dict, keys: list[str]) -> str:
    for key in keys:
        value = tags.get(key)
        if value:
            return value
    return ""

def build_resource_entries(mappings: list[dict], account_id: str, region: str) -> list[dict]:
    entries = []
    for item in mappings:
        tags = {t["Key"]: t.get("Value", "") for t in item.get("Tags", [])}
        arn = item.get("ResourceARN", "")
        service = extract_service(arn)
        entries.append({
            "account_id": account_id,
            "region": region,
            "service": service,
            "resource_arn": arn,
            "resource_name": extract_resource_name(arn),
            "tag_hints": {
                "owner": tags.get("Owner") or tags.get("owner"),
                "environment": tags.get("Environment") or tags.get("environment"),
                "project": tags.get("Project") or tags.get("project"),
                "cost_center": pick_tag_value(tags, COST_CENTER_KEYS),
            },
            "tags": tags,
        })
    return entries

def extract_ecr_repository_name(arn: str) -> str:
    parts = arn.split(":", 5)
    if len(parts) < 6:
        return arn
    resource = parts[5]
    if "repository/" in resource:
        return resource.split("repository/")[-1]
    return extract_resource_name(arn)

def build_ecr_subset(entries: list[dict]) -> list[dict]:
    subset = []
    for entry in entries:
        if entry.get("service") != "ecr":
            continue
        subset.append({
            "account_id": entry.get("account_id", ""),
            "region": entry.get("region", ""),
            "repository_name": extract_ecr_repository_name(entry.get("resource_arn", "")),
            "resource_arn": entry.get("resource_arn", ""),
            "tag_hints": entry.get("tag_hints", {}),
            "tags": entry.get("tags", {}),
        })
    return subset

def redact_account_id(account_id: str) -> str:
    if not account_id:
        return account_id
    return "REDACTED"

def redact_arn(arn: str) -> str:
    parts = arn.split(":")
    if len(parts) >= 6 and parts[0] == "arn":
        parts[4] = "REDACTED"
        return ":".join(parts)
    return arn

def redact_report(report: dict, redact_accounts: bool) -> dict:
    redacted = json.loads(json.dumps(report))

    scope = redacted.get("scope", {})
    if redact_accounts and "accounts" in scope:
        scope["accounts"] = [redact_account_id(a) for a in scope.get("accounts", [])]

    for entry in redacted.get("by_account", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))

    for entry in redacted.get("missing_tags", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))
        if "resource_arn" in entry:
            entry["resource_arn"] = redact_arn(entry.get("resource_arn", ""))

    for entry in redacted.get("tag_violations", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))
        if "resource_arn" in entry:
            entry["resource_arn"] = redact_arn(entry.get("resource_arn", ""))

    for entry in redacted.get("errors", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))

    for entry in redacted.get("resource_list", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))
        if "resource_arn" in entry:
            entry["resource_arn"] = redact_arn(entry.get("resource_arn", ""))

    ecr_subset = redacted.get("ecr_subset", {})
    for entry in ecr_subset.get("repositories", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))
        if "resource_arn" in entry:
            entry["resource_arn"] = redact_arn(entry.get("resource_arn", ""))

    for entry in redacted.get("repositories", []):
        if redact_accounts:
            entry["account_id"] = redact_account_id(entry.get("account_id", ""))
        if "resource_arn" in entry:
            entry["resource_arn"] = redact_arn(entry.get("resource_arn", ""))

    return redacted

def get_tag_mappings(region: str, env: dict, max_items: int | None) -> list[dict]:
    mappings = []
    token = None

    while True:
        cmd = [
            "aws", "resourcegroupstaggingapi", "get-resources",
            "--region", region,
            "--output", "json",
            "--page-size", "100",
        ]
        if token:
            cmd.extend(["--starting-token", token])
        if max_items:
            cmd.extend(["--max-items", str(max_items)])

        data = run_aws(cmd, env)
        mappings.extend(data.get("ResourceTagMappingList", []))
        token = data.get("PaginationToken")
        if not token:
            break
    return mappings

def analyze_tags(
    mappings: list[dict],
    required_keys: set[str],
    env_values: set[str],
    project_values: set[str],
    owner_values: set[str],
    detail_limit: int,
    account_id: str,
    region: str,
) -> dict:
    tagged = 0
    untagged = 0
    missing_count = 0
    violation_count = 0
    missing_details = []
    violation_details = []

    for item in mappings:
        tags = {t["Key"]: t.get("Value", "") for t in item.get("Tags", [])}
        arn = item.get("ResourceARN", "")
        service = extract_service(arn)

        if not tags:
            untagged += 1
        else:
            tagged += 1

        missing = [k for k in required_keys if not tags.get(k)]
        if missing:
            missing_count += 1
            violation_count += 1
            if len(missing_details) < detail_limit:
                missing_details.append({
                    "account_id": account_id,
                    "region": region,
                    "service": service,
                    "resource_arn": arn,
                    "missing_keys": missing,
                })

        # Value validations
        if env_values and "Environment" in tags and tags["Environment"] not in env_values:
            violation_count += 1
            if len(violation_details) < detail_limit:
                violation_details.append({
                    "account_id": account_id,
                    "region": region,
                    "service": service,
                    "resource_arn": arn,
                    "key": "Environment",
                    "value": tags["Environment"],
                    "allowed": sorted(env_values),
                })

        if project_values and "Project" in tags and tags["Project"] not in project_values:
            violation_count += 1
            if len(violation_details) < detail_limit:
                violation_details.append({
                    "account_id": account_id,
                    "region": region,
                    "service": service,
                    "resource_arn": arn,
                    "key": "Project",
                    "value": tags["Project"],
                    "allowed": sorted(project_values),
                })

        if owner_values and "Owner" in tags and tags["Owner"] not in owner_values:
            violation_count += 1
            if len(violation_details) < detail_limit:
                violation_details.append({
                    "account_id": account_id,
                    "region": region,
                    "service": service,
                    "resource_arn": arn,
                    "key": "Owner",
                    "value": tags["Owner"],
                    "allowed": sorted(owner_values),
                })

    return {
        "tagged": tagged,
        "untagged": untagged,
        "missing_count": missing_count,
        "violation_count": violation_count,
        "missing_details": missing_details,
        "violation_details": violation_details,
    }

def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)

def write_md(path: Path, data: dict) -> None:
    lines = [
        f"# AWS Inventory Report ({data['run_id']})",
        "",
        "## Summary",
        f"- Total resources: {data['summary']['total_resources']}",
        f"- Tagged: {data['summary']['tagged']}",
        f"- Untagged: {data['summary']['untagged']}",
        f"- Tag violations: {data['summary']['tag_violations']}",
        "",
        "## Notes",
        "- Tagging API only returns resources that are tagged or were previously tagged.",
        "- Resources that have never been tagged may not appear.",
        "",
        "## Missing Tags (sample)",
    ]
    missing = data.get("missing_tags", [])[:10]
    if not missing:
        lines.append("- None")
    else:
        for item in missing:
            lines.append(
                f"- {item['account_id']} / {item['region']} / {item['service']} "
                f"/ {item['resource_arn']} — missing: {', '.join(item['missing_keys'])}"
            )

    lines.append("")
    lines.append("## Tag Violations (sample)")
    violations = data.get("tag_violations", [])[:10]
    if not violations:
        lines.append("- None")
    else:
        for item in violations:
            allowed = ", ".join(item["allowed"]) if item.get("allowed") else ""
            lines.append(
                f"- {item['account_id']} / {item['region']} / {item['service']} "
                f"/ {item['resource_arn']} — {item['key']}={item['value']} "
                f"(allowed: {allowed})"
            )

    lines.append("")
    lines.append("## Resource List")
    resources = data.get("resource_list", [])
    if not resources:
        lines.append("- None")
    else:
        lines.append("| Account | Region | Service | Resource | Owner | Environment | Project | Cost Center | ARN |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for entry in resources:
            hints = entry.get("tag_hints", {})
            lines.append(
                "| {account} | {region} | {service} | {name} | {owner} | {env} | {project} | {cost_center} | {arn} |".format(
                    account=entry.get("account_id", ""),
                    region=entry.get("region", ""),
                    service=entry.get("service", ""),
                    name=entry.get("resource_name", ""),
                    owner=hints.get("owner", "") or "",
                    env=hints.get("environment", "") or "",
                    project=hints.get("project", "") or "",
                    cost_center=hints.get("cost_center", "") or "",
                    arn=entry.get("resource_arn", ""),
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_ecr_md(path: Path, data: dict) -> None:
    lines = [
        f"# AWS ECR Inventory ({data['run_id']})",
        "",
        "## Summary",
        f"- Total repositories: {data['summary']['total_repositories']}",
        "",
        "## Repositories",
    ]
    repos = data.get("repositories", [])
    if not repos:
        lines.append("- None")
    else:
        lines.append("| Account | Region | Repository | Owner | Environment | Project | Cost Center | ARN |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for entry in repos:
            hints = entry.get("tag_hints", {})
            lines.append(
                "| {account} | {region} | {repo} | {owner} | {env} | {project} | {cost_center} | {arn} |".format(
                    account=entry.get("account_id", ""),
                    region=entry.get("region", ""),
                    repo=entry.get("repository_name", ""),
                    owner=hints.get("owner", "") or "",
                    env=hints.get("environment", "") or "",
                    project=hints.get("project", "") or "",
                    cost_center=hints.get("cost_center", "") or "",
                    arn=entry.get("resource_arn", ""),
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_sidecar(path: Path, report_id: str, run_date: str) -> None:
    sidecar = {
        "id": report_id,
        "title": f"AWS Inventory Report ({run_date})",
        "type": "report",
        "domain": "governance",
        "owner": "platform-team",
        "lifecycle": "active",
        "status": "released",
        "date": run_date,
        "risk_profile": {
            "production_impact": "low",
            "security_risk": "low",
            "coupling_risk": "low",
        },
        "reliability": {
            "rollback_strategy": "git-revert",
            "observability_tier": "bronze",
        },
        "relates_to": ["INVENTORY_CONFIG", str(path)],
        "tags": ["inventory", "report", "aws"],
    }

    sidecar_path = path.with_suffix(path.suffix + ".metadata.yaml")
    with sidecar_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(sidecar, f, sort_keys=False)

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate AWS inventory reports.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to inventory config.")
    parser.add_argument("--date", default=None, help="Report date (YYYY-MM-DD).")
    parser.add_argument("--output-dir", default=None, help="Override output directory.")
    parser.add_argument("--max-detail", type=int, default=200, help="Max detailed rows per list.")
    parser.add_argument("--no-assume-role", action="store_true", help="Ignore role_arn in config.")
    parser.add_argument("--no-sidecar", action="store_true", help="Do not write report sidecar.")
    args = parser.parse_args()

    config = load_yaml(Path(args.config))
    accounts = config.get("accounts", []) or []
    tag_policy = config.get("tag_policy", {}) or {}
    reporting = config.get("reporting", {}) or {}

    required_keys = set(tag_policy.get("required_keys", []) or [])
    env_values = set(tag_policy.get("env_values", []) or [])
    project_values = set(tag_policy.get("goldenpath_project_values", []) or [])
    owner_values = set(tag_policy.get("owner_values", []) or [])
    if not owner_values:
        owner_values = load_owner_enums()

    output_dir = Path(args.output_dir or reporting.get("output_dir") or "reports/aws-inventory")
    full_output_dir = Path(reporting.get("full_output_dir") or "")
    formats = reporting.get("formats", ["json", "md"])
    include_resource_list = reporting.get("include_resource_list", False)
    include_ecr_subset = reporting.get("include_ecr_subset", False)
    redact_account_ids = reporting.get("redact_account_ids", False)
    run_date = args.date or datetime.date.today().isoformat()
    report_base = f"aws-inventory-{run_date}"
    ecr_report_base = f"aws-inventory-ecr-{run_date}"

    env = base_env()
    if not accounts:
        accounts = [{"id": "", "name": "default", "regions": {"include": ["all"], "exclude": []}}]

    summary = {
        "total_resources": 0,
        "tagged": 0,
        "untagged": 0,
        "tag_violations": 0,
    }
    by_account = []
    missing_tags = []
    tag_violations = []
    errors = []
    resource_list = []
    ecr_resources = []

    for account in accounts:
        account_id = account.get("id", "")
        role_arn = account.get("role_arn", "")
        name = account.get("name", "")

        account_env = env
        if role_arn and not args.no_assume_role and not is_placeholder(role_arn):
            try:
                account_env = assume_role(role_arn, "goldenpath-inventory", env)
            except subprocess.CalledProcessError as e:
                errors.append({
                    "account_id": account_id,
                    "error": f"assume-role failed: {e.stderr.strip()}",
                })
                continue

        if is_placeholder(account_id):
            try:
                ident = get_caller_identity(account_env)
                account_id = ident.get("Account", account_id)
            except subprocess.CalledProcessError as e:
                errors.append({
                    "account_id": account_id or "unknown",
                    "error": f"get-caller-identity failed: {e.stderr.strip()}",
                })
                continue

        regions_cfg = account.get("regions", {}) or {}
        try:
            regions = resolve_regions(regions_cfg, account_env)
        except subprocess.CalledProcessError as e:
            errors.append({
                "account_id": account_id,
                "error": f"region discovery failed: {e.stderr.strip()}",
            })
            continue

        account_totals = {
            "account_id": account_id,
            "name": name,
            "regions_scanned": regions,
            "resources": 0,
            "tagged": 0,
            "untagged": 0,
            "tag_violations": 0,
        }

        for region in regions:
            try:
                mappings = get_tag_mappings(region, account_env, None)
            except subprocess.CalledProcessError as e:
                errors.append({
                    "account_id": account_id,
                    "region": region,
                    "error": f"tagging API failed: {e.stderr.strip()}",
                })
                continue

            analysis = analyze_tags(
                mappings,
                required_keys,
                env_values,
                project_values,
                owner_values,
                args.max_detail,
                account_id,
                region,
            )

            account_totals["resources"] += len(mappings)
            account_totals["tagged"] += analysis["tagged"]
            account_totals["untagged"] += analysis["untagged"]
            account_totals["tag_violations"] += analysis["violation_count"]

            summary["total_resources"] += len(mappings)
            summary["tagged"] += analysis["tagged"]
            summary["untagged"] += analysis["untagged"]
            summary["tag_violations"] += analysis["violation_count"]

            missing_tags.extend(analysis["missing_details"])
            tag_violations.extend(analysis["violation_details"])

            if include_resource_list or include_ecr_subset:
                entries = build_resource_entries(mappings, account_id, region)
                if include_resource_list:
                    resource_list.extend(entries)
                if include_ecr_subset:
                    ecr_resources.extend(build_ecr_subset(entries))

        by_account.append(account_totals)

    report = {
        "run_id": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "scope": {
            "accounts": [a["account_id"] for a in by_account],
            "regions": sorted({r for a in by_account for r in a.get("regions_scanned", [])}),
            "iam_included": False,
        },
        "summary": summary,
        "by_account": by_account,
        "missing_tags": missing_tags,
        "tag_violations": tag_violations,
        "errors": errors,
        "note": "Tagging API only returns resources that are tagged or were previously tagged.",
    }

    if include_resource_list:
        report["resource_list"] = resource_list
    if include_ecr_subset:
        report["ecr_subset"] = {
            "total_repositories": len(ecr_resources),
            "repositories": ecr_resources,
        }

    public_report = redact_report(report, redact_account_ids)

    if "json" in formats:
        write_json(output_dir / f"{report_base}.json", public_report)
    if "md" in formats:
        write_md(output_dir / f"{report_base}.md", public_report)
    if include_ecr_subset:
        ecr_report = {
            "run_id": report["run_id"],
            "scope": report["scope"],
            "summary": {"total_repositories": len(ecr_resources)},
            "repositories": ecr_resources,
            "note": "Subset of AWS inventory for ECR repositories only.",
        }
        ecr_public = redact_report(ecr_report, redact_account_ids)
        if "json" in formats:
            write_json(output_dir / f"{ecr_report_base}.json", ecr_public)
        if "md" in formats:
            write_ecr_md(output_dir / f"{ecr_report_base}.md", ecr_public)

    if full_output_dir:
        if "json" in formats:
            write_json(full_output_dir / f"{report_base}.json", report)
        if "md" in formats:
            write_md(full_output_dir / f"{report_base}.md", report)
        if include_ecr_subset:
            ecr_report = {
                "run_id": report["run_id"],
                "scope": report["scope"],
                "summary": {"total_repositories": len(ecr_resources)},
                "repositories": ecr_resources,
                "note": "Subset of AWS inventory for ECR repositories only.",
            }
            if "json" in formats:
                write_json(full_output_dir / f"{ecr_report_base}.json", ecr_report)
            if "md" in formats:
                write_ecr_md(full_output_dir / f"{ecr_report_base}.md", ecr_report)

    if not args.no_sidecar:
        report_id = f"AWS_INVENTORY_REPORT_{run_date.replace('-', '_')}"
        write_sidecar(output_dir / f"{report_base}.json", report_id, run_date)

    print(f"✅ Inventory report generated: {output_dir}/{report_base}.*")
    return 0

if __name__ == "__main__":
    sys.exit(main())
