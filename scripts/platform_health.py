"""
Purpose: Platform Health & Compliance Reporter
Achievement: Aggregates repository metadata into a human-readable dashboard (PLATFORM_HEALTH.md),
             highlighting orphaned resources, stale lifecycles, and risk distributions.
Value: Provides the "Management Plane" for governance, shifting metadata from boilerplate
       into actionable operational intelligence for leadership.
"""
import yaml
import re
import os
from datetime import datetime
from validate_metadata import verify_injection
from lib.vq_logger import get_total_reclaimed_hours
from lib.cost_logger import get_cost_summary
from lib.metadata_config import MetadataConfig

cfg = MetadataConfig()

def parse_frontmatter(filepath):
    """Simple frontmatter parser."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            return yaml.safe_load(fm_text), None
    except Exception as e:
        return None, str(e)
    return None, "No frontmatter found"

def get_adr_stats():
    stats = {'total': 0, 'active': 0}
    path = 'docs/adrs/01_adr_index.md'
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
            matches = re.findall(r'- (ADR-\d+)', content)
            stats['total'] = len(set(matches))
            # Rough check for 'active' in the table rows if possible
            lower_content = content.lower()
            stats['active'] = lower_content.count('| active |') + lower_content.count('| accepted |')
    return stats

def get_changelog_stats():
    stats = {'total': 0, 'latest': None}
    dir_path = 'docs/changelog/entries'
    if os.path.exists(dir_path):
        entries = [f for f in os.listdir(dir_path) if f.endswith('.md')]
        stats['total'] = len(entries)
        if entries:
            stats['latest'] = sorted(entries)[-1]
    return stats

def calculate_v1_readiness(health_stats, adr_stats, comp_rate, coverage):
    """Calculates V1 Readiness Score (0-100%)."""
    # Weights
    W_METADATA = 0.25
    W_INJECTION = 0.25
    W_ADR = 0.20
    W_ORPHANS = 0.15
    W_STALE = 0.15

    # Components
    metadata_score = comp_rate / 100.0
    injection_score = coverage / 100.0
    adr_score = (adr_stats['active'] / adr_stats['total']) if adr_stats['total'] > 0 else 0
    orphan_score = max(0, 1 - (len(health_stats['orphans']) / max(1, health_stats['total_files'])))
    stale_score = max(0, 1 - (len(health_stats['stale_files']) / max(1, health_stats['total_files'])))

    total = (metadata_score * W_METADATA +
             injection_score * W_INJECTION +
             adr_score * W_ADR +
             orphan_score * W_ORPHANS +
             stale_score * W_STALE)

    return total * 100

def get_script_stats():
    stats = {'total': 0, 'categories': {}}
    path = 'scripts/index.md'
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
            # Count [name.sh](...) links
            matches = re.findall(r'\[.*?\.(\w+)\]\(file://.*?\)', content)
            stats['total'] = len(matches)
    return stats

def get_workflow_stats():
    stats = {'total': 0}
    path = 'ci-workflows/CI_WORKFLOWS.md'
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
            matches = re.findall(r'### .*?', content)
            stats['total'] = len(matches)
    return stats

def get_catalog_stats():
    catalog_counts = {}
    catalog_dir = 'docs/catalogs'
    if os.path.exists(catalog_dir):
        for f in os.listdir(catalog_dir):
            if f.endswith('.yaml') and f != 'backstage-entities.yaml':
                try:
                    with open(os.path.join(catalog_dir, f), 'r') as cy:
                        data = yaml.safe_load(cy)
                        if not data: continue
                        # Special handling for hierarchical ECR catalog
                        if 'physical_registry' in data and 'repositories' in data:
                            catalog_counts['Ecr Registry'] = 1
                            catalog_counts['Ecr Repositories'] = len(data['repositories'])
                            continue

                        # Find the first dictionary key that isn't metadata-typical
                        for key, value in data.items():
                            if isinstance(value, dict) and key not in ['version', 'owner', 'domain', 'last_updated', 'managed_by']:
                                catalog_counts[f.replace('.yaml', '').replace('-catalog', '').title()] = len(value)
                                break
                except:
                    pass
    return catalog_counts

def get_historical_trends():
    trends = []
    path = 'docs/10-governance/reports/HEALTH_AUDIT_LOG.md'
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Match: **Unified Maturity**: `100.0%`
                matches = re.findall(r'Unified Maturity\*\*: \`(.*?)\%\`', content)
                trends = [m for m in matches if re.match(r'^\d+(\.\d+)?$', m)]
        except:
            pass
    return trends

def get_compliance_stats():
    path = 'compliance-report.json'
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def calculate_maturity(stats):
    """Calculates a risk-weighted maturity score (0-100)."""
    impact_weights = {'high': 5, 'medium': 2, 'low': 1, 'none': 0, 'unknown': 1}
    total_weight = 0
    penalty_weight = 0

    # Weight by production impact
    for impact, count in stats['risk_profile']['production_impact'].items():
        total_weight += count * impact_weights.get(impact, 1)

    # Penalize for orphans and stale files (weighted by high impact)
    penalty_weight += len(stats['orphans']) * 3
    penalty_weight += len(stats['stale_files']) * 2

    if total_weight == 0: return 100
    score = max(0, min(100, 100 * (1 - (penalty_weight / total_weight))))
    return score

import json

def generate_report(target_dir='.'):
    stats = {
        'total_files': 0,
        'categories': {},
        'status': {},
        'risk_profile': {
            'production_impact': {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        },
        'owners': {},
        'orphans': [],
        'stale_files': [],
        'missing_metadata': [],
        'maturity_scores': [],
        'injection_coverage': {
            'total_mandated': 0,
            'total_injected': 0,
            'gaps': []
        }
    }

    today = datetime.now().date()
    adr_stats = get_adr_stats()
    script_stats = get_script_stats()
    workflow_stats = get_workflow_stats()
    catalog_stats = get_catalog_stats()
    compliance_data = get_compliance_stats()
    trends = get_historical_trends()

    # Step 1: Scan for Markdown & Sidecars
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'api_server']]
        for file in files:
            is_md = file.endswith('.md') and file != 'DOC_INDEX.md'
            is_sidecar = file == 'metadata.yaml' or file == 'metadata.yml'
            if not is_md and not is_sidecar: continue

            filepath = os.path.join(root, file)
            if is_sidecar:
                try:
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)
                        error = None
                except Exception as e:
                    data, error = None, str(e)
            else:
                data, error = parse_frontmatter(filepath)

            if error:
                if is_md: stats['missing_metadata'].append(filepath)
                continue

            # STEP 1.1: Resolve Inheritance
            effective_data = cfg.get_effective_metadata(filepath, data)

            if is_md:
                stats['total_files'] += 1
                cat = effective_data.get('category', 'unknown')
                stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
                status = str(effective_data.get('status', 'unknown')).lower()
                stats['status'][status] = stats['status'].get(status, 0) + 1

                risk = effective_data.get('risk_profile', {})
                if isinstance(risk, dict):
                    impact = risk.get('production_impact', 'unknown')
                    if impact in stats['risk_profile']['production_impact']:
                        stats['risk_profile']['production_impact'][impact] += 1

                owner = effective_data.get('owner', 'unknown')
                if owner == 'unknown' or not owner:
                    stats['orphans'].append(filepath)
                else:
                    stats['owners'][owner] = stats['owners'].get(owner, 0) + 1

                # Maturity tracking
                rel = effective_data.get('reliability', {})
                if isinstance(rel, dict):
                    stats['maturity_scores'].append(int(rel.get('maturity', 1)))

                # Stale check
                lifecycle = data.get('lifecycle', {})
                if isinstance(lifecycle, dict):
                    supported_until = lifecycle.get('supported_until')
                    if supported_until:
                        try:
                            if isinstance(supported_until, str):
                                end_date = datetime.strptime(supported_until, '%Y-%m-%d').date()
                            else:
                                end_date = supported_until
                            if end_date < today: stats['stale_files'].append({'path': filepath, 'deadline': str(supported_until)})
                        except: pass

            if is_sidecar:
                norm_root = os.path.relpath(root, target_dir)
                parent_dir = os.path.dirname(norm_root.rstrip('/'))
                MANDATED_ZONES = ['gitops/helm', 'idp-tooling', 'envs', 'apps']

                # Only count DIRECT children of mandated zones, not nested subdirs
                # e.g., gitops/helm/loki ✅ but gitops/helm/loki/values ❌
                is_direct_child = parent_dir in MANDATED_ZONES

                if is_direct_child:
                    stats['injection_coverage']['total_mandated'] += 1
                    if data and 'id' in data:
                        if verify_injection(root, data['id']):
                            stats['injection_coverage']['total_injected'] += 1
                        else:
                            stats['injection_coverage']['gaps'].append(filepath)

    # Step 2: Multi-Source Ingestion
    adr_stats = get_adr_stats()
    script_stats = get_script_stats()
    workflow_stats = get_workflow_stats()
    catalog_stats = get_catalog_stats()
    compliance_data = get_compliance_stats()
    changelog_stats = get_changelog_stats()
    maturity_score = calculate_maturity(stats)
    total_reclaimed = get_total_reclaimed_hours()
    cost_summary = get_cost_summary()
    monthly_cost = cost_summary.get("current_monthly_estimate", 0.0)
    currency = cost_summary.get("currency", "USD")

    comp_rate = ((stats['total_files'] - len(stats['missing_metadata'])) / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
    total_inj = stats['injection_coverage']['total_mandated']
    injected = stats['injection_coverage']['total_injected']
    coverage = (injected / total_inj * 100) if total_inj > 0 else 0

    mean_confidence = (sum(stats['maturity_scores']) / len(stats['maturity_scores'])) if stats['maturity_scores'] else 1.0

    v1_readiness = calculate_v1_readiness(stats, adr_stats, comp_rate, coverage)

    # Step 3: Layout Generation
    lines = []
    lines.append("---")
    lines.append("id: PLATFORM_HEALTH")
    lines.append("title: Platform Health & Compliance Report")
    lines.append("type: documentation")
    lines.append("category: governance")
    lines.append("status: active")
    lines.append("owner: platform-team")
    lines.append(f"version: '{datetime.now().strftime('%Y-%m-%d')}'")
    lines.append("relates_to:")
    lines.append(f"  - {os.path.basename(__file__)}")
    lines.append("---")
    lines.append("")

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines.append("## 🏥 Platform Health Command Center")
    lines.append("")
    lines.append(f"**Generated**: `{timestamp}` | **V1 Readiness**: `{v1_readiness:.1f}%` | **Mean Confidence**: `{'⭐' * int(round(mean_confidence)) or '⭐'} ({mean_confidence:.1f}/5.0)`")
    lines.append("")
    lines.append(f"**Realized Value**: `{total_reclaimed:.1f} Hours` | **Infra Run Rate**: `${monthly_cost:,.2f} {currency}/mo`")

    lines.append("")
    lines.append("## V1 Platform Readiness Gate")
    lines.append("")
    lines.append("> [!IMPORTANT]")
    lines.append(f"> The platform is currently **{v1_readiness:.1f}%** ready for V1 production rollout.")

    lines.append("")
    lines.append("| Milestone | Status | Readiness |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **Metadata Integrity** | {'✅' if comp_rate > 95 else '⚠️'} | {comp_rate:.1f}% |")
    lines.append(f"| **Injection Integrity** | {'✅' if coverage > 95 else '⚠️'} | {coverage:.1f}% |")
    lines.append(f"| **Architecture Maturity** | {'✅' if adr_stats['active'] == adr_stats['total'] else '🚧'} | {adr_stats['active']}/{adr_stats['total']} Active |")
    lines.append(f"| **Changelog Activity** | ✅ | {changelog_stats['total']} Entries |")

    if len(trends) > 1:
        lines.append("")
        lines.append("## 📈 Governance Velocity (Historical Trend)")
        lines.append("")
        lines.append("```mermaid")
        lines.append("xychart-beta")
        lines.append("    title \"V1 Readiness Trend (Last 10 Runs)\"")
        lines.append(f'    x-axis ["Run -{len(trends[-10:])}", "Run -1"]')
        lines.append(f'    y-axis "Readiness %" 0 --> 100')
        lines.append(f"    line [{', '.join(trends[-10:])}]")
        lines.append("```")

    lines.append("")
    lines.append("## Knowledge Graph Vitality")
    lines.append("")
    lines.append(f"| Metric | Count | Source |")
    lines.append(f"| :--- | :--- | :--- |")
    lines.append(f"| **Architecture Decisions** | {adr_stats['total']} | [ADR Index](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/01_adr_index.md) |")
    lines.append(f"| **Automation Scripts** | {script_stats['total']} | [Script Index](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/index.md) |")
    lines.append(f"| **CI Workflows** | {workflow_stats['total']} | [Workflow Index](file:///Users/mikesablaze/goldenpath-idp-infra/ci-workflows/CI_WORKFLOWS.md) |")
    lines.append(f"| **Change Logs** | {changelog_stats['total']} | [Changelog Index](file:///Users/mikesablaze/goldenpath-idp-infra/docs/changelog/README.md) |")
    lines.append(f"| **Tracked Resources** | {stats['total_files']} | Repository Scan |")

    lines.append("")
    lines.append("## Catalog Inventory")
    lines.append("| Catalog | Entity Count |")
    lines.append("| :--- | :--- |")
    # Sort for deterministic output
    for cat in sorted(catalog_stats.keys()):
        lines.append(f"| {cat} | {catalog_stats[cat]} |")

    lines.append("")
    lines.append("## 🛡️ Risk & Maturity Visualization")
    lines.append("")
    lines.append("```mermaid")
    lines.append("pie title Production Impact distribution")
    for impact, count in stats['risk_profile']['production_impact'].items():
        if count > 0: lines.append(f'    "{impact.upper()}" : {count}')
    lines.append("```")

    lines.append("")
    lines.append("## Governance Maturity")
    lines.append("")
    comp_rate = ((stats['total_files'] - len(stats['missing_metadata'])) / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
    lines.append(f"- **Metadata Compliance**: `{comp_rate:.1f}%`")
    lines.append(f"- **Risk-Weighted Score**: `{maturity_score:.1f}%`")

    if compliance_data:
        lines.append(f"- **Infrastructure Drift**: `{100 - compliance_data.get('compliance_rate', 0):.1f}%` (via `compliance-report.json`)")

    lines.append("")
    lines.append("## Injection Coverage")
    lines.append("")
    total = stats['injection_coverage']['total_mandated']
    injected = stats['injection_coverage']['total_injected']
    coverage = (injected / total * 100) if total > 0 else 0
    lines.append("")
    lines.append("## Project Realized Value (Heartbeat)")
    lines.append("")
    lines.append("> [!TIP]")
    lines.append(f"> Total realized value reclaimed through automation heartbeats: **{total_reclaimed:.1f} hours**.")
    lines.append("")
    lines.append(f"- **ROI Ledger**: [.goldenpath/value_ledger.json](file://.goldenpath/value_ledger.json)")

    lines.append("")
    lines.append("## Financial Governance (Cloud Cost)")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> Current monthly infrastructure run rate: **${monthly_cost:,.2f} {currency}**.")
    lines.append("")
    lines.append(f"- **Estimated Annual**: `${monthly_cost * 12:,.2f} {currency}`")
    lines.append(f"- **Cost Ledger**: [.goldenpath/cost_ledger.json](file://.goldenpath/cost_ledger.json)")
    lines.append("- **Tooling**: Infracost (CI-integrated)")

    lines.append("")
    lines.append("## Operational Risks")
    lines.append("")
    lines.append(f"- **Orphaned (No Owner)**: {len(stats['orphans'])}")
    lines.append(f"- **Stale (Past Lifecycle)**: {len(stats['stale_files'])}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Strategic Guidance")
    lines.append("")
    lines.append("- **V1 Readiness Indicator**: A composite metric tracking Architecture (ADRs), Governance (Metadata/Injection), and Delivery (Changelogs). Target: 100%.")
    lines.append("- **Visualizing Trends**: The `xychart-beta` is best viewed in GitHub/GitLab or VS Code with updated Mermaid support (v10.x+). It tracks our 'Readiness Velocity' across audit cycles.")

    # Persist Final Dashboard
    content = "\n".join(lines)
    os.makedirs('docs/10-governance/reports', exist_ok=True)
    with open('PLATFORM_HEALTH.md', 'w') as f:
        f.write(content + "\n\n<!-- AUTOMATED REPORT - DO NOT EDIT MANUALLY -->\n")

    with open('docs/10-governance/reports/HEALTH_AUDIT_LOG.md', 'a') as f:
        f.write(f"\n\n---\n### Audit: {timestamp}\n{content}")

if __name__ == "__main__":
    generate_report()
