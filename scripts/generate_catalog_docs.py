#!/usr/bin/env python3
"""
Registry Catalog Documentation Generator

Purpose:
    Generates human-readable markdown documentation from the YAML registry catalog.
    Transforms the machine-readable catalog into a formatted, searchable document
    for platform and application teams.

What it does:
    1. Loads registry catalog from docs/catalogs/ecr-catalog.yaml
    2. Generates formatted markdown with:
       - Registry inventory table
       - Detailed registry cards with metadata
       - Risk-based grouping
       - Quick reference links
    3. Writes output to docs/REGISTRY_CATALOG.md

Usage:
    python generate_catalog_docs.py [--catalog FILE] [--output FILE]

Options:
    --catalog FILE    Path to YAML catalog (default: docs/catalogs/ecr-catalog.yaml)
    --output FILE     Output markdown file (default: docs/REGISTRY_CATALOG.md)
    --verbose         Enable verbose logging

Output:
    Markdown document with:
    - Summary statistics
    - Registry inventory table
    - Detailed registry cards
    - Risk-based grouping
    - Links to runbooks and ADRs

Exit Codes:
    0 - Success
    1 - Catalog file not found
    2 - Invalid YAML format
    3 - Other error

Related:
    - ADR-0092: ECR Registry Product Strategy
    - ADR-0097: Domain-Based Resource Catalogs
    - docs/catalogs/ecr-catalog.yaml
    - docs/policies/README.md

Author: Platform Team
Created: 2026-01-05
"""

