"""
---
id: SCRIPT-0025
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0025.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
Purpose: Platform Health & Compliance Reporter
Achievement: Aggregates repository metadata into a human-readable dashboard (PLATFORM_HEALTH.md),
             highlighting orphaned resources, stale lifecycles, and risk distributions.
Value: Provides the "Management Plane" for governance, shifting metadata from boilerplate
       into actionable operational intelligence for leadership.
Relates-To: 85-how-it-works/governance/DOC_AUTO_HEALING.md
"""
import yaml
import re
import os
from datetime import datetime
from pathlib import Path
from validate_metadata import verify_injection
from lib.vq_logger import get_total_reclaimed_hours
from lib.cost_logger import get_cost_summary
from lib.metadata_config import MetadataConfig

cfg = MetadataConfig()

def relativize_links(content, base_dir):
    root = Path('.').resolve()
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    def repl(match):
        label = match.group(1)
        href = match.group(2)
        if href.startswith(('http://', 'https://', 'mailto:', '#', './', '../', '/')):
            return match.group(0)
        if '://' in href:
            return match.group(0)
        path_part, sep, frag = href.partition('#')
        if not path_part:
            return match.group(0)
        target = root / path_part
        if not target.exists():
            return match.group(0)
        rel_path = os.path.relpath(target, start=base_dir)
        rel_path = rel_path.replace(os.sep, '/')
        new_href = rel_path + (sep + frag if sep else '')
        return f'[{label}]({new_href})'

    return link_pattern.sub(repl, content)

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

