#!/usr/bin/env python3
"""
ECR Catalog Synchronization & Reconciliation Utility

Purpose:
    Reconciles the logical repositories defined in docs/catalogs/ecr-catalog.yaml
    with the physical reality of AWS ECR. Detects discrepancies between the
    governance layer and infrastructure.

Value:
    Eliminates "Dark Infrastructure" (orphans) and "Vaporware" (ghosts) by
    ensuring the catalog is a high-fidelity mirror of AWS state.
"""

import os
import yaml
import json
import subprocess
import argparse
from pathlib import Path

# Constants
CATALOG_PATH = "docs/catalogs/ecr-catalog.yaml"

def get_physical_repositories():
    """Fetches repository list from AWS ECR."""
    try:
        result = subprocess.run(
            ["aws", "ecr", "describe-repositories", "--output", "json"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        return {r['repositoryName']: r for r in data.get('repositories', [])}
    except subprocess.CalledProcessError as e:
        print(f"⚠️ AWS CLI Error: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("⚠️ aws cli not found. Running in ADVISORY mode using mock data.")
        return None

def sync_catalog(dry_run=True):
    """Performs reconciliation between catalog and AWS."""
    if not os.path.exists(CATALOG_PATH):
        print(f"❌ Catalog not found: {CATALOG_PATH}")
        return

    with open(CATALOG_PATH, 'r') as f:
        catalog = yaml.safe_load(f)

    catalog_repos = catalog.get('repositories', {})
    physical_repos = get_physical_repositories()

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
        for o in orphans: print(f"   - {o}")

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
    args = parser.parse_args()
    
    sync_catalog(dry_run=args.dry_run)
