#!/usr/bin/env python3
"""
SecretRequest parser/generator (Adapted Standard).

Maps:
  docs/catalogs/secrets/<service>/<env>/<secret-id>.yaml
to:
  envs/<env>/secrets/generated/<service>/<secret-id>.auto.tfvars.json
and:
  gitops/kustomize/overlays/<env>/apps/<service>/externalsecrets/<secret-id>.yaml

Modes:
  validate  - schema-ish validation + enum enforcement
  generate  - writes tfvars + ExternalSecret output files
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


@dataclass(frozen=True)
class SecretRequest:
    secret_id: str
    name: str
    service: str
    environment: str
    owner: str

    secret_type: str
    risk_tier: str
    rotation_class: str
    lifecycle_status: str

    namespace: str
    k8s_secret_name: str

    provider: str = "aws-secrets-manager"


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_enums(enums_path: Path) -> Dict[str, List[str]]:
    data = load_yaml(enums_path)
    # Existing structure: security: { secret_types: {values: [...]}, ... }
    security = data.get("security", {})
    def values(key: str) -> List[str]:
        node = security.get(key, {})
        return list(node.get("values", []))
    return {
        "secret_type": values("secret_types"),
        "risk_tier": values("risk_tiers"),
        "rotation_class": values("rotation_classes"),
        "lifecycle_status": values("lifecycle_status"),
    }


def parse_request(doc: Dict[str, Any], src_path: Path) -> SecretRequest:
    md = doc.get("metadata", {})
    spec = doc.get("spec", {})

    # Top-level field mapping (snake_case)
    secret_id = doc.get("id") or md.get("id")
    name = doc.get("name") or md.get("name")
    service = doc.get("service") or md.get("service")
    environment = doc.get("environment") or md.get("environment")
    owner = doc.get("owner") or md.get("owner")

    provider = spec.get("provider", "aws-secrets-manager")

    secret_type = spec.get("secret_type")
    
    # Nested mapping for risk/rotation/lifecycle
    risk_tier = ((spec.get("risk") or {}).get("tier"))
    rotation_class = ((spec.get("rotation") or {}).get("rotation_class"))
    lifecycle_status = ((spec.get("lifecycle") or {}).get("status"))

    access = spec.get("access") or {}
    namespace = access.get("namespace")
    k8s_secret_name = access.get("k8s_secret_name")

    missing = [k for k, v in {
        "id": secret_id,
        "name": name,
        "service": service,
        "environment": environment,
        "owner": owner,
        "spec.provider": provider,
        "spec.secret_type": secret_type,
        "spec.risk.tier": risk_tier,
        "spec.rotation.rotation_class": rotation_class,
        "spec.lifecycle.status": lifecycle_status,
        "spec.access.namespace": namespace,
        "spec.access.k8s_secret_name": k8s_secret_name,
    }.items() if not v]

    if missing:
        raise ValueError(f"{src_path}: missing required fields: {', '.join(missing)}")

    return SecretRequest(
        secret_id=str(secret_id),
        name=str(name),
        service=str(service),
        environment=str(environment),
        owner=str(owner),
        provider=str(provider),
        secret_type=str(secret_type),
        risk_tier=str(risk_tier),
        rotation_class=str(rotation_class),
        lifecycle_status=str(lifecycle_status),
        namespace=str(namespace),
        k8s_secret_name=str(k8s_secret_name),
    )


def validate_enums(req: SecretRequest, enums: Dict[str, List[str]], src_path: Path) -> None:
    def check(field: str, value: str, allowed: List[str]) -> None:
        if value not in allowed:
            raise ValueError(
                f"{src_path}: invalid {field}='{value}'. Allowed: {allowed}"
            )

    check("spec.secret_type", req.secret_type, enums["secret_type"])
    check("spec.risk.tier", req.risk_tier, enums["risk_tier"])
    check("spec.rotation.rotation_class", req.rotation_class, enums["rotation_class"])
    check("spec.lifecycle.status", req.lifecycle_status, enums["lifecycle_status"])

    # Minimal V1 policy gates
    if req.risk_tier == "high" and req.rotation_class == "none":
        raise ValueError(f"{src_path}: risk_tier=high requires rotation_class != 'none'")


def derive_secret_key(req: SecretRequest) -> str:
    # deterministic key in AWS Secrets Manager: goldenpath/<env>/<service>/<name>
    return f"goldenpath/{req.environment}/{req.service}/{req.name}"


def tfvars_output_path(tfvars_out_root: Path, req: SecretRequest) -> Path:
    # Writes into envs/<env>/secrets/generated/<service>/<id>.auto.tfvars.json
    return tfvars_out_root / req.environment / "secrets" / "generated" / req.service / f"{req.secret_id}.auto.tfvars.json"


def externalsecret_output_path(externalsecret_out_root: Path, req: SecretRequest) -> Path:
    # Writes into gitops/kustomize/overlays/<env>/apps/<service>/externalsecrets/<id>.yaml
    return (
        externalsecret_out_root
        / "kustomize"
        / "overlays"
        / req.environment
        / "apps"
        / req.service
        / "externalsecrets"
        / f"{req.secret_id}.yaml"
    )


def generate_tfvars(req: SecretRequest) -> Dict[str, Any]:
    # Match Terraform module inputs
    return {
        "app_secrets": {
            f"{req.service}-{req.name}": {
                "description": f"Managed secret for {req.service} in {req.environment}",
                "metadata": {
                    "id": req.secret_id,
                    "owner": req.owner,
                    "risk": req.risk_tier,
                }
            }
        }
    }


def generate_externalsecret(req: SecretRequest) -> Dict[str, Any]:
    return {
        "apiVersion": "external-secrets.io/v1beta1",
        "kind": "ExternalSecret",
        "metadata": {
            "name": f"{req.service}-{req.name}-sync",
            "namespace": req.namespace,
            "labels": {
                "goldenpath.idp/id": req.secret_id,
                "platform.idp/service": req.service,
                "platform.idp/env": req.environment,
            },
        },
        "spec": {
            "refreshInterval": "1h",
            "secretStoreRef": {
                "name": "aws-secretsmanager",
                "kind": "ClusterSecretStore",
            },
            "target": {
                "name": req.k8s_secret_name,
                "creationPolicy": "Owner",
            },
            "dataFrom": [
                {"extract": {"key": derive_secret_key(req)}}
            ],
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
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["validate", "generate"], required=True)
    p.add_argument("--enums", required=True, help="Path to schemas/metadata/enums.yaml")
    p.add_argument("--input-files", nargs="+", required=True, help="SecretRequest YAML files")
    p.add_argument("--tfvars-out-root", default="envs", help="Root for tfvars outputs (default: envs)")
    p.add_argument("--externalsecret-out-root", default="gitops", help="Root for ExternalSecret outputs (default: gitops)")
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

                write_json(tfvars_path, generate_tfvars(req))
                write_yaml(es_path, generate_externalsecret(req))

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