import argparse
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class CatalogGenerator:
    """Generate markdown documentation from YAML catalog"""

    def __init__(self, catalog_path: str):
        self.catalog_path = Path(catalog_path)
        self.catalog = None

    def load_catalog(self) -> Dict[str, Any]:
        """Load YAML catalog"""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        with open(self.catalog_path) as f:
            self.catalog = yaml.safe_load(f)

        return self.catalog

    def generate_summary(self) -> str:
        """Generate summary statistics"""
        registries = self.catalog.get('registries', {})
        total = len(registries)

        # Count by status
        active = sum(1 for r in registries.values()
                    if r.get('metadata', {}).get('status') == 'active')
        deprecated = sum(1 for r in registries.values()
                        if r.get('metadata', {}).get('status') == 'deprecated')

        # Count by risk
        low = sum(1 for r in registries.values()
                 if r.get('metadata', {}).get('risk') == 'low')
        medium = sum(1 for r in registries.values()
                    if r.get('metadata', {}).get('risk') == 'medium')
        high = sum(1 for r in registries.values()
                  if r.get('metadata', {}).get('risk') == 'high')

        return f"""## Summary

**Total Registries:** {total}
**Active:** {active} | **Deprecated:** {deprecated}

**Risk Distribution:**
- 🟢 Low: {low}
- 🟡 Medium: {medium}
- 🔴 High: {high}

**Last Updated:** {self.catalog.get('last_updated', 'Unknown')}
**Managed By:** {self.catalog.get('managed_by', 'platform-team')}
"""

    def generate_inventory_table(self) -> str:
        """Generate registry inventory table"""
        registries = self.catalog.get('registries', {})

        if not registries:
            return "No registries found.\n"

        table = """## Registry Inventory

| Registry | Owner | Risk | Status | Scanning | Lifecycle |
|----------|-------|------|--------|----------|-----------|
"""

        for name, reg in sorted(registries.items()):
            metadata = reg.get('metadata', {})
            governance = reg.get('governance', {})

            owner = metadata.get('owner', 'unknown')
            risk = metadata.get('risk', 'unknown')
            status = metadata.get('status', 'unknown')
            scanning = '✅' if governance.get('image_scanning') else '❌'
            lifecycle = '✅' if governance.get('lifecycle_policy', {}).get('enabled') else '❌'

            # Risk emoji
            risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk, '⚪')

            table += f"| `{name}` | {owner} | {risk_emoji} {risk} | {status} | {scanning} | {lifecycle} |\n"

        return table

    def generate_registry_card(self, name: str, registry: Dict[str, Any]) -> str:
        """Generate detailed registry card"""
        metadata = registry.get('metadata', {})
        aws = registry.get('aws', {})
        governance = registry.get('governance', {})
        access = registry.get('access', {})
        images = registry.get('images', [])
        docs = registry.get('documentation', {})

        risk = metadata.get('risk', 'unknown')
        risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk, '⚪')

        # Risk-based policy mapping (from modules/aws_ecr/locals.tf)
        risk_policies = {
            'low': {
                'encryption': 'AES256 (AWS-managed)',
                'mutability': 'MUTABLE',
                'retention': '20 images',
                'use_for': 'Development, testing, experiments'
            },
            'medium': {
                'encryption': 'AES256 (AWS-managed)',
                'mutability': 'MUTABLE',
                'retention': '30 images',
                'use_for': 'Staging, internal tools, non-critical production'
            },
            'high': {
                'encryption': 'KMS (customer-managed keys)',
                'mutability': 'IMMUTABLE',
                'retention': '50 images',
                'use_for': 'Production, customer-facing, PCI/HIPAA'
            }
        }

        policy = risk_policies.get(risk, {})

        card = f"""### {name}

**ID:** `{metadata.get('id', 'N/A')}`
**Owner:** {metadata.get('owner', 'unknown')}
**Risk:** {risk_emoji} {risk}
**Status:** {metadata.get('status', 'unknown')}
**Created:** {metadata.get('created_date', 'N/A')}

**AWS Details:**
- **Region:** {aws.get('region', 'N/A')}
- **Repository URL:** `{aws.get('repository_url', 'N/A')}`
- **ARN:** `{aws.get('arn', 'N/A')}`

**🔒 Security Controls (Risk-Based):**
- **Encryption:** {policy.get('encryption', 'N/A')}
- **Tag Mutability:** {policy.get('mutability', 'N/A')}
- **Image Retention:** {policy.get('retention', 'N/A')}
- **Image Scanning:** ✅ Enabled on push
- **Use For:** {policy.get('use_for', 'N/A')}
"""

        if images:
            card += "\n**Images:**\n"
            for img in images:
                card += f"- `{img.get('name', 'unknown')}` - {img.get('description', 'No description')}\n"
                card += f"  - Latest: `{img.get('latest_tag', 'N/A')}`\n"

        if docs:
            card += "\n**Documentation:**\n"
            if docs.get('adr'):
                card += f"- [ADR]({docs['adr']})\n"
            if docs.get('runbook'):
                card += f"- [Runbook]({docs['runbook']})\n"

        card += "\n---\n"

        return card

    def generate_markdown(self) -> str:
        """Generate complete markdown document"""
        registries = self.catalog.get('registries', {})

        md = f"""# ECR Registry Catalog

> **Auto-generated from `docs/catalogs/ecr-catalog.yaml`**
> **Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
> **Do not edit this file manually - changes will be overwritten**

{self.generate_summary()}

---

{self.generate_inventory_table()}

---

## Registry Details

"""

        # Group by risk level
        for risk_level in ['high', 'medium', 'low']:
            risk_registries = {name: reg for name, reg in registries.items()
                             if reg.get('metadata', {}).get('risk') == risk_level}

            if risk_registries:
                risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[risk_level]
                md += f"## {risk_emoji} {risk_level.capitalize()} Risk Registries\n\n"

                for name, reg in sorted(risk_registries.items()):
                    md += self.generate_registry_card(name, reg)

        md += """
---

## Related Documentation

- [ADR-0092: ECR Registry Product Strategy](./adrs/ADR-0092-ecr-registry-product-strategy.md)
- [Registry Governance Policy](./governance/registry-governance-policy.md)
- [Platform Team: Create Registry Runbook](./runbooks/platform-team/create-registry.md)
- [App Team: Request Registry Runbook](./runbooks/app-team/request-registry.md)

---

**Questions?** Contact #platform-team on Slack
"""

        return md


def main():
    parser = argparse.ArgumentParser(description="Generate registry catalog documentation")
    parser.add_argument("--catalog", default="docs/catalogs/ecr-catalog.yaml",
                       help="Path to YAML catalog")
    parser.add_argument("--output", default="docs/REGISTRY_CATALOG.md",
                       help="Output markdown file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"Loading catalog from {args.catalog}")

        generator = CatalogGenerator(args.catalog)
        generator.load_catalog()

        if args.verbose:
            print(f"Generating markdown documentation")

        markdown = generator.generate_markdown()

        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(markdown)

        print(f"✅ Generated catalog documentation: {args.output}")
        print(f"   Total registries: {len(generator.catalog.get('registries', {}))}")

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
