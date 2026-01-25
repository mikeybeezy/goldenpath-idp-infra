# AGENT_CONTEXT: Read .agent/README.md for rules
#!/usr/bin/env python3
"""
---
id: SCRIPT-0043
type: script
owner: platform-team
status: active
maturity: 1
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0043.py
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
EKS Request parser/generator (Adapted Standard).

Maps:
  docs/20-contracts/eks-requests/<env>/<eks-id>.yaml
to:
  envs/<env>/clusters/generated/<eks-id>.auto.tfvars.json

Modes:
  validate  - schema-ish validation + enum enforcement
  generate  - writes tfvars output file
"""

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


NODE_TIER_TO_INSTANCE = {
    "small": "t3.small",
    "medium": "t3.medium",
    "large": "t3.large",
    "xlarge": "t3.xlarge",
}


@dataclass(frozen=True)
class EksRequest:
    eks_id: str
    environment: str
    region: str
    owner: str
    requester: str
    created_date: Optional[str]
    cluster_lifecycle: str
    mode: str
    build_id: str

    cluster_name: str
    kubernetes_version: str
    private_endpoint_only: bool

    node_tier: str
    instance_type: str
    node_min: int
    node_desired: int
    node_max: int
    capacity_type: str
    autoscaler_enabled: bool

    gitops_controller: str
    gitops_install: bool
    bootstrap_profile: str

    ingress_provider: str
    aws_lb_type: str
    ingress_internal: bool

    ssm_break_glass: bool
    ssh_break_glass: bool
    ssh_key_name: Optional[str]
    ssh_source_sg_ids: List[str]

    irsa_enabled: bool


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_enums(enums_path: Path) -> Dict[str, List[str]]:
    data = load_yaml(enums_path)
    return {
        "environment": data.get("eks_environments", []),
        "mode": data.get("eks_modes", []),
        "node_tier": data.get("eks_node_tiers", []),
        "kubernetes_version": data.get("kubernetes_versions", []),
        "capacity_type": data.get("eks_capacity_types", []),
        "gitops_controller": data.get("eks_gitops_controllers", []),
        "bootstrap_profile": data.get("eks_bootstrap_profiles", []),
        "ingress_provider": data.get("eks_ingress_providers", []),
        "aws_lb_type": data.get("eks_aws_lb_types", []),
        "owner": data.get("owners", []),
    }


