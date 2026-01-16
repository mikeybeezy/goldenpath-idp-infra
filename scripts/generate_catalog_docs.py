#!/usr/bin/env python3
"""
---
id: SCRIPT-0019
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0019.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Multi-Domain Platform Catalog Generator

Purpose:
    Generates human-readable markdown documentation from YAML resource catalogs
    (e.g., ECR registries, S3 buckets, RDS instances). It acts as the bridging
    layer between machine-readable YAML and human-centric documentation.

What it does:
    1. Loads a YAML resource catalog based on the 'domain' field.
    2. Maps risk levels to security policies using an external YAML library.
    3. Generates a summary dashboard, inventory table, and detailed resource cards.
    4. Handles domain-based label pluralization (e.g., Registry -> Registries).
    5. Writes a formatted Markdown document to a specified location.

Usage:
    python3 generate_catalog_docs.py --catalog <path> --output <path> --policies <path>

Exit Codes:
    0 - Success
    1 - Catalog file not found
    2 - Invalid YAML format
    3 - Other error
"""

import argparse
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class CatalogGenerator:
    """Generate markdown documentation from YAML catalog"""

    def __init__(self, catalog_path: str, policy_path: str = "docs/10-governance/policies/ecr-risk-settings.yaml"):
        self.catalog_path = Path(catalog_path)
        self.policy_path = Path(policy_path)
        self.catalog = None
        self.policies = {}

    def load_catalog(self) -> Dict[str, Any]:
        """Load YAML catalog and policies"""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        with open(self.catalog_path) as f:
            self.catalog = yaml.safe_load(f)

        # Domain-based configuration
        self.domain = self.catalog.get('domain', 'resources')
        # Map domain to the key used for resources in the YAML
        self.resource_key = {
            'container-registries': 'registries',
            'delivery': 'repositories', # Aligned with new hierarchical ECR catalog
            's3-buckets': 'buckets',
            'rds-instances': 'instances'
        }.get(self.domain, 'resources')

        # Domain display name labels
        self.domain_label = self.domain.replace('-', ' ').title()

        # Singularize resource key for labels
        if self.resource_key.endswith('ies'):
            self.resource_label = self.resource_key.replace('-', ' ').title()[:-3] + 'y'
        elif self.resource_key.endswith('s'):
            self.resource_label = self.resource_key.replace('-', ' ').title()[:-1]
        else:
            self.resource_label = self.resource_key.replace('-', ' ').title()

        if self.policy_path.exists():
            with open(self.policy_path) as f:
                docs = list(yaml.safe_load_all(f))
                for doc in docs:
                    if doc and isinstance(doc, dict) and 'policies' in doc:
                        self.policies = doc['policies']
                        break

        return self.catalog

    def generate_summary(self) -> str:
        """Generate summary statistics"""
        resources = self.catalog.get(self.resource_key, {})
        total = len(resources)

        # Count by status
        active = sum(1 for r in resources.values()
                    if r.get('metadata', {}).get('status') == 'active')
        deprecated = sum(1 for r in resources.values()
                        if r.get('metadata', {}).get('status') == 'deprecated')

        # Count by risk
        low = sum(1 for r in resources.values()
                 if r.get('metadata', {}).get('risk') == 'low')
        medium = sum(1 for r in resources.values()
                    if r.get('metadata', {}).get('risk') == 'medium')
        high = sum(1 for r in resources.values()
                  if r.get('metadata', {}).get('risk') == 'high')

        summary = f"**Total {self.resource_key.title()}:** {total}\n"
        summary += f"**Active:** {active} | **Deprecated:** {deprecated}\n\n"

        if 'physical_registry' in self.catalog:
             summary += f"⚓ **Physical Registry:** `{self.catalog['physical_registry']}`\n\n"

        summary += "**Risk Distribution:**\n"
        summary += f"- 🟢 Low: {low}\n"
        summary += f"- 🟡 Medium: {medium}\n"
        summary += f"- 🔴 High: {high}\n\n"
        summary += f"**Last Updated:** {self.catalog.get('last_updated', 'Unknown')}\n"
        summary += f"**Managed By:** {self.catalog.get('managed_by', 'platform-team')}\n"

        return f"## Summary\n\n{summary}"

    def generate_inventory_table(self) -> str:
        """Generate resource inventory table"""
        resources = self.catalog.get(self.resource_key, {})

        if not resources:
            return f"No {self.resource_key} found.\n"

        table = f"## {self.resource_label} Inventory\n\n"

        if self.domain == 'container-registries':
            table += "| Registry | Owner | Risk | Status | Scanning | Lifecycle |\n"
            table += "|----------|-------|------|--------|----------|-----------|\n"
        else:
            table += f"| {self.resource_label} | Owner | Risk | Status |\n"
            table += "|----------|-------|------|--------|\n"

        for name, res in sorted(resources.items()):
            metadata = res.get('metadata', {})
            governance = res.get('governance', {})

            owner = metadata.get('owner', 'unknown')
            risk = metadata.get('risk', 'unknown')
            status = metadata.get('status', 'unknown')

            # Risk emoji
            risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk, '⚪')

            if self.domain == 'container-registries':
                scanning = '✅' if governance.get('image_scanning') else '❌'
                lifecycle = '✅' if governance.get('lifecycle_policy', {}).get('enabled') else '❌'
                table += f"| `{name}` | {owner} | {risk_emoji} {risk} | {status} | {scanning} | {lifecycle} |\n"
            else:
                table += f"| `{name}` | {owner} | {risk_emoji} {risk} | {status} |\n"

        return table

    def generate_resource_card(self, name: str, resource: Dict[str, Any]) -> str:
        """Generate detailed resource card"""
        metadata = resource.get('metadata', {})
        aws = resource.get('aws', {})
        governance = resource.get('governance', {})
        access = resource.get('access', {})
        images = resource.get('images', []) if self.domain == 'container-registries' else []
        docs = resource.get('documentation', {})

        risk = metadata.get('risk', 'unknown')
        risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(risk, '⚪')

        # Risk-based policy mapping
        policy = self.policies.get(risk, {})

        # Fallback values if policy not found
        if not policy:
            policy = {
                'encryption': 'Unknown',
                'mutability': 'Unknown',
                'retention': 'Unknown',
                'use_for': 'Unknown'
            }

        card = f"### {name}\n\n"
        card += f"**ID:** `{metadata.get('id', 'N/A')}`\n"
        card += f"**Owner:** {metadata.get('owner', 'unknown')}\n"
        card += f"**Risk:** {risk_emoji} {risk}\n"
        card += f"**Status:** {metadata.get('status', 'unknown')}\n"
        card += f"**Created:** {metadata.get('created_date', 'N/A')}\n\n"

        if aws:
            card += "**AWS Details:**\n"
            for k, v in aws.items():
                label = k.replace('_', ' ').title()
                if 'url' in k.lower() or 'arn' in k.lower():
                    card += f"- **{label}:** `{v}`\n"
                else:
                    card += f"- **{label}:** {v}\n"
            card += "\n"

        card += "**🔒 Security Controls (Risk-Based):**\n"
        card += f"- **Encryption:** {policy.get('encryption', 'N/A')}\n"
        card += f"- **Tag Mutability:** {policy.get('mutability', 'N/A')}\n"
        card += f"- **Image Retention:** {policy.get('retention', 'N/A')}\n"
        if self.domain == 'container-registries':
            card += "- **Image Scanning:** ✅ Enabled on push\n"
        card += f"- **Use For:** {policy.get('use_for', 'N/A')}\n"

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
        """Generate complete markdown document with platform frontmatter"""
        resources = self.catalog.get(self.resource_key, {})

        # 1. Generate Platform Frontmatter
        md = "---\n"
        md += f"id: REGISTRY_CATALOG\n"
        md += f"title: {self.domain_label} Catalog\n"
        md += "type: documentation\n"
        md += "category: catalog\n"
        md += f"status: active\n"
        md += f"owner: {self.catalog.get('owner', 'platform-team')}\n"
        md += "version: '1.0'\n"
        md += "risk_profile:\n"
        md += "  production_impact: low\n"
        md += "  security_risk: none\n"
        md += "  coupling_risk: low\n"
        md += "reliability:\n"
        md += "  rollback_strategy: git-revert\n"
        md += "  observability_tier: silver\n"
        md += "lifecycle: active\n"
        md += f"supported_until: 2028-01-01\n"
        md += "breaking_change: false\n"
        md += "relates_to:\n"
        md += f"  - ADR-0097\n"
        md += f"  - ADR-0100\n"
        md += f"  - {Path(__file__).name}\n"
        md += "---\n\n"

        # 2. Add Main Header and Meta
        md += f"# {self.domain_label} Catalog\n\n"
        md += f"> **Auto-generated from `{self.catalog_path}`**\n"
        md += f"> **Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
        md += "> **Do not edit this file manually - changes will be overwritten**\n\n"

        md += self.generate_summary()
        md += "\n---\n\n"
        md += self.generate_inventory_table()
        md += "\n---\n\n"
        md += f"## {self.resource_label} Details\n\n"

        # Group by risk level
        for risk_level in ['high', 'medium', 'low']:
            risk_resources = {name: res for name, res in resources.items()
                             if res.get('metadata', {}).get('risk') == risk_level}

            if risk_resources:
                risk_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}[risk_level]
                md += f"## {risk_emoji} {risk_level.capitalize()} Risk {self.resource_key.title()}\n\n"

                for name, res in sorted(risk_resources.items()):
                    md += self.generate_resource_card(name, res)

        md += """
---

## Related Documentation

- [ADR-0092: ECR Registry Product Strategy](./adrs/ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0097: Domain-Based Resource Catalogs](./adrs/ADR-0097-domain-based-resource-catalogs.md)
- [Registry Governance Policy](./governance/registry-governance-policy.md)

---

**Questions?** Contact #platform-team on Slack
"""

        return md

def main():
    parser = argparse.ArgumentParser(description="Generate platform catalog documentation")
    parser.add_argument("--catalog", default="docs/20-contracts/resource-catalogs/ecr-catalog.yaml",
                       help="Path to YAML catalog")
    parser.add_argument("--output", default="docs/REGISTRY_CATALOG.md",
                       help="Output markdown file")
    parser.add_argument("--policies", default="docs/10-governance/policies/ecr-risk-settings.yaml",
                       help="Path to YAML policies")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"Loading catalog from {args.catalog} (Policies: {args.policies})")

        generator = CatalogGenerator(args.catalog, args.policies)
        generator.load_catalog()

        if args.verbose:
            print(f"Generating markdown documentation for domain: {generator.domain}")

        markdown = generator.generate_markdown()

        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(markdown)

        print(f"✅ Generated {generator.domain_label} documentation: {args.output}")
        print(f"   Resource type: {generator.resource_key}")
        print(f"   Total items: {len(generator.catalog.get(generator.resource_key, {}))}")

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