def get_latest_inventory_report():
    reports_dir = Path("reports/aws-inventory")
    if not reports_dir.exists():
        return None

    candidates = sorted(
        [p for p in reports_dir.glob("aws-inventory-*.json") if "aws-inventory-ecr-" not in p.name],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None

    path = candidates[0]
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    summary = data.get("summary", {})
    scope = data.get("scope", {})
    return {
        "path": str(path),
        "md_path": str(path.with_suffix(".md")),
        "run_id": data.get("run_id"),
        "accounts": scope.get("accounts", []),
        "regions": scope.get("regions", []),
        "summary": summary,
        "errors": data.get("errors", []),
    }

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
            matches = re.findall(r'\[.*?\.(\w+)\]\([^)]+\)', content)
            stats['total'] = len(matches)
    return stats

def get_script_certification_stats():
    stats = {'total': 0, 'certified': 0}
    path = 'docs/10-governance/SCRIPT_CERTIFICATION_MATRIX.md'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Count table rows (excluding header)
            # Row starts with | `scripts/
            rows = re.findall(r'^\| `scripts/.*', content, re.MULTILINE)
            stats['total'] = len(rows)
            # Count certified (Maturity 3)
            # Matches | ⭐⭐⭐ 3 |
            stats['certified'] = len(re.findall(r'\| ⭐⭐⭐ 3 \|', content))
    return stats


def get_maturity_snapshots():
    """Get maturity distribution snapshots from value ledger."""
    stats = {'latest': None, 'trend': []}
    path = '.goldenpath/value_ledger.json'
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
                snapshots = ledger.get('maturity_snapshots', [])
                if snapshots:
                    stats['latest'] = snapshots[-1]
                    # Get last 10 certification rates for trend
                    stats['trend'] = [s.get('certification_rate', 0) for s in snapshots[-10:]]
        except (json.JSONDecodeError, IOError):
            pass
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

    # 1. Standard YAML Catalogs (contracts)
    catalog_dirs = [
        'docs/20-contracts/resource-catalogs',
        'docs/20-contracts/secret-requests'
    ]
    for catalog_dir in catalog_dirs:
        if not os.path.exists(catalog_dir):
            continue

        # Recursive scan for nested catalogs (e.g. docs/20-contracts/secret-requests/**)
        for root, _, files in os.walk(catalog_dir):
            for f in files:
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
                    except: pass

    # 2. Backstage Demo Catalog
    backstage_dir = 'backstage-helm/backstage-catalog'
    if os.path.exists(backstage_dir):
        for f in os.listdir(backstage_dir):
            if f.startswith('all-') and f.endswith('.yaml'):
                try:
                    with open(os.path.join(backstage_dir, f), 'r') as cy:
                        docs = list(yaml.safe_load_all(cy))
                        entity_type = f.replace('all-', '').replace('.yaml', '').title()
                        total_entities = 0
                        for doc in docs:
                            if not doc: continue
                            if doc.get('kind') == 'Location':
                                targets = doc.get('spec', {}).get('targets', [])
                                total_entities += len(targets)
                            elif 'kind' in doc:
                                total_entities += 1

                        if total_entities > 0:
                            catalog_counts[f"IDP {entity_type}"] = total_entities
                except: pass

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


def get_build_timing_stats():
    """Get build timing stats from governance-registry branch."""
    import subprocess
    import csv
    from io import StringIO

    stats = {
        'available': False,
        'recent_builds': [],
        'phase_averages': {},
        'last_updated': None
    }

    try:
        # Fetch latest from governance-registry
        subprocess.run(
            ['git', 'fetch', 'origin', 'governance-registry'],
            capture_output=True, timeout=10
        )

        # Read CSV from governance-registry branch
        result = subprocess.run(
            ['git', 'show', 'origin/governance-registry:environments/development/latest/build_timings.csv'],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            return stats

        # Parse CSV
        reader = csv.DictReader(StringIO(result.stdout))
        rows = list(reader)

        if not rows:
            return stats

        stats['available'] = True
        stats['last_updated'] = rows[-1].get('start_time_utc', 'unknown')

        # Get last 10 builds
        stats['recent_builds'] = rows[-10:]

        # Calculate phase averages
        phase_durations = {}
        for row in rows:
            phase = row.get('phase', 'unknown')
            try:
                duration = int(row.get('duration_seconds', 0))
                if duration > 0:
                    if phase not in phase_durations:
                        phase_durations[phase] = []
                    phase_durations[phase].append(duration)
            except (ValueError, TypeError):
                pass

        for phase, durations in phase_durations.items():
            if durations:
                avg = sum(durations) / len(durations)
                stats['phase_averages'][phase] = {
                    'avg_seconds': round(avg),
                    'count': len(durations)
                }

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        pass

    return stats

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
    script_cert_stats = get_script_certification_stats()
    maturity_snapshots = get_maturity_snapshots()
    build_timing_stats = get_build_timing_stats()
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
    inventory_report = get_latest_inventory_report()

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

    cert_rate = (script_cert_stats['certified'] / script_cert_stats['total'] * 100) if script_cert_stats['total'] > 0 else 0
    lines.append(f"| **Architecture Decisions** | {adr_stats['total']} | [ADR Index](docs/adrs/01_adr_index.md) |")
    lines.append(f"| **Automation Scripts** | {script_stats['total']} | [Script Index](scripts/index.md) |")
    lines.append(f"| **Certified Scripts (M3)** | {script_cert_stats['certified']}/{script_cert_stats['total']} ({cert_rate:.0f}%) | [Certification Matrix](docs/10-governance/SCRIPT_CERTIFICATION_MATRIX.md) |")

    # Add maturity distribution if available
    if maturity_snapshots.get('latest'):
        latest = maturity_snapshots['latest']
        dist = latest.get('maturity_distribution', {})
        m1 = dist.get('M1', 0)
        m2 = dist.get('M2', 0)
        m3 = dist.get('M3', 0)
        lines.append(f"| **Script Maturity Distribution** | M1:{m1} M2:{m2} M3:{m3} | [Value Ledger](.goldenpath/value_ledger.json) |")

    lines.append(f"| **CI Workflows** | {workflow_stats['total']} | [Workflow Index](ci-workflows/CI_WORKFLOWS.md) |")
    lines.append(f"| **Change Logs** | {changelog_stats['total']} | [Changelog Index](docs/changelog/README.md) |")
    lines.append(f"| **Tracked Resources** | {stats['total_files']} | Repository Scan |")

    lines.append("")
    lines.append("## Catalog Inventory")
    lines.append("")
    lines.append("| Catalog | Entity Count |")
    lines.append("| :--- | :--- |")
    # Sort for deterministic output
    for cat in sorted(catalog_stats.keys()):
        lines.append(f"| {cat} | {catalog_stats[cat]} |")

    lines.append("")
    lines.append("## AWS Inventory Snapshot")
    lines.append("")
    if inventory_report:
        summary = inventory_report.get("summary", {})
        accounts = ", ".join(inventory_report.get("accounts", [])) or "n/a"
        regions = ", ".join(inventory_report.get("regions", [])) or "n/a"
        errors = inventory_report.get("errors", [])
        lines.append(f"- **Last run**: `{inventory_report.get('run_id', 'n/a')}`")
        lines.append(f"- **Accounts**: `{accounts}`")
        lines.append(f"- **Regions**: `{regions}`")
        lines.append(f"- **Total resources**: `{summary.get('total_resources', 0)}`")
        lines.append(
            f"- **Tagged**: `{summary.get('tagged', 0)}` | "
            f"**Untagged**: `{summary.get('untagged', 0)}` | "
            f"**Tag violations**: `{summary.get('tag_violations', 0)}`"
        )
        if errors:
            lines.append(f"- **Errors**: `{len(errors)}` (see report)")
        md_path = inventory_report.get("md_path", inventory_report["path"])
        lines.append(f"- **Report**: [`{md_path}`]({md_path})")
    else:
        lines.append("- **Status**: No inventory report found under `reports/aws-inventory`.")

    lines.append("")
    lines.append("## Build Timing Metrics")
    lines.append("")
    if build_timing_stats.get('available'):
        lines.append(f"- **Last Updated**: `{build_timing_stats.get('last_updated', 'n/a')}`")
        lines.append(f"- **Source**: `governance-registry:environments/development/latest/build_timings.csv`")
        lines.append("")
        lines.append("| Phase | Avg Duration | Sample Count |")
        lines.append("| :--- | :--- | :--- |")
        for phase, data in sorted(build_timing_stats.get('phase_averages', {}).items()):
            avg_sec = data.get('avg_seconds', 0)
            count = data.get('count', 0)
            if avg_sec >= 60:
                duration_str = f"{avg_sec // 60}m {avg_sec % 60}s"
            else:
                duration_str = f"{avg_sec}s"
            lines.append(f"| `{phase}` | {duration_str} | {count} |")
    else:
        lines.append("- **Status**: Build timing data not available from governance-registry branch.")

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
    lines.append(f"- **Sidecar Coverage**: `{coverage:.1f}%` ({injected}/{total})")

    lines.append("")
    lines.append("## Project Realized Value (Heartbeat)")
    lines.append("")
    lines.append("> [!TIP]")
    lines.append(f"> Total realized value reclaimed through automation heartbeats: **{total_reclaimed:.1f} hours**.")
    lines.append("")
    lines.append(f"- **ROI Ledger**: [.goldenpath/value_ledger.json](.goldenpath/value_ledger.json)")

    lines.append("")
    lines.append("## Financial Governance (Cloud Cost)")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> Current monthly infrastructure run rate: **${monthly_cost:,.2f} {currency}**.")
    lines.append("")
    lines.append(f"- **Estimated Annual**: `${monthly_cost * 12:,.2f} {currency}`")
    lines.append(f"- **Cost Ledger**: [.goldenpath/cost_ledger.json](.goldenpath/cost_ledger.json)")
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

    audit_content = relativize_links(content, Path('docs/10-governance/reports').resolve())
    with open('docs/10-governance/reports/HEALTH_AUDIT_LOG.md', 'w') as f:
        f.write(
            "\n".join([
                "---",
                "id: HEALTH_AUDIT_LOG",
                "title: Platform Health Audit Log",
                "type: report",
                "category: governance",
                "status: active",
                "owner: platform-team",
                "lifecycle: active",
                "risk_profile:",
                "  production_impact: low",
                "  security_risk: none",
                "  coupling_risk: low",
                "reliability:",
                "  rollback_strategy: git-revert",
                "  observability_tier: bronze",
                "schema_version: 1",
                "relates_to:",
                f"  - {os.path.basename(__file__)}",
                "---",
                "",
                "# Platform Health Audit Log",
                "",
                f"Last updated: `{timestamp}`",
                "",
                "- This file keeps only the latest snapshot.",
                "- Full history can be regenerated from source data if needed.",
                "",
                "## Latest Snapshot",
                "",
                audit_content,
            ])
        )

if __name__ == "__main__":
    generate_report()
