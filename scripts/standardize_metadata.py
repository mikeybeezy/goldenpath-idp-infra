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
import copy
from datetime import datetime
import sys

# Add lib to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from metadata_config import MetadataConfig

cfg = MetadataConfig()

# Fallback owner and versions if schema lookup fails
OWNER = "platform-team"
VERSION = "1.0"

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
    data = None
    body = ""

    # 1. Parse existing content
    if is_yaml:
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict): data = {}
        except:
            data = {}
    else:
        data, body_start = parse_frontmatter(content)
        if data is None and content.startswith('---'):
            # Handle corrupted or multi-dash blocks
            lines = content.splitlines()
            last_dash_idx = -1
            for i, line in enumerate(lines[:30]):
                if line.strip().startswith('---'):
                    last_dash_idx = i
            body = "\n".join(lines[last_dash_idx+1:]) if last_dash_idx != -1 else content
        elif data is not None:
            body = content[body_start:]
        else:
            body = content

    filename_base = os.path.splitext(os.path.basename(filepath))[0]
    title_match = re.search(r'^#\s+(.*)', body, re.MULTILINE) if not is_yaml else None
    default_title = title_match.group(1) if title_match else filename_base

    # 2. GET EFFECTIVE CONTEXT (Inheritance)
    effective_data = cfg.get_effective_metadata(filepath, data or {})

    # 3. CONTEXTUAL HEALING (Mapping logic based on location)
    rel_path = os.path.relpath(filepath, '.')

    doc_type = effective_data.get('type') or get_type_from_path(filepath)
    category = effective_data.get('category', 'platform')

    # Aggressive contextual mapping
    if 'docs/adrs' in rel_path or 'docs/30-architecture' in rel_path:
        category, doc_type = 'architecture', 'adr'
    elif 'docs/changelog' in rel_path:
        category, doc_type = 'changelog', 'changelog'
    elif 'runbooks/' in rel_path:
        category, doc_type = 'runbooks', 'runbook'
    elif 'docs/policies' in rel_path or 'docs/70-operations' in rel_path:
        category, doc_type = 'compliance', 'policy'
    elif 'idp-tooling/' in rel_path:
        category = 'platform'

    # 4. START RECONSTRUCTION
    # We use a skeleton based on the HEALED doc_type
    skeleton = cfg.get_skeleton(doc_type)
    if not skeleton and doc_type in ['policy', 'runbook', 'strategy', 'implementation-plan', 'report']:
        skeleton = cfg.get_skeleton('documentation')

    if not skeleton:
        skeleton = {'id': '', 'title': '', 'type': 'documentation', 'owner': OWNER, 'status': 'active'}

    # final_data = skeleton + effective_metadata
    new_data = copy.deepcopy(skeleton)
    for k, v in effective_data.items():
        if v not in [None, "", "unknown"]:
            if k in new_data and isinstance(new_data[k], dict) and isinstance(v, dict):
                new_data[k].update(v)
            else:
                new_data[k] = v

    # Re-apply healed category/type
    new_data['category'] = category
    new_data['type'] = doc_type
    if not new_data.get('title'): new_data['title'] = default_title

    # 5. ID ENFORCEMENT
    if filename_base in ['README', 'metadata', 'index']:
        rel_dir = os.path.relpath(os.path.dirname(filepath), '.')
        if rel_dir == '.':
            new_id = 'ROOT_README'
        else:
            prefix = 'HELM' if 'gitops/helm' in rel_dir else ('TOOL' if 'idp-tooling' in rel_dir else ('ENV' if 'envs' in rel_dir else 'APPS'))
            new_id = f"{prefix}_{os.path.basename(rel_dir).replace('-', '_').upper()}"
            if filename_base in ['index', 'metadata']:
                new_id = f"{new_id}_{filename_base.upper()}"

        current_id = str(new_data.get('id', '')).upper()
        if not current_id or current_id in ['README', 'METADATA', 'INDEX']:
            new_data['id'] = new_id
    else:
        if not new_data.get('id'):
            new_data['id'] = filename_base

    # 6. PRUNING (Dry Governance)
    # Remove fields from local sidecar if they match the parent EXACTLY
    parent_data = cfg.find_parent_metadata(filepath)
    if parent_data:
        # print(f"DEBUG: Pruning against parent: {parent_data.get('owner')}")
        for k in list(new_data.keys()):
            if k in ['id', 'title', 'type']: continue # Keep core identity fields
            if k in parent_data and new_data[k] == parent_data[k]:
                # print(f"DEBUG: Pruning redundant field: {k}")
                del new_data[k]

    # 7. Final Polish
    if 'reliability' in new_data and isinstance(new_data['reliability'], dict):
        if not new_data['reliability'].get('observability_tier'):
            new_data['reliability']['observability_tier'] = 'bronze'

    # 8. Reconstruct and Save
    new_fm = yaml.dump(new_data, Dumper=IndentDumper, sort_keys=False, default_flow_style=False, allow_unicode=True, indent=2)
    if is_yaml:
        # Standard YAML sidecars should only have a leading marker, trailing marker signals a second document.
        new_content = f"---\n{new_fm}"
    else:
        # Markdown frontmatter MANDATES markers at both ends.
        new_content = f"---\n{new_fm}---\n\n{body.lstrip()}"

    new_content = re.sub(r'\n{3,}', '\n\n', new_content).strip() + '\n'

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Standardized: {filepath}")
    else:
        # print(f"ℹ️  No changes needed: {filepath}")
        pass

    # CLOSED-LOOP GOVERNANCE: Inject metadata into associated K8s resources
    if filename_base == 'metadata':
        inject_governance(filepath, new_data)