def parse_request(doc: Dict[str, Any], src_path: Path) -> EksRequest:
    md = doc.get("metadata", {})
    spec = doc.get("spec", {})

    eks_id = doc.get("id") or md.get("id")
    environment = doc.get("environment") or md.get("environment")
    region = doc.get("region") or md.get("region")
    owner = doc.get("owner") or md.get("owner")
    requester = doc.get("requester") or md.get("requester")
    created_date = md.get("created") or md.get("created_date") or md.get("createdDate")
    cluster_lifecycle = doc.get("clusterLifecycle") or doc.get("cluster_lifecycle") or md.get("clusterLifecycle") or md.get("cluster_lifecycle") or ""

    mode = spec.get("mode")
    build = spec.get("build", {})
    build_id = build.get("buildId") or build.get("build_id", "")

    cluster = spec.get("cluster", {})
    cluster_name = cluster.get("clusterName") or cluster.get("name")
    kubernetes_version = cluster.get("kubernetesVersion") or cluster.get("kubernetes_version")
    private_endpoint_only = cluster.get("privateEndpointOnly")
    if private_endpoint_only is None:
        private_endpoint_only = cluster.get("private_endpoint_only", True)
    irsa = cluster.get("irsa", {})
    irsa_enabled = bool(irsa.get("enabled", False))

    access = cluster.get("access", {})
    ssm_break_glass = bool(access.get("ssmBreakGlass", access.get("ssm_break_glass", True)))
    ssh_break_glass = bool(access.get("sshBreakGlass", access.get("ssh_break_glass", False)))
    ssh_key_name = access.get("sshKeyName") or access.get("ssh_key_name")
    ssh_source_sg_ids = access.get("sshSourceSgIds") or access.get("ssh_source_sg_ids") or access.get("ssh_source_security_group_ids") or []

    node_pool = spec.get("nodePool") or spec.get("node_pool") or {}
    node_tier = node_pool.get("nodeTier") or node_pool.get("node_tier") or node_pool.get("tier") or ""
    instance_type = node_pool.get("instanceType") or node_pool.get("instance_type") or ""
    node_min = node_pool.get("nodeMin") or node_pool.get("min") or node_pool.get("min_size")
    node_desired = node_pool.get("nodeDesired") or node_pool.get("desired") or node_pool.get("desired_size")
    node_max = node_pool.get("nodeMax") or node_pool.get("max") or node_pool.get("max_size")
    capacity_type = node_pool.get("capacityType") or node_pool.get("capacity_type") or "ON_DEMAND"
    autoscaler = node_pool.get("autoscaler", {})
    autoscaler_enabled = bool(autoscaler.get("enabled", True))

    gitops = spec.get("gitops", {})
    gitops_controller = gitops.get("controller", "argocd")
    gitops_install = bool(gitops.get("install", True))
    bootstrap_profile = gitops.get("bootstrapProfile") or gitops.get("bootstrap_profile") or "core-tooling"

    ingress = spec.get("ingress", {})
    ingress_provider = ingress.get("provider", "kong")
    aws_lb_type = ingress.get("awsLbType") or ingress.get("aws_lb_type") or "nlb"
    ingress_internal = bool(ingress.get("internal", True))

    missing = [k for k, v in {
        "id": eks_id,
        "environment": environment,
        "region": region,
        "owner": owner,
        "requester": requester,
        "spec.mode": mode,
        "spec.cluster.clusterName": cluster_name,
        "spec.cluster.kubernetesVersion": kubernetes_version,
        "spec.nodePool.nodeDesired": node_desired,
        "spec.nodePool.nodeMax": node_max,
    }.items() if not v]

    if mode in ["cluster-only", "cluster+bootstrap"] and not build_id:
        missing.append("spec.build.buildId")

    if not instance_type and not node_tier:
        missing.append("spec.nodePool.nodeTier or spec.nodePool.instanceType")

    if missing:
        raise ValueError(f"{src_path}: missing required fields: {', '.join(missing)}")

    node_min_val = int(node_min) if node_min is not None else int(node_desired)
    node_desired_val = int(node_desired)
    node_max_val = int(node_max)

    if node_min_val > node_desired_val or node_desired_val > node_max_val:
        raise ValueError(
            f"{src_path}: nodePool sizing must satisfy min <= desired <= max"
        )

    resolved_instance_type = instance_type or NODE_TIER_TO_INSTANCE.get(node_tier, "")
    if not resolved_instance_type:
        raise ValueError(f"{src_path}: unsupported nodeTier '{node_tier}'")

    return EksRequest(
        eks_id=str(eks_id),
        environment=str(environment),
        region=str(region),
        owner=str(owner),
        requester=str(requester),
        created_date=str(created_date) if created_date else None,
        cluster_lifecycle=str(cluster_lifecycle),
        mode=str(mode),
        build_id=str(build_id),
        cluster_name=str(cluster_name),
        kubernetes_version=str(kubernetes_version),
        private_endpoint_only=bool(private_endpoint_only),
        node_tier=str(node_tier),
        instance_type=str(resolved_instance_type),
        node_min=node_min_val,
        node_desired=node_desired_val,
        node_max=node_max_val,
        capacity_type=str(capacity_type),
        autoscaler_enabled=bool(autoscaler_enabled),
        gitops_controller=str(gitops_controller),
        gitops_install=bool(gitops_install),
        bootstrap_profile=str(bootstrap_profile),
        ingress_provider=str(ingress_provider),
        aws_lb_type=str(aws_lb_type),
        ingress_internal=bool(ingress_internal),
        ssm_break_glass=bool(ssm_break_glass),
        ssh_break_glass=bool(ssh_break_glass),
        ssh_key_name=str(ssh_key_name) if ssh_key_name else None,
        ssh_source_sg_ids=[str(x) for x in ssh_source_sg_ids],
        irsa_enabled=bool(irsa_enabled),
    )


def validate_enums(req: EksRequest, enums: Dict[str, List[str]], src_path: Path) -> None:
    def check(field: str, value: str, allowed: List[str]) -> None:
        if value in ("", None):
            return
        if allowed and value not in allowed:
            raise ValueError(
                f"{src_path}: invalid {field}='{value}'. Allowed: {allowed}"
            )

    check("environment", req.environment, enums["environment"])
    check("mode", req.mode, enums["mode"])
    check("nodeTier", req.node_tier, enums["node_tier"])
    check("kubernetes_version", req.kubernetes_version, enums["kubernetes_version"])
    check("capacityType", req.capacity_type, enums["capacity_type"])
    check("gitopsController", req.gitops_controller, enums["gitops_controller"])
    check("bootstrapProfile", req.bootstrap_profile, enums["bootstrap_profile"])
    check("ingressProvider", req.ingress_provider, enums["ingress_provider"])
    check("awsLbType", req.aws_lb_type, enums["aws_lb_type"])
    check("owner", req.owner, enums["owner"])


def tfvars_output_path(tfvars_out_root: Path, req: EksRequest) -> Path:
    return (
        tfvars_out_root
        / req.environment
        / "clusters"
        / "generated"
        / f"{req.eks_id}.auto.tfvars.json"
    )


def read_catalog(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "version": "1.0",
            "domain": "platform-core",
            "owner": "platform-team",
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "managed_by": "platform-team",
            "clusters": {},
        }
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_catalog(path: Path, data: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] Would write catalog: {path}")
        print(yaml.safe_dump(data, sort_keys=False))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def derive_risk(environment: str) -> str:
    if environment == "prod":
        return "high"
    if environment == "staging":
        return "medium"
    return "low"


