#!/usr/bin/env python3
"""
---
id: SCRIPT-0050
type: script
owner: platform-team
status: active
maturity: 2
test:
  runner: pytest
  command: python3 scripts/eks_build_parser.py --mode validate --input-files docs/catalogs/clusters/platform/dev/EKS-0001.yaml
  evidence: execution
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List
import yaml

# Add scripts directory to path for lib imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lib.metadata_config import MetadataConfig

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def parse_request(doc: Dict[str, Any], src_path: Path) -> Dict[str, Any]:
    spec = doc.get("spec", {})
    node_group = spec.get("nodeGroup", {})

    # Map schema fields (camelCase) to Terraform variable structure (snake_case)
    return {
        "eks_config": {
            "enabled": True,
            "cluster_name": spec.get("clusterName"),
            "version": spec.get("version", "1.29"),
            "enable_ssh_break_glass": spec.get("enableSshBreakGlass", False),
            "node_group": {
                "name": node_group.get("name", "default"),
                "min_size": node_group.get("minSize"),
                "max_size": node_group.get("maxSize"),
                "desired_size": node_group.get("desiredSize"),
                "instance_types": node_group.get("instanceTypes", ["t3.medium"]),
                "disk_size": node_group.get("diskSize", 20),
                "capacity_type": node_group.get("capacityType", "ON_DEMAND")
            }
        },
        "enable_storage_addons": spec.get("enableStorageAddons", True),
        "bootstrap_mode": spec.get("bootstrapMode", False)
    }

def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["validate", "generate"], required=True)
    parser.add_argument("--input-files", nargs="+", required=True)
    parser.add_argument("--out-dir", default="envs", help="Root for tfvars outputs")
    args = parser.parse_args()

    cfg = MetadataConfig()
    failures = []

    for f in args.input_files:
        src = Path(f)
        try:
            doc = load_yaml(src)
            # 1. Basic structural validation
            if doc.get("kind") != "ClusterRequest":
                raise ValueError(f"Invalid kind: {doc.get('kind')}. Expected 'ClusterRequest'")
            
            # 2. Schema deep validation
            errors = []
            req_fields = cfg.get_required_fields("cluster_request")
            for field in req_fields:
                if field not in doc:
                    errors.append(f"Missing required field: '{field}'")
            
            if errors:
                raise ValueError(", ".join(errors))

            config = parse_request(doc, src)
            
            if args.mode == "generate":
                env = doc.get("metadata", {}).get("environment", "dev")
                cid = doc.get("id", "EKS-DEFAULT")
                # Direct output to env root to be visible to Terraform
                out_path = Path(args.out_dir) / env / f"{cid}.auto.tfvars.json"
                write_json(out_path, config)
                print(f"[OK] {src} -> {out_path}")
            else:
                print(f"[OK] {src} validated against schema")
        except Exception as e:
            failures.append(f"{src}: {e}")

    if failures:
        for fail in failures: print(fail)
        sys.exit(1)

if __name__ == "__main__":
    main()
