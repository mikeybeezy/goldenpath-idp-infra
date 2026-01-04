#!/usr/bin/env python3
"""
Purpose: PR Quality Gate & Structural Validator
Achievement: Enforces schema compliance and mandatory sidecar presence in core directories.
             Blocks non-compliant PRs to prevent "Dark Infrastructure" from entering the platform.
Value: Guarantees high-fidelity metadata for every platform resource, ensuring ownership
       and risk data are always present for automated reporting.
"""
import os
import sys
import yaml
import re

REQUIRED_FIELDS = ['id', 'type', 'owner', 'status', 'risk_profile', 'reliability', 'lifecycle']
OPTIONAL_FIELDS = ['relates_to', 'title', 'dependencies', 'version', 'category']

# Directories where metadata.yaml is MANDATORY in every direct subdirectory
SIDECAR_MANDATED_ZONES = [
    'gitops/helm',
    'idp-tooling',
    'envs',
    'apps'
]

def extract_metadata(filepath):
    """
    Extracts and parses metadata from a markdown frontmatter or a standalone YAML file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None, f"Read error: {e}"

    if filepath.endswith('.yaml') or filepath.endswith('.yml'):
        try:
            # Handle possible multiple documents (e.g. if --- is used as a separator)
            data_iterator = yaml.safe_load_all(content)
            for data in data_iterator:
                if data: # Return the first non-empty document
                    return data, None
            return None, "Empty YAML file"
        except yaml.YAMLError as e:
            return None, f"Invalid YAML: {e}"

    # Default to Markdown Frontmatter logic
    if not content.startswith('---'):
        return None, "Missing frontmatter (must start with ---)"

    try:
        # Extract content between first and second ---
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not frontmatter_match:
            return None, "Malformed or unterminated frontmatter"

        data = yaml.safe_load(frontmatter_match.group(1))
        return data, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML: {e}"

def validate_schema(data, filepath):
    """
    Validates the parsed data against the schema.
    """
    errors = []

    # 1. Check Required Fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
        elif field in ['risk_profile', 'reliability', 'lifecycle'] and not isinstance(data[field], dict):
            errors.append(f"Field '{field}' must be a dictionary")

    # 2. ID-Filename/Path Checks
    if 'id' in data:
        filename = os.path.basename(filepath)
        filename_base = os.path.splitext(filename)[0]
        doc_id = str(data['id'])

        if filename == 'metadata.yaml' or filename == 'metadata.yml':
             # For standalone metadata, ID should relate to directory or be descriptive
             # We don't strictly enforce ID-dirname match yet, but we ensure it's not empty
             if not doc_id:
                  errors.append("ID field cannot be empty in metadata.yaml")
        elif filename_base in ['README', 'index']:
             if doc_id.upper() in ['README', 'INDEX']:
                  errors.append(f"{filename} files must have a descriptive ID (not just '{doc_id}')")
        elif doc_id != filename_base:
             errors.append(f"ID mismatch: '{doc_id}' found in header but filename is '{filename_base}'")

    if 'owner' in data:
        if not data['owner']:
             errors.append("Owner field cannot be empty")

    return errors

def verify_injection(base_dir, expected_id):
    """Verifies that the metadata ID has been injected into at least one deployment file."""
    # 1. Check values.yaml in same dir or values/
    candidates = []
    for f in ['values.yaml', 'values.yml']:
        path = os.path.join(base_dir, f)
        if os.path.exists(path):
            candidates.append(path)
    val_dir = os.path.join(base_dir, 'values')
    if os.path.isdir(val_dir):
        for f in os.listdir(val_dir):
            if f.endswith(('.yaml', '.yml')):
                candidates.append(os.path.join(val_dir, f))

    # 2. Check deploy/helm/values.yaml
    deploy_dir = os.path.join(base_dir, 'deploy')
    if os.path.isdir(deploy_dir):
        for root, _, files in os.walk(deploy_dir):
            for f in files:
                if f.startswith('values') and f.endswith(('.yaml', '.yml')):
                    candidates.append(os.path.join(root, f))

    # 3. ArgoCD Application Manifests (Labeling the delivery resource)
    # Skip ArgoCD search for envs/ as 'prod'/'dev' are too generic and cause collisions
    if 'envs/' not in base_dir:
        argocd_dir = os.path.abspath(os.path.join(os.getcwd(), 'gitops', 'argocd', 'apps'))
        if os.path.isdir(argocd_dir):
            comp_name = os.path.basename(base_dir)
            for root, _, files in os.walk(argocd_dir):
                for f in files:
                    if (comp_name in f or comp_name.replace('-', '_') in f) and f.endswith(('.yaml', '.yml')):
                        candidates.append(os.path.join(root, f))

    # If no candidates found, and it's not a Helm chart, we treat it as documentation-only.
    if not candidates:
        is_helm = os.path.exists(os.path.join(base_dir, 'Chart.yaml'))
        return not is_helm

    for cand in candidates:
        if not os.path.exists(cand): continue
        try:
            with open(cand, 'r', encoding='utf-8') as f:
                content = f.read()
            # Simple string check for speed, skip slow YAML loading if possible
            if f"id: {expected_id}" in content or f'id: "{expected_id}"' in content or f"goldenpath.idp/id: {expected_id}" in content:
                return True
        except:
            pass
    return False

def scan_directory(target_path):
    """
    Scans directory for markdown and metadata.yaml files and validates them.
    Also enforces presence of sidecars in mandated zones.
    """
    fail_count = 0
    pass_count = 0

    print(f"🔍 Scanning {target_path} for metadata compliance...")

    files_to_check = []
    # Structural check tracker: { 'path/to/dir': has_sidecar }
    mandatory_checks = {}

    if os.path.isfile(target_path):
        files_to_check = [target_path]
    else:
        for root, dirs, files in os.walk(target_path):
            # Skip hidden and ignored dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules']]

            # Normalize root for zone checking
            norm_root = os.path.relpath(root, '.')
            if norm_root == '.':
                norm_root = ''

            # Identify if this directory is in a Mandated Zone
            # Example: norm_root = 'gitops/helm/kong' -> parent = 'gitops/helm'
            parent_dir = os.path.dirname(norm_root.rstrip('/'))
            if parent_dir in SIDECAR_MANDATED_ZONES:
                 mandatory_checks[norm_root] = False

            for file in files:
                # Check .md files
                if file.endswith('.md') and file not in ['DOC_INDEX.md', 'PLATFORM_HEALTH.md']:
                    files_to_check.append(os.path.join(root, file))

                # Check metadata.yaml sidecars
                if file == 'metadata.yaml' or file == 'metadata.yml':
                    files_to_check.append(os.path.join(root, file))
                    if norm_root in mandatory_checks:
                        mandatory_checks[norm_root] = True

    # 1. Validate Existing Files
    for filepath in files_to_check:
        data, error = extract_metadata(filepath)

        if error:
            print(f"❌ [MISSING/MALFORMED] {filepath}: {error}")
            fail_count += 1
            continue

        validation_errors = validate_schema(data, filepath)
        if validation_errors:
            print(f"❌ [INVALID] {filepath}")
            for err in validation_errors:
                print(f"   - {err}")
            fail_count += 1
        else:
            pass_count += 1

    # 2. Check for Missing Mandatory Sidecars
    for dir_path, has_sidecar in mandatory_checks.items():
        if not has_sidecar:
            print(f"❌ [MISSING] {dir_path}/metadata.yaml (Mandatory in this zone)")
            fail_count += 1
        else:
            # CLOSED-LOOP VERIFICATION: Ensure sidecar data is actually injected
            sidecar_path = os.path.join(dir_path, 'metadata.yaml')
            if not os.path.exists(sidecar_path):
                 sidecar_path = os.path.join(dir_path, 'metadata.yml')

            data, _ = extract_metadata(sidecar_path)
            if data and 'id' in data:
                 if not verify_injection(dir_path, data['id']):
                      print(f"❌ [INJECTION FAILURE] {dir_path}: Sidecar ID '{data['id']}' not found in deployment files")
                      fail_count += 1

    print("-" * 40)
    print(f"✅ Passed: {pass_count}")
    print(f"❌ Failed: {fail_count}")

    if fail_count > 0:
        return 1
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        target_dir = "."
    else:
        target_dir = sys.argv[1]

    sys.exit(scan_directory(target_dir))