def update_eks_catalog(req: EksRequest, catalog_path: Path, status: str, dry_run: bool) -> None:
    catalog = read_catalog(catalog_path)
    catalog.setdefault("clusters", {})
    catalog["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    created_date = req.created_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    catalog["clusters"][req.cluster_name] = {
        "metadata": {
            "id": req.eks_id,
            "owner": req.owner,
            "requested_by": req.requester,
            "domain": "platform-core",
            "risk": derive_risk(req.environment),
            "environment": req.environment,
            "status": status,
            "created_date": created_date,
        },
        "aws": {
            "cluster_name": req.cluster_name,
            "region": req.region,
            "version": req.kubernetes_version,
        },
        "configuration": {
            "mode": req.mode,
            "node_tier": req.node_tier,
            "node_min": req.node_min,
            "node_desired": req.node_desired,
            "node_max": req.node_max,
            "capacity_type": req.capacity_type.lower(),
            "build_id": req.build_id,
        },
    }

    write_catalog(catalog_path, catalog, dry_run)


def generate_audit_record(req: EksRequest, action: str, status: str, approver: str) -> Dict[str, Any]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "request_id": req.eks_id,
        "cluster_name": req.cluster_name,
        "owner": req.owner,
        "environment": req.environment,
        "mode": req.mode,
        "build_id": req.build_id,
        "action": action,
        "approver": approver,
        "status": status,
    }


def append_audit_record(path: Path, record: Dict[str, Any], dry_run: bool) -> None:
    header = [
        "timestamp_utc",
        "request_id",
        "cluster_name",
        "owner",
        "environment",
        "mode",
        "build_id",
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


def generate_tfvars(req: EksRequest) -> Dict[str, Any]:
    cluster_lifecycle = "ephemeral" if req.build_id else "persistent"
    includes_bootstrap = req.mode in ["bootstrap-only", "cluster+bootstrap"]
    apply_addons = includes_bootstrap and req.gitops_install
    node_group = {
        "name": f"{req.environment}-default",
        "min_size": req.node_min,
        "max_size": req.node_max,
        "desired_size": req.node_desired,
        "instance_types": [req.instance_type],
        "disk_size": 20,
        "capacity_type": req.capacity_type,
        "update_config": {"max_unavailable": 1},
    }

    return {
        "cluster_lifecycle": cluster_lifecycle,
        "build_id": req.build_id,
        "eks_config": {
            "enabled": True,
            "cluster_name": req.cluster_name,
            "version": req.kubernetes_version,
            "enable_ssh_break_glass": req.ssh_break_glass,
            "ssh_key_name": req.ssh_key_name,
            "ssh_source_security_group_ids": req.ssh_source_sg_ids,
            "node_group": node_group,
        },
        "enable_k8s_resources": includes_bootstrap,
        "apply_kubernetes_addons": apply_addons,
    }


def validate_request(req: EksRequest, enums: Dict[str, List[str]], src_path: Path) -> None:
    validate_enums(req, enums, src_path)
    if req.cluster_lifecycle and req.cluster_lifecycle != "ephemeral":
        raise ValueError(f"{src_path}: clusterLifecycle must be ephemeral for now")
    if req.bootstrap_profile != "core-tooling":
        print(f"[WARN] {src_path}: bootstrapProfile is not wired to automation yet")
    if req.ingress_provider != "kong" or req.aws_lb_type != "nlb":
        print(f"[WARN] {src_path}: ingress settings are not wired to automation yet")
    if req.irsa_enabled:
        print(f"[WARN] {src_path}: irsaEnabled is not wired to automation yet")


def load_requests(input_files: List[str]) -> List[Path]:
    return [Path(p) for p in input_files]


def write_json(path: Path, data: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="EKS Request Parser")
    parser.add_argument("--mode", choices=["validate", "generate"], required=True)
    parser.add_argument("--input-files", nargs="+", required=True)
    parser.add_argument("--enums", required=True)
    parser.add_argument("--tfvars-out-root", default="envs")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--catalog-path", default="")
    parser.add_argument("--catalog-status", default="active")
    parser.add_argument("--audit-path", default="")
    parser.add_argument("--audit-action", default="apply")
    parser.add_argument("--audit-status", default="success")
    parser.add_argument("--audit-approver", default="")
    args = parser.parse_args()

    enums = load_enums(Path(args.enums))
    inputs = load_requests(args.input_files)

    for path in inputs:
        doc = load_yaml(path)
        req = parse_request(doc, path)
        validate_request(req, enums, path)

        if args.mode == "generate":
            if req.mode == "bootstrap-only":
                raise ValueError(
                    f"{path}: mode bootstrap-only does not generate tfvars; use bootstrap workflow"
                )
            tfvars = generate_tfvars(req)
            out_path = tfvars_output_path(Path(args.tfvars_out_root), req)
            write_json(out_path, tfvars, args.dry_run)
            print(f"[OK] {path} -> {out_path}")

            if args.catalog_path:
                update_eks_catalog(req, Path(args.catalog_path), args.catalog_status, args.dry_run)

            if args.audit_path:
                approver = args.audit_approver or os.environ.get("GITHUB_ACTOR", "unknown")
                record = generate_audit_record(req, args.audit_action, args.audit_status, approver)
                append_audit_record(Path(args.audit_path), record, args.dry_run)
        else:
            print(f"[OK] {path} validated")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
