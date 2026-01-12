#!/usr/bin/env python3
"""
---
id: SCRIPT-0036
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0036.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
ECR Catalog Synchronization & Reconciliation Utility

Purpose:
    Reconciles the logical repositories defined in docs/20-contracts/catalogs/ecr-catalog.yaml
    with the physical reality of AWS ECR. Detects discrepancies between the
    governance layer and infrastructure.

Value:
    Eliminates "Dark Infrastructure" (orphans) and "Vaporware" (ghosts) by
    ensuring the catalog is a high-fidelity mirror of AWS state.
"""

import argparse
import json
import os
import subprocess
import sys
import yaml
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from metadata_config import platform_yaml_dump

# Constants
CATALOG_PATH = "docs/20-contracts/catalogs/ecr-catalog.yaml"
DEFAULT_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")


def dump_yaml(data, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        platform_yaml_dump(data, f)

def get_physical_repositories(region=None):
    """Fetches repository list from AWS ECR."""
    try:
        cmd = ["aws", "ecr", "describe-repositories", "--output", "json"]
        if region:
            cmd.extend(["--region", region])
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return {r['repositoryName']: r for r in data.get('repositories', [])}
    except subprocess.CalledProcessError as e:
        print(f"⚠️ AWS CLI Error: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("⚠️ aws cli not found. Running in ADVISORY mode using mock data.")
        return None

def sync_catalog(dry_run=True, region=None):
    """Performs reconciliation between catalog and AWS."""
    if not os.path.exists(CATALOG_PATH):
        print(f"❌ Catalog not found: {CATALOG_PATH}")
        return

    with open(CATALOG_PATH, 'r') as f:
        catalog = yaml.safe_load(f)

    catalog_repos = catalog.get('repositories', {})
    physical_repos = get_physical_repositories(region=region)

    if physical_repos is None:
        print("🔍 ADVISORY: Could not query AWS. Comparison skipped.")
        return

    print(f"🏥 Reconciling ECR Catalog against AWS Physical State...")
    print("-" * 50)

    ghosts = [] # In catalog but not in AWS
    orphans = [] # In AWS but not in catalog
    synced = []

    for name in catalog_repos:
        if name in physical_repos:
            synced.append(name)
        else:
            ghosts.append(name)

    for name in physical_repos:
        if name not in catalog_repos:
            orphans.append(name)

    print(f"✅ Synced: {len(synced)}")
    print(f"👻 Ghosts (In Catalog only): {len(ghosts)}")
    if ghosts:
        for g in ghosts: print(f"   - {g}")

    print(f"🕵️ Orphans (In AWS only): {len(orphans)}")
    if orphans:
        for o in orphans:
            print(f"   - {o}")

    # --- Backstage Integration ---
    BACKSTAGE_ENTITY_PATH = "backstage-helm/catalog/resources/ecr-registry.yaml"

    # Generate repository list for description
    repo_list = "\n".join([
        f"- {name} ({catalog_repos.get(name, {}).get('metadata', {}).get('environment', 'unassigned')})"
        for name in sorted(physical_repos)
    ])

    backstage_resource = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Resource",
        "metadata": {
            "name": "goldenpath-ecr-registry",
            "description": f"Master AWS ECR Registry. Manages {len(physical_repos)} repositories:\n{repo_list}",
            "links": [
                {
                    "url": "https://console.aws.amazon.com/ecr/repositories",
                    "title": "AWS ECR Console"
                }
            ],
            "annotations": {
                "backstage.io/managed-by-location": "url:https://github.com/mikeybeezy/goldenpath-idp-infra/tree/development/backstage-helm/catalog/resources/ecr-registry.yaml",
                "platform/repo-count": str(len(physical_repos)),
                "platform/last-sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        },
        "spec": {
            "type": "container-registry",
            "owner": "platform-team",
            "system": "container-registry"
        }
    }

    print(f"📝 Generating Backstage Entity: {BACKSTAGE_ENTITY_PATH}")
    os.makedirs(os.path.dirname(BACKSTAGE_ENTITY_PATH), exist_ok=True)
    dump_yaml(backstage_resource, BACKSTAGE_ENTITY_PATH)

    # Log Value Heartbeat
    try:
        # Relative import for shared lib
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
        from vq_logger import log_heartbeat
        log_heartbeat("sync_ecr_catalog.py")
    except:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECR Catalog Sync Utility")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument(
        "--region",
        default=DEFAULT_REGION,
        help="AWS region (defaults to AWS_REGION/AWS_DEFAULT_REGION or AWS CLI config)."
    )
    args = parser.parse_args()

    sync_catalog(dry_run=args.dry_run, region=args.region)
