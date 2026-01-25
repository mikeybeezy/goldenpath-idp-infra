# AGENT_CONTEXT: Read .agent/README.md for rules
#!/usr/bin/env python3
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

"""
Purpose: Automated Relationship & Dependency Extractor (Bidirectional)
Achievement: Scans content for ADR/CL/RB/PRD/EC/US mentions, Markdown links, and dependency
             prefixes to programmatically wire together the Platform Knowledge Graph.
             Implements bidirectional linking: if A references B, both A and B get updated.
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

# Prefixes for short ID patterns (ADR-0001, CL-0042, RB-0031, etc.)
SHORT_ID_PREFIXES = ("ADR", "CL", "PRD", "RB", "EC", "US")


def extract_doc_id_from_path(file_path):
    """Convert file path to document ID when no frontmatter is present."""
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

    # Pattern 2: ADR/CL/RB/PRD/EC/US mentions (e.g. ADR-0026, CL-0042, RB-0031)
    for prefix in SHORT_ID_PREFIXES:
        mentions = re.findall(rf'\b({prefix}-\d{{4}})\b', content)
        relationships.update(mentions)

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


def build_short_id_map(all_doc_ids):
    """Map short IDs (e.g., ADR-0001) to full document IDs."""
    short_map = defaultdict(list)
    pattern = re.compile(rf"^({'|'.join(SHORT_ID_PREFIXES)})-\d{{4}}")
    for doc_id in all_doc_ids:
        match = pattern.match(doc_id)
        if match:
            short = doc_id.split("-", 2)[:2]
            short_id = "-".join(short)
            short_map[short_id].append(doc_id)
    return short_map


def normalize_reference(ref, all_doc_ids, short_id_map, file_id_map):
    """Resolve a reference into canonical doc IDs (no path refs)."""
    resolved = set()
    if not ref:
        return resolved

    if ref in all_doc_ids:
        resolved.add(ref)
        return resolved

    slug_match = re.match(rf"^({'|'.join(SHORT_ID_PREFIXES)})-\d{{4}}-", ref)
    if slug_match:
        short = "-".join(ref.split("-", 2)[:2])
        if short in short_id_map and len(short_id_map[short]) == 1:
            resolved.update(short_id_map[short])
            return resolved

    if ref in short_id_map:
        if len(short_id_map[ref]) == 1:
            resolved.update(short_id_map[ref])
        return resolved

    if "/" in ref or ref.endswith(".md"):
        try:
            ref_path = os.path.normpath(ref)
            if ref_path.startswith("./"):
                ref_path = ref_path[2:]
            doc_id = file_id_map.get(ref_path)
            if doc_id:
                resolved.add(doc_id)
                return resolved
            fallback_id = extract_doc_id_from_path(ref_path)
            if fallback_id in all_doc_ids:
                resolved.add(fallback_id)
        except Exception:
            pass
        return resolved

    return resolved


def normalize_relates(relates, all_doc_ids, short_id_map, file_id_map):
    """Normalize existing relates_to entries to IDs only."""
    normalized = set()
    short_pattern = re.compile(rf"^({'|'.join(SHORT_ID_PREFIXES)})-\d{{4}}$")
    slug_pattern = re.compile(rf"^({'|'.join(SHORT_ID_PREFIXES)})-\d{{4}}-")
    for ref in relates:
        if not isinstance(ref, str):
            continue
        if slug_pattern.match(ref):
            short = "-".join(ref.split("-", 2)[:2])
            if short in short_id_map and len(short_id_map[short]) == 1:
                normalized.update(short_id_map[short])
                continue
        if ref in short_id_map:
            if len(short_id_map[ref]) == 1:
                normalized.update(short_id_map[ref])
            continue
        if short_pattern.match(ref):
            if ref in short_id_map and len(short_id_map[ref]) == 1:
                normalized.update(short_id_map[ref])
            else:
                normalized.add(ref)
            continue
        if "/" in ref or ref.endswith(".md"):
            normalized.update(normalize_reference(ref, all_doc_ids, short_id_map, file_id_map))
            continue
        if ref in all_doc_ids:
            normalized.add(ref)
        else:
            normalized.add(ref)
    return normalized


def extract_file_references(file_path, all_doc_ids, short_id_map, file_id_map):
    """Extract forward references from a file. Returns (doc_id, related_ids, deps) or None."""
    metadata, rest_of_file = read_metadata(file_path)

    if metadata is None:
        return None

    current_id = metadata.get('id')
    if not current_id:
        return None

    # Extract relationships and dependencies from content
    with open(file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()

    found_rels, found_deps = extract_metadata_fields(full_content, file_path)

    # Convert relative paths/doc mentions to IDs
    related_ids = set()
    for rel in found_rels:
        related_ids.update(normalize_reference(rel, all_doc_ids, short_id_map, file_id_map))

    # Skip self-reference
    if current_id in related_ids:
        related_ids.remove(current_id)

    return (current_id, related_ids, found_deps, metadata, rest_of_file)


def process_file_with_backlinks(file_path, all_doc_ids, short_id_map, file_id_map, reverse_graph,
                                 dry_run=False, verbose=False):
    """Process a single file with both forward refs and backlinks from reverse_graph."""
    metadata, rest_of_file = read_metadata(file_path)

    if metadata is None:
        return False

    current_id = metadata.get('id')
    if not current_id:
        return False

    # Extract forward relationships and dependencies
    with open(file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()

    found_rels, found_deps = extract_metadata_fields(full_content, file_path)

    # Convert relative paths/doc mentions to IDs (forward refs)
    forward_ids = set()
    for rel in found_rels:
        forward_ids.update(normalize_reference(rel, all_doc_ids, short_id_map, file_id_map))

    # Skip self-reference
    if current_id in forward_ids:
        forward_ids.remove(current_id)

    # Get backlinks (docs that reference this doc)
    backlink_ids = reverse_graph.get(current_id, set())

    # Combine forward + backward relationships
    all_related_ids = forward_ids | backlink_ids

    # Merge Dependencies
    current_deps = metadata.get('dependencies', [])
    if not isinstance(current_deps, list):
        current_deps = []
    updated_deps = sorted(list(set(current_deps + found_deps)))

    # Merge Relationships (normalize existing + add new)
    current_relates = metadata.get('relates_to', [])
    if not isinstance(current_relates, list):
        current_relates = []
    normalized_relates = normalize_relates(current_relates, all_doc_ids, short_id_map, file_id_map)
    updated_relates = sorted(list(set(normalized_relates | all_related_ids)))

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
        added_forward = forward_ids - normalized_relates
        added_backlinks = backlink_ids - normalized_relates
        if added_forward or added_backlinks:
            print(f"🔍 Would update {file_path}")
            if added_forward:
                print(f"   + forward: {sorted(added_forward)}")
            if added_backlinks:
                print(f"   + backlinks: {sorted(added_backlinks)}")
        else:
            print(f"🔍 Would update {file_path} (normalization only)")
        return True

    if write_metadata(file_path, metadata, rest_of_file):
        print(f"✅ Updated {file_path}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Extract and populate document relationships (bidirectional)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--verbose', action='store_true', help='Show all files including skipped ones')
    parser.add_argument('--no-backlinks', action='store_true', help='Skip bidirectional backlink population')
    args = parser.parse_args()

    # Find all markdown files
    all_md_files = []
    for pattern in ['docs/**/*.md', 'ci-workflows/**/*.md', 'apps/**/*.md', 'bootstrap/**/*.md',
                    'modules/**/*.md', 'gitops/**/*.md', 'idp-tooling/**/*.md', 'envs/**/*.md',
                    'compliance/**/*.md', 'session_summary/**/*.md', 'session_capture/**/*.md', '*.md']:
        all_md_files.extend(glob.glob(pattern, recursive=True))

    # Remove duplicates
    all_md_files = sorted(set(all_md_files))

    # Build index of all doc IDs and map files to IDs (prefer frontmatter IDs)
    all_doc_ids = set()
    id_to_file = {}
    file_id_map = {}
    for f in all_md_files:
        metadata, _ = read_metadata(f)
        doc_id = None
        if metadata and metadata.get('id'):
            doc_id = str(metadata.get('id')).strip()
        if not doc_id:
            doc_id = extract_doc_id_from_path(f)
        file_id_map[os.path.normpath(f)] = doc_id
        all_doc_ids.add(doc_id)
        id_to_file[doc_id] = f
    short_id_map = build_short_id_map(all_doc_ids)

    print(f"Found {len(all_md_files)} markdown files")
    print(f"Indexed {len(all_doc_ids)} document IDs")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Backlinks: {'DISABLED' if args.no_backlinks else 'ENABLED'}")
    print("=" * 60)

    # PASS 1: Extract all forward references to build the graph
    print("Pass 1: Extracting forward references...")
    forward_graph = {}  # doc_id -> set of referenced doc_ids

    for filepath in all_md_files:
        result = extract_file_references(filepath, all_doc_ids, short_id_map, file_id_map)
        if result:
            doc_id, related_ids, _, _, _ = result
            # Only include references to docs that actually exist
            valid_refs = {ref for ref in related_ids if ref in all_doc_ids}
            if valid_refs:
                forward_graph[doc_id] = valid_refs

    print(f"   Found {len(forward_graph)} documents with outgoing references")
    total_edges = sum(len(refs) for refs in forward_graph.values())
    print(f"   Total forward edges: {total_edges}")

    # PASS 2: Build reverse graph (backlinks)
    reverse_graph = defaultdict(set)  # doc_id -> set of docs that reference it

    if not args.no_backlinks:
        print("Pass 2: Computing backlinks...")
        for source_id, target_ids in forward_graph.items():
            for target_id in target_ids:
                if target_id in all_doc_ids:
                    reverse_graph[target_id].add(source_id)

        docs_with_backlinks = sum(1 for refs in reverse_graph.values() if refs)
        total_backlinks = sum(len(refs) for refs in reverse_graph.values())
        print(f"   Found {docs_with_backlinks} documents with incoming backlinks")
        print(f"   Total backlink edges: {total_backlinks}")
    else:
        print("Pass 2: Skipped (--no-backlinks)")

    # PASS 3: Update files with combined forward + reverse relationships
    print("Pass 3: Updating documents...")
    print("=" * 60)

    updated_count = 0
    skipped_count = 0

    for filepath in all_md_files:
        if process_file_with_backlinks(filepath, all_doc_ids, short_id_map, file_id_map, reverse_graph,
                                       dry_run=args.dry_run, verbose=args.verbose):
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
        print("\n✅ Bidirectional relationship extraction complete!")
        print("   Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Validate: python3 scripts/validate_metadata.py docs")
        print("   3. Commit: git add . && git commit -m 'docs: add bidirectional document relationships'")


if __name__ == '__main__':
    main()
