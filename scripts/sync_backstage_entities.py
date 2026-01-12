#!/usr/bin/env python3
"""
---
id: SCRIPT-0035
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0035.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

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
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from datetime import datetime
from lib.metadata_config import MetadataConfig

class BackstageSync:
    def __init__(self, catalog_path: str):
        self.catalog_path = Path(catalog_path)
        self.catalog = None
        self.cfg = MetadataConfig()

    def load_catalog(self) -> Dict[str, Any]:
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        with open(self.catalog_path) as f:
            self.catalog = yaml.safe_load(f)
        return self.catalog

    def _get_vq_class(self, risk: str) -> str:
        """Simple mapping of risk to VQ class indicators"""
        mapping = {
            'high': ' 🔴 HV/HQ',
            'medium': ' 🔵 MV/HQ',
            'low': ' ⚫ LV/LQ'
        }
        return mapping.get(risk.lower(), 'Unknown')

    def generate_entities(self) -> List[Dict[str, Any]]:
        resources = self.catalog.get('repositories', {}) # Changed from 'registries' to 'repositories' to match ecr-catalog.yaml
        entities = []

        for name, res in resources.items():
            metadata = res.get('metadata', {})
            entity_name = name.lower().replace('_', '-')

            # Resolve effective metadata (Inheritance Support)
            effective_metadata = self.cfg.get_effective_metadata(str(self.catalog_path), metadata)
            risk = effective_metadata.get('risk', 'unknown')

            entity = {
                'apiVersion': 'backstage.io/v1alpha1',
                'kind': 'Resource',
                'metadata': {
                    'name': entity_name,
                    'title': name,
                    'description': f"ECR Registry for {name}",
                    'value_quantification': {
                        'vq_class': self._get_vq_class(risk)
                    },
                    'annotations': {
                        'goldenpath-idp.io/risk': risk,
                        'goldenpath-idp.io/environment': effective_metadata.get('environment', 'unknown'),
                        'goldenpath-idp.io/status': effective_metadata.get('status', 'unknown'),
                        'goldenpath-idp.io/id': effective_metadata.get('id', 'N/A'),
                        'goldenpath-idp.io/lineage': 'inherited' if 'owner' not in metadata else 'explicit'
                    },
                    'labels': {
                        'owner': effective_metadata.get('owner', 'unknown'),
                    }
                },
                'spec': {
                    'type': 'container-registry',
                    'owner': effective_metadata.get('owner', 'platform-team'),
                    'lifecycle': effective_metadata.get('status', 'active'),
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
    parser.add_argument("--catalog", default="docs/20-contracts/catalogs/ecr-catalog.yaml", help="Path to ECR catalog")
    parser.add_argument("--output", default="docs/20-contracts/catalogs/backstage-entities.yaml", help="Output path for Backstage entities")
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
