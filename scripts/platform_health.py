import os
import yaml
import re
from datetime import datetime

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
        'missing_metadata': []
    }

    today = datetime.now().date()

    for root, dirs, files in os.walk(target_dir):
        # Skip hidden and ignored dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'api_server']]

        for file in files:
            if not file.endswith('.md') or file == 'DOC_INDEX.md':
                continue

            stats['total_files'] += 1
            filepath = os.path.join(root, file)
            data, error = parse_frontmatter(filepath)

            if error:
                stats['missing_metadata'].append(filepath)
                continue

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

    # Print Report
    print("# 🏥 Platform Health Report")
    print(f"**Date Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"**Total Tracked Resources**: {stats['total_files']}")
    print(f"**Metadata Compliance**: {((stats['total_files'] - len(stats['missing_metadata'])) / stats['total_files'] * 100):.1f}%")

    print("\n## 📊 Lifecycle Distribution")
    for s, count in stats['status'].items():
        print(f"- **{s.capitalize()}**: {count}")

    print("\n## 🛡️ Risk Summary (Production Impact)")
    for impact, count in stats['risk_profile']['production_impact'].items():
        print(f"- **{impact.capitalize()}**: {count}")

    print("\n## 📂 Top Categories")
    sorted_cats = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats[:5]:
        print(f"- **{cat}**: {count}")

    print("\n## 🚨 Operational Risks")
    print(f"- **Orphaned Files (No Owner)**: {len(stats['orphans'])}")
    print(f"- **Stale Files (Past Lifecycle)**: {len(stats['stale_files'])}")

    if stats['orphans']:
        print("\n### Orphan Sample")
        for p in stats['orphans'][:5]:
            print(f"- {p}")

    if stats['stale_files']:
        print("\n### Stale Sample")
        for s in stats['stale_files'][:5]:
            print(f"- {s['path']} (Expired: {s['deadline']})")

if __name__ == "__main__":
    generate_report()
