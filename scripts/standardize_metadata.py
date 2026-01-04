#!/usr/bin/env python3
"""
Purpose: Automated Remediation Engine ("The Healer")
Achievement: Enables O(1) schema evolution across 300+ files. Merges existing data with
             the canonical governance skeleton, enforces path-based IDs, and creates
             missing metadata sidecars in mandated zones. Supports **Governance Injection Pass**
             to propagate metadata into live Kubernetes resources (Values/Apps).
Value: Eliminates manual backfills and "governance debt" while bridging the gap
       between documentation and live infrastructure auditability.
"""
import os
import re
import yaml
from datetime import datetime

# Standard owner and versions
OWNER = "platform-team"
VERSION = "1.0"

# Schema Skeleton
SKELETON = {
    'id': '',
    'title': '',
    'type': 'documentation',
    'category': 'unknown',
    'version': VERSION,
    'owner': OWNER,
    'status': 'active',
    'dependencies': [],
    'risk_profile': {
        'production_impact': 'low',
        'security_risk': 'none',
        'coupling_risk': 'low'
    },
    'reliability': {
        'rollback_strategy': 'git-revert',
        'observability_tier': 'bronze'
    },
    'lifecycle': {
        'supported_until': '2028-01-01',
        'breaking_change': False
    },
    'relates_to': []
}

class IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)

def get_type_from_path(filepath):
    if 'adrs/' in filepath: return 'adr'
    if 'changelog/' in filepath: return 'changelog'
    if 'runbooks/' in filepath: return 'runbook'
    if 'governance/' in filepath: return 'policy'
    if 'contracts/' in filepath: return 'contract'
    if 'strategy' in filepath: return 'strategy'
    return 'documentation'

def parse_frontmatter(content):
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        try:
            return yaml.safe_load(fm_text), match.end()
        except:
            return None, 0
    return None, 0

SIDECAR_MANDATED_ZONES = [
    'gitops/helm',
    'idp-tooling',
    'envs',
    'apps'
]

