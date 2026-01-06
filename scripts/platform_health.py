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

def parse_frontmatter(filepath):
    """Simple frontmatter parser."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match frontmatter using regex
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            return yaml.safe_load(fm_text), None
    except Exception as e:
        return None, str(e)
    return None, "No frontmatter found"

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
        'injection_coverage': {
            'total_mandated': 0,
            'total_injected': 0,
            'gaps': []
        }
    }

    today = datetime.now().date()

    for root, dirs, files in os.walk(target_dir):
        # Skip hidden and ignored dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'api_server']]

        for file in files:
            is_md = file.endswith('.md') and file != 'DOC_INDEX.md'
            is_sidecar = file == 'metadata.yaml' or file == 'metadata.yml'

            if not is_md and not is_sidecar:
                continue

            filepath = os.path.join(root, file)
            data, error = parse_frontmatter(filepath)

            if error:
                if is_md: stats['missing_metadata'].append(filepath)
                continue

            if is_md:
                stats['total_files'] += 1
                # Category stats
                cat = data.get('category', 'unknown')
                stats['categories'][cat] = stats['categories'].get(cat, 0) + 1

                # Status stats
                status = data.get('status', 'unknown')
                stats['status'][status] = stats['status'].get(status, 0) + 1

                # Risk stats
                risk = data.get('risk_profile', {})
                if isinstance(risk, dict):
                    impact = risk.get('production_impact', 'unknown')
                    if impact in stats['risk_profile']['production_impact']:
                        stats['risk_profile']['production_impact'][impact] += 1

                # Owner stats & Orphan detection
                owner = data.get('owner', 'unknown')
                if owner == 'unknown' or not owner:
                    stats['orphans'].append(filepath)
                else:
                    stats['owners'][owner] = stats['owners'].get(owner, 0) + 1

                # Stale detection (lifecycle)
                lifecycle = data.get('lifecycle', {})
                if isinstance(lifecycle, dict):
                    supported_until = lifecycle.get('supported_until')
                    if supported_until:
                        try:
                            # Some might be strings or dates depending on parser
                            if isinstance(supported_until, str):
                                end_date = datetime.strptime(supported_until, '%Y-%m-%d').date()
                            else:
                                end_date = supported_until

                            if end_date < today:
                                stats['stale_files'].append({
                                    'path': filepath,
                                    'deadline': supported_until
                                })
                        except:
                            pass

            # Injection Coverage Check (for metadata sidecars)
            if is_sidecar:
                norm_root = os.path.relpath(root, target_dir)
                parent_dir = os.path.dirname(norm_root.rstrip('/'))
                MANDATED_ZONES = ['gitops/helm', 'idp-tooling', 'envs', 'apps']
                if parent_dir in MANDATED_ZONES:
                    stats['injection_coverage']['total_mandated'] += 1
                    if data and 'id' in data:
                         if verify_injection(root, data['id']):
                              stats['injection_coverage']['total_injected'] += 1
                         else:
                              stats['injection_coverage']['gaps'].append(filepath)

    # Build Report Content
    lines = []
    lines.append("---")
    lines.append("id: PLATFORM_HEALTH")
    lines.append("title: Platform Health & Compliance Report")
    lines.append("type: documentation")
    lines.append("category: governance")
    lines.append("status: active")
    lines.append("owner: platform-team")
    lines.append(f"version: '{datetime.now().strftime('%Y-%m-%d')}'")
    lines.append("dependencies: []")
    lines.append("risk_profile:")
    lines.append("  production_impact: low")
    lines.append("  security_risk: none")
    lines.append("  coupling_risk: low")
    lines.append("reliability:")
    lines.append("  rollback_strategy: git-revert")
    lines.append("  observability_tier: gold")
    lines.append("lifecycle:")
    lines.append("  supported_until: '2028-01-01'")
    lines.append("  breaking_change: false")
    lines.append("relates_to:")
    lines.append(f"  - {os.path.basename(__file__)}")
    lines.append("---")
    lines.append("")
    lines.append("# 🏥 Platform Health Report")
    lines.append(f"**Date Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Total Tracked Resources**: {stats['total_files']}")
    compliance = ((stats['total_files'] - len(stats['missing_metadata'])) / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
    lines.append(f"**Metadata Compliance**: {compliance:.1f}%")

    lines.append("\n## 📊 Lifecycle Distribution")
    for s, count in stats['status'].items():
        lines.append(f"- **{s.capitalize()}**: {count}")

    lines.append("\n## 🛡️ Risk Summary (Production Impact)")
    for impact, count in stats['risk_profile']['production_impact'].items():
        lines.append(f"- **{impact.capitalize()}**: {count}")

    lines.append("\n## 📂 Top Categories")
    sorted_cats = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats[:5]:
        lines.append(f"- **{cat}**: {count}")

    lines.append("\n## 🚨 Operational Risks")
    lines.append(f"- **Orphaned Files (No Owner)**: {len(stats['orphans'])}")
    lines.append(f"- **Stale Files (Past Lifecycle)**: {len(stats['stale_files'])}")

    if stats['orphans']:
        lines.append("\n### Orphan Sample")
        for p in stats['orphans'][:5]:
            lines.append(f"- {p}")

    if stats['stale_files']:
        lines.append("\n### Stale Sample")
        for s in stats['stale_files'][:5]:
            lines.append(f"- {s['path']} (Expired: {s['deadline']})")

    lines.append("\n## 💉 Closed-Loop Injection Coverage")
    lines.append("> [!NOTE]")
    lines.append("> **How it works**: This metric measures the percentage of 'Governance Sidecars' that have been successfully propagated into live deployment configurations (Helm values, ArgoCD manifests).")

    total = stats['injection_coverage']['total_mandated']
    injected = stats['injection_coverage']['total_injected']
    coverage = (injected / total * 100) if total > 0 else 0
    lines.append(f"- **Coverage**: {coverage:.1f}% ({injected}/{total})")

    if stats['injection_coverage']['gaps']:
        lines.append("\n### Injection Gaps (Dark Infrastructure)")
        lines.append("The following components have sidecars but are NOT yet advertising their governance data in deployment manifests:")
        for p in stats['injection_coverage']['gaps'][:10]:
            lines.append(f"- {p}")

    report_content = "\n".join(lines)
    print(report_content)

    # Persist to file
    with open('PLATFORM_HEALTH.md', 'w', encoding='utf-8') as f:
        f.write(report_content + '\n')
    print(f"\n✅ Report persisted to PLATFORM_HEALTH.md")

if __name__ == "__main__":
    generate_report()
