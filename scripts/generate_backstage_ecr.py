"""
---
id: SCRIPT-0018
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0018.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

#!/usr/bin/env python3
"""
Backstage ECR Entity Generator

Purpose:
    Transforms the governance-layer ECR catalog (docs/20-contracts/catalogs/ecr-catalog.yaml)
    into Backstage-compliant Resource entities for visualization in the IDP.

Value:
    Provides O(1) visibility into the container registry fleet within Backstage.
"""

import os
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from metadata_config import platform_yaml_dump

SOURCE_CATALOG = "docs/20-contracts/catalogs/ecr-catalog.yaml"
TARGET_DIR = "backstage-helm/catalog/resources/ecr"
ALL_RESOURCES_PATH = "backstage-helm/catalog/all-resources.yaml"


def dump_yaml(data, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        platform_yaml_dump(data, f)

def generate():
    if not os.path.exists(SOURCE_CATALOG):
        print(f"❌ Source catalog not found: {SOURCE_CATALOG}")
        return

    with open(SOURCE_CATALOG, 'r') as f:
        catalog = yaml.safe_load(f)

    repositories = catalog.get('repositories', {})
    entities = []

    for name, data in repositories.items():
        metadata = data.get('metadata', {})
        entity = {
            "apiVersion": "backstage.io/v1alpha1",
            "kind": "Resource",
            "metadata": {
                "name": f"ecr-{name}",
                "description": f"ECR Repository for {name}",
                "tags": [
                    f"env-{metadata.get('environment', 'unknown')}",
                    f"risk-{metadata.get('risk', 'low')}"
                ],
                "annotations": {
                    "goldenpath.io/risk": str(metadata.get('risk', 'low')),
                    "goldenpath.io/id": str(metadata.get('id', 'unknown'))
                }
            },
            "spec": {
                "type": "container-repository",
                "owner": metadata.get('owner', 'platform-team'),
                "dependencyOf": ["resource:goldenpath-ecr-registry"]
            }
        }
        entities.append(entity)

    os.makedirs(TARGET_DIR, exist_ok=True)

    generated_files = []
    for name, entity in zip(repositories.keys(), entities):
        file_path = f"{TARGET_DIR}/{name}.yaml"
        dump_yaml(entity, file_path)
        generated_files.append(f"./resources/ecr/{name}.yaml")

    # Update all-resources.yaml
    if os.path.exists(ALL_RESOURCES_PATH):
        with open(ALL_RESOURCES_PATH, 'r') as f:
            all_res = yaml.safe_load(f)

        # Keep original targets (like artists-db and ecr-registry)
        # but replace/append ECR repos
        current_targets = all_res.get('spec', {}).get('targets', [])
        new_targets = [t for t in current_targets if not t.startswith('./resources/ecr/') and t != './resources/ecr-repositories.yaml']

        # Ensure ecr-registry is there
        if './resources/ecr-registry.yaml' not in new_targets:
            new_targets.append('./resources/ecr-registry.yaml')

        new_targets.extend(generated_files)
        all_res['spec']['targets'] = new_targets

        dump_yaml(all_res, ALL_RESOURCES_PATH)

    print(f"✅ Generated {len(entities)} individual Backstage ECR entities in {TARGET_DIR}")
    print(f"✅ Updated {ALL_RESOURCES_PATH} with {len(generated_files)} new targets")

if __name__ == "__main__":
    generate()