def inject_governance(sidecar_path, data):
    """Propagates metadata values into associated values.yaml files."""
    base_dir = os.path.dirname(sidecar_path)
    candidates = []

    # Standalone K8s Manifests in current dir
    for f in os.listdir(base_dir):
        if f.endswith(('.yaml', '.yml')) and f != 'metadata.yaml' and f != 'metadata.yml':
            # Check if it looks like a K8s resource
            try:
                with open(os.path.join(base_dir, f), 'r') as check_f:
                    if 'apiVersion:' in check_f.read(1024):
                        candidates.append(os.path.join(base_dir, f))
            except: pass

    # ArgoCD Apps
    argocd_dir = os.path.abspath(os.path.join(os.getcwd(), 'gitops', 'argocd', 'apps'))
    if os.path.isdir(argocd_dir):
        # Improved matching: Must match accurately or be in a specific subdirectory
        target_name = os.path.basename(base_dir)
        for root, _, files in os.walk(argocd_dir):
             for f in files:
                # Specific matching to avoid collision between idp-tooling and gitops/helm
                is_match = False
                if target_name in f and f.endswith(('.yaml', '.yml')):
                    if 'gitops/helm' in sidecar_path and 'apps/' not in root: is_match = True
                    elif 'apps/' in sidecar_path and 'apps/' in root: is_match = True
                    elif 'idp-tooling' in sidecar_path: is_match = False # Tooling usually doesn't have an ArgoCD app itself

                if is_match:
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

            # Check if change is needed
            current_gov = v_data.get('governance', {})
            current_ann = v_data.get('metadata', {}).get('annotations', {})

            is_k8s = v_data.get('apiVersion') and v_data.get('kind')
            needs_update = False

            if is_k8s:
                anno_id = current_ann.get('goldenpath.idp/id')
                anno_owner = current_ann.get('goldenpath.idp/owner')
                target_id = str(gov_block['id'])
                target_owner = str(gov_block.get('owner', 'unknown'))

                if anno_id != target_id or anno_owner != target_owner:
                    needs_update = True
                    if 'metadata' not in v_data: v_data['metadata'] = {}
                    if 'annotations' not in v_data['metadata']: v_data['metadata']['annotations'] = {}
                    v_data['metadata']['annotations']['goldenpath.idp/id'] = target_id
                    v_data['metadata']['annotations']['goldenpath.idp/owner'] = target_owner
            else:
                if current_gov != gov_block:
                    needs_update = True
                    v_data['governance'] = gov_block

            if needs_update:
                with open(cand, 'w', encoding='utf-8') as f:
                    f.write("# Managed by scripts/standardize_metadata.py\n")
                    yaml.dump(v_data, f, Dumper=IndentDumper, sort_keys=False, default_flow_style=False, indent=2)
                print(f"{'🏷️' if is_k8s else '💉'} {'Annotated' if is_k8s else 'Injected'} resource: {cand}")
        except Exception as e:
            print(f"⚠️ Failed injection for {cand}: {e}")

def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ['.']

    for target in targets:
        if not os.path.exists(target):
            print(f"⚠️ Warning: Target {target} not found.")
            continue

        if os.path.isfile(target):
            standardize_file(target)
            continue

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in ['.git', '.gemini', 'node_modules', 'tmp', '__pycache__']]
            norm_root = os.path.relpath(root, '.')

            # Structural check: Create missing metadata.yaml in mandated zones
            path_parts = norm_root.split(os.sep)
            is_mandated = any(zone in norm_root for zone in SIDECAR_MANDATED_ZONES)

            if is_mandated and len(path_parts) >= 2:
                if 'metadata.yaml' not in files and 'metadata.yml' not in files:
                    sidecar_path = os.path.join(root, 'metadata.yaml')
                    print(f"🩹 Creating missing sidecar: {sidecar_path}")
                    with open(sidecar_path, 'w') as f:
                        f.write("---\n# Placeholder\n---\n")
                    files.append('metadata.yaml')

            for file in files:
                is_md = file.endswith('.md') and file not in ['DOC_INDEX.md', 'PLATFORM_HEALTH.md']
                is_meta = file in ['metadata.yaml', 'metadata.yml']
                if is_md or is_meta:
                    standardize_file(os.path.join(root, file))

    # Log Value Heartbeat
    try:
        from lib.vq_logger import log_heartbeat
        log_heartbeat("standardize_metadata.py")
    except:
        pass

if __name__ == "__main__":
    main()
