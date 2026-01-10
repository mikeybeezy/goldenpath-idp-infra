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
import yaml

SOURCE_CATALOG = "docs/20-contracts/catalogs/ecr-catalog.yaml"
TARGET_DIR = "backstage-helm/catalog/resources/ecr"
ALL_RESOURCES_PATH = "backstage-helm/catalog/all-resources.yaml"

class IndentDumper(yaml.SafeDumper):
    """Ensure list items are indented under their parent keys."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def dump_yaml(data, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            sort_keys=False,
            default_flow_style=False,
            Dumper=IndentDumper,
        )

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