def standardize_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    is_yaml = filepath.endswith('.yaml') or filepath.endswith('.yml')

    # AGGRESSIVE CLEANUP: Strip multiple frontmatter blocks or corrupted dashes
    if is_yaml:
        try:
            data_iterator = yaml.safe_load_all(content)
            data = None
            for d in data_iterator:
                if d:
                    data = d
                    break
            body = "" # No body for YAML sidecars
        except:
            data, body = None, ""
    else:
        data, body_start = parse_frontmatter(content)

        # If no frontmatter found by regex, but file starts with dashes, it's corrupted
        if data is None and content.startswith('---'):
            lines = content.splitlines()
            last_dash_idx = -1
            for i, line in enumerate(lines[:30]):
                if line.strip() == '---' or line.strip().startswith('---'):
                    last_dash_idx = i
            if last_dash_idx != -1:
                body = "\n".join(lines[last_dash_idx+1:])
            else:
                body = content
        elif data is not None:
            body = content[body_start:]
            while body.lstrip().startswith('---'):
                lines = body.lstrip().splitlines()
                next_dash = -1
                for i, line in enumerate(lines[1:30]):
                    if line.strip().startswith('---'):
                        next_dash = i + 1
                        break
                if next_dash != -1:
                    body = "\n".join(lines[next_dash+1:])
                else:
                    body = body.lstrip()[3:]
        else:
            body = content

    filename_base = os.path.splitext(os.path.basename(filepath))[0]
    title_match = re.search(r'^#\s+(.*)', body, re.MULTILINE) if not is_yaml else None
    default_title = title_match.group(1) if title_match else filename_base

    # Base Data Merging
    new_data = SKELETON.copy()
    if data:
        for key in data:
            if key in new_data and isinstance(new_data[key], dict) and isinstance(data[key], dict):
                new_data[key].update(data[key])
            else:
                new_data[key] = data[key]

    if not new_data.get('title'):
        new_data['title'] = default_title

    if 'type' not in (data or {}):
        new_data['type'] = get_type_from_path(filepath)

    # ID ENFORCEMENT logic
    if filename_base == 'README' or filename_base == 'metadata' or filename_base == 'index':
        rel_dir = os.path.relpath(os.path.dirname(filepath), '.')
        if rel_dir == '.':
             new_id = 'GOLDENPATH_IDP_ROOT_README'
        else:
             prefix = 'HELM' if 'gitops/helm' in rel_dir else ('TOOL' if 'idp-tooling' in rel_dir else ('ENV' if 'envs' in rel_dir else 'SCRIPTS'))
             new_id = prefix + '_' + os.path.basename(rel_dir).replace('-', '_').upper()
             if filename_base == 'index' or filename_base == 'metadata':
                  new_id = new_id + '_' + filename_base.upper()

        current_id = str(new_data.get('id', '')).upper()
        if not current_id or current_id in ['README', 'METADATA', 'INDEX']:
             new_id = new_id + '_' + filename_base.upper() if (filename_base == 'index' or filename_base == 'metadata') else new_id
             new_data['id'] = new_id
    else:
        new_data['id'] = filename_base

    new_data['title'] = str(new_data['title']).strip('"`')

    # Construct New Content
    new_fm = yaml.dump(new_data, Dumper=IndentDumper, sort_keys=False, default_flow_style=False, allow_unicode=True, indent=2)
    if is_yaml:
        new_content = f"---\n{new_fm}---\n"
    else:
        new_content = f"---\n{new_fm}---\n\n{body.lstrip()}"

    new_content = re.sub(r'\n{3,}', '\n\n', new_content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ Standardized: {filepath}")

    # CLOSED-LOOP GOVERNANCE: Inject metadata into associated K8s resources
    if filename_base == 'metadata':
        inject_governance(filepath, new_data)

def inject_governance(sidecar_path, data):
    """Propagates metadata values into associated values.yaml files."""
    base_dir = os.path.dirname(sidecar_path)
    candidates = []

    # 1. Standard Helm Locations
    for v_file in ['values.yaml', 'values.yml']:
        if os.path.exists(os.path.join(base_dir, v_file)):
            candidates.append(os.path.join(base_dir, v_file))

    # 2. Multi-Environment Values
    val_dir = os.path.join(base_dir, 'values')
    if os.path.isdir(val_dir):
        for f in os.listdir(val_dir):
            if f.endswith(('.yaml', '.yml')):
                candidates.append(os.path.join(val_dir, f))

    # 3. Application deploy directories
    deploy_dir = os.path.join(base_dir, 'deploy')
    if os.path.isdir(deploy_dir):
        for root, _, files in os.walk(deploy_dir):
            for f in files:
                if f.startswith('values') and f.endswith(('.yaml', '.yml')):
                    candidates.append(os.path.join(root, f))

    # 4. ArgoCD Application Manifests (Labeling the delivery resource)
    argocd_dir = os.path.abspath(os.path.join(os.getcwd(), 'gitops', 'argocd', 'apps'))
    if os.path.isdir(argocd_dir):
        comp_name = os.path.basename(base_dir)
        for root, _, files in os.walk(argocd_dir):
            for f in files:
                if (comp_name in f or comp_name.replace('-', '_') in f) and f.endswith(('.yaml', '.yml')):
                    candidates.append(os.path.join(root, f))

    gov_block = {
        'id': data.get('id'),
        'owner': data.get('owner'),
        'risk_profile': data.get('risk_profile'),
        'reliability': data.get('reliability')
    }

    for cand in candidates:
        try:
            with open(cand, 'r', encoding='utf-8') as f:
                v_content = f.read()

            v_data = yaml.safe_load(v_content) or {}
            if not isinstance(v_data, dict): continue

            # If it's a K8s resource (like ArgoCD Application), use annotations
            if v_data.get('apiVersion') and v_data.get('kind'):
                if 'metadata' not in v_data: v_data['metadata'] = {}
                if 'annotations' not in v_data['metadata']: v_data['metadata']['annotations'] = {}

                v_data['metadata']['annotations']['goldenpath.idp/id'] = str(gov_block['id'])
                v_data['metadata']['annotations']['goldenpath.idp/owner'] = str(gov_block['owner'])
                v_data['metadata']['annotations']['goldenpath.idp/risk'] = str(gov_block['risk_profile'].get('production_impact', 'unknown'))
                print(f"🏷️  Annotated K8s resource: {cand}")
            else:
                # Standard values.yaml injection
                v_data['governance'] = gov_block
                print(f"💉 Injected governance into: {cand}")

            with open(cand, 'w', encoding='utf-8') as f:
                f.write("# Managed by scripts/standardize-metadata.py\n")
                yaml.dump(v_data, f, Dumper=IndentDumper, sort_keys=False, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"⚠️ Failed injection for {cand}: {e}")

def main():
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '.gemini', 'node_modules', 'tmp', '__pycache__']]
        norm_root = os.path.relpath(root, '.')

        # Structural check: Create missing metadata.yaml in mandated zones
        parent_dir = os.path.dirname(norm_root.rstrip('/'))
        if parent_dir in SIDECAR_MANDATED_ZONES:
            if 'metadata.yaml' not in files and 'metadata.yml' not in files:
                sidecar_path = os.path.join(root, 'metadata.yaml')
                print(f"🩹 Creating missing sidecar: {sidecar_path}")
                with open(sidecar_path, 'w') as f:
                    f.write("---\n# Template\n---\n")
                files.append('metadata.yaml')

        for file in files:
            if file.endswith('.md') and not file in ['DOC_INDEX.md', 'PLATFORM_HEALTH.md']:
                standardize_file(os.path.join(root, file))
            if file == 'metadata.yaml' or file == 'metadata.yml':
                standardize_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
