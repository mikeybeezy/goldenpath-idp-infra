"""
---
id: SCRIPT-0011
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0011.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

#!/usr/bin/env python3
"""
Purpose: Automated Relationship & Dependency Extractor
Achievement: Scans content for ADR/CL mentions, Markdown links, and dependency prefixes
             to programmatically wire together the Platform Knowledge Graph.
Value: Surfaces "Hidden Dependencies" and impact areas, allowing the Platform Team
       to perform high-confidence risk assessment before infrastructure changes.
"""

import os
import re
import glob
import yaml
import argparse
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from metadata_config import platform_yaml_dump
from collections import defaultdict


def extract_doc_id_from_path(file_path):
    """Convert file path to document ID, matching standardize-metadata.py logic"""
    basename = os.path.basename(file_path)
    filename_base = os.path.splitext(basename)[0]

    if filename_base == 'README':
        # Path-based ID for READMEs
        dirname = os.path.dirname(file_path)
        if not dirname or dirname == '.':
            return 'GOLDENPATH_IDP_ROOT_README'
        else:
            rel_dir = os.path.relpath(dirname, '.')
            return rel_dir.replace(os.sep, '_').upper() + '_README'

    # For others, ID matches filename base
    return filename_base


def extract_metadata_fields(content, current_file):
    """Extract relationship and dependency references from document content"""
    relationships = set()
    dependencies = set()

    # Pattern 1: Inline `docs/...` references
    inline_refs = re.findall(r'`(docs/[^`]+\.md)`', content)
    relationships.update(inline_refs)

    # Pattern 2: ADR/CL mentions (e.g. ADR-0026, CL-0042)
    adr_mentions = re.findall(r'\b(ADR-\d{4})\b', content)
    relationships.update(adr_mentions)
    cl_mentions = re.findall(r'\b(CL-\d{4})\b', content)
    relationships.update(cl_mentions)

    # Pattern 3: Markdown links to local files
    md_links = re.findall(r'\]\(([^)]+\.md)\)', content)
    for link in md_links:
        if link.startswith('../') or link.startswith('./'):
            current_dir = os.path.dirname(current_file)
            resolved = os.path.normpath(os.path.join(current_dir, link))
            relationships.add(resolved)
        elif link.startswith('docs/') or link.startswith('apps/') or link.startswith('envs/'):
            relationships.add(link)

    # Pattern 4: Dependencies in content
    # Look for "depends on: <name>", "module: <name>", or "service: <name>"
    dep_patterns = [
        r'(?:depends on|dependency):\s*`?(module:[^`\s,]+)`?',
        r'(?:depends on|dependency):\s*`?(service:[^`\s,]+)`?',
        r'(?:depends on|dependency):\s*`?(chart:[^`\s,]+)`?',
        r'- (module:[^\s,]+)',
        r'- (service:[^\s,]+)',
        r'- (chart:[^\s,]+)',
    ]
    for pattern in dep_patterns:
        found = re.findall(pattern, content, re.IGNORECASE)
        dependencies.update(found)

    # Pattern 5: Path-based references in docs
    paths_to_scan = ['gitops/', 'idp-tooling/', 'bootstrap/', 'modules/']
    for p_dir in paths_to_scan:
        found_paths = re.findall(rf'`({p_dir}[^`]+\.md)`', content)
        relationships.update(found_paths)

    return relationships, list(dependencies)


def read_metadata(file_path):
    """Read YAML frontmatter from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has frontmatter
        if not content.startswith('---'):
            return None, content

        # Split frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None, content

        # Parse YAML
        metadata = yaml.safe_load(parts[1])
        rest_of_file = parts[2]

        return metadata, rest_of_file
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, None


def write_metadata(file_path, metadata, content):
    """Write updated metadata back to file"""
    try:
        # Serialize metadata to YAML
        yaml_str = platform_yaml_dump(metadata)

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml_str)
            f.write('---\n')
            f.write(content.lstrip())

        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False


def process_file(file_path, all_doc_ids, dry_run=False, verbose=False):
    """Process a single file to extract and update relationships and dependencies"""
    metadata, rest_of_file = read_metadata(file_path)

    if metadata is None:
        return False

    # Extract relationships and dependencies
    with open(file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()

    found_rels, found_deps = extract_metadata_fields(full_content, file_path)

    # Convert relative paths/doc mentions to IDs
    related_ids = set()
    for rel in found_rels:
        # If it's already an ID (e.g. ADR-0001), use it
        if rel in all_doc_ids:
            related_ids.add(rel)
        elif rel.startswith('ADR-') or rel.startswith('CL-'):
             # Loose match for ADR-XXXX or CL-XXXX
             related_ids.add(rel)
        else:
            # Try to convert path to ID
            try:
                doc_id = extract_doc_id_from_path(rel)
                if doc_id in all_doc_ids:
                    related_ids.add(doc_id)
            except:
                continue

    # Skip self-reference
    current_id = metadata.get('id')
    if current_id in related_ids:
        related_ids.remove(current_id)

    # Merge Dependencies
    current_deps = metadata.get('dependencies', [])
    if not isinstance(current_deps, list): current_deps = []
    updated_deps = sorted(list(set(current_deps + found_deps)))

    # Merge Relationships
    current_relates = metadata.get('relates_to', [])
    if not isinstance(current_relates, list): current_relates = []
    updated_relates = sorted(list(set(current_relates + list(related_ids))))

    # Check for changes
    changed = False
    if set(current_deps) != set(updated_deps):
        metadata['dependencies'] = updated_deps
        changed = True

    if set(current_relates) != set(updated_relates):
        metadata['relates_to'] = updated_relates
        changed = True

    if not changed:
        return False

    if dry_run:
        print(f"🔍 Would update {file_path}")
        return True

    if write_metadata(file_path, metadata, rest_of_file):
        print(f"✅ Updated {file_path}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Extract and populate document relationships')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--verbose', action='store_true', help='Show all files including skipped ones')
    args = parser.parse_args()

    # Find all markdown files
    all_md_files = []
    for pattern in ['docs/**/*.md', 'ci-workflows/**/*.md', 'apps/**/*.md', 'bootstrap/**/*.md',
                    'modules/**/*.md', 'gitops/**/*.md', 'idp-tooling/**/*.md', 'envs/**/*.md',
                    'compliance/**/*.md', '*.md']:
        all_md_files.extend(glob.glob(pattern, recursive=True))

    # Remove duplicates
    all_md_files = sorted(set(all_md_files))

    # Build index of all doc IDs
    all_doc_ids = set()
    for f in all_md_files:
        doc_id = extract_doc_id_from_path(f)
        all_doc_ids.add(doc_id)

    print(f"Found {len(all_md_files)} markdown files")
    print(f"Indexed {len(all_doc_ids)} document IDs")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)

    updated_count = 0
    skipped_count = 0

    for filepath in all_md_files:
        if process_file(filepath, all_doc_ids, dry_run=args.dry_run, verbose=args.verbose):
            updated_count += 1
        else:
            skipped_count += 1

    print("=" * 60)
    print(f"✅ Updated: {updated_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"📊 Total: {len(all_md_files)}")

    if args.dry_run:
        print("\n🔍 This was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\n✅ Relationship extraction complete!")
        print("   Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Validate: python3 scripts/validate_metadata.py docs")
        print("   3. Commit: git add . && git commit -m 'docs: add document relationships'")


if __name__ == '__main__':
    main()
