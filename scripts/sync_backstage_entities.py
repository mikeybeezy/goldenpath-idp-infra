#!/usr/bin/env python3
"""
Backstage Entity Sync Utility

Purpose:
    Transforms the ECR Service Catalog (YAML) into Backstage Resource entities.
    This enables seamless discovery of infrastructure in the Backstage UI.

Usage:
    python3 sync_backstage_entities.py --catalog <path> --output <path>
"""

import argparse
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class BackstageSync:
    def __init__(self, catalog_path: str):
        self.catalog_path = Path(catalog_path)
        self.catalog = None

    def load_catalog(self) -> Dict[str, Any]:
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        with open(self.catalog_path) as f:
            self.catalog = yaml.safe_load(f)
        return self.catalog

    def generate_entities(self) -> List[Dict[str, Any]]:
        resources = self.catalog.get('registries', {})
        entities = []

        for name, res in resources.items():
            metadata = res.get('metadata', {})

            # Sanitize name for Backstage (lowercase, alphanumeric, hyphens)
            entity_name = name.lower().replace('_', '-')

            entity = {
                'apiVersion': 'backstage.io/v1alpha1',
                'kind': 'Resource',
                'metadata': {
                    'name': entity_name,
                    'title': name,
                    'description': f"ECR Registry for {name}",
                    'annotations': {
                        'goldenpath-idp.io/risk': metadata.get('risk', 'unknown'),
                        'goldenpath-idp.io/environment': metadata.get('environment', 'unknown'),
                        'goldenpath-idp.io/status': metadata.get('status', 'unknown'),
                        'goldenpath-idp.io/id': metadata.get('id', 'N/A'),
                    },
                    'labels': {
                        'owner': metadata.get('owner', 'unknown'),
                    }
                },
                'spec': {
                    'type': 'container-registry',
                    'owner': metadata.get('owner', 'platform-team'), # Backstage group format would be better
                    'lifecycle': metadata.get('status', 'active'),
                    'system': 'container-infrastructure'
                }
            }
            entities.append(entity)

        return entities

    def write_entities(self, output_path: str, entities: List[Dict[str, Any]]):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            # Use yaml.dump_all for multiple documents
            yaml.dump_all(entities, f, sort_keys=False, default_flow_style=False)

def main():
    parser = argparse.ArgumentParser(description="Sync ECR catalog to Backstage entities")
    parser.add_argument("--catalog", default="docs/catalogs/ecr-catalog.yaml", help="Path to ECR catalog")
    parser.add_argument("--output", default="docs/catalogs/backstage-entities.yaml", help="Output path for Backstage entities")
    args = parser.parse_args()

    try:
        sync = BackstageSync(args.catalog)
        sync.load_catalog()
        entities = sync.generate_entities()
        sync.write_entities(args.output, entities)
        print(f"✅ Successfully generated {len(entities)} Backstage entities in {args.output}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
