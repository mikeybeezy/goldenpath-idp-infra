#!/usr/bin/env python3
"""
Relationship Extraction Script

Extracts document relationships from content and updates metadata `relates_to` fields.

Usage:
    python3 scripts/extract-relationships.py [--dry-run] [--verbose]
"""

import os
import re
import glob
import yaml
import argparse
from collections import defaultdict


def extract_doc_id_from_path(file_path):
    """Convert file path to document ID"""
    # Remove .md extension
    path = file_path.replace('.md', '')
    
    # Extract ID from common patterns
    basename = os.path.basename(path)
    
    # ADR files: ADR-0026-title → ADR-0026
    if basename.startswith('ADR-'):
        return basename.split('-')[0] + '-' + basename.split('-')[1]
    
    # Changelog: CL-0042-title → CL-0042
    if basename.startswith('CL-'):
        return basename.split('-')[0] + '-' + basename.split('-')[1]
    
    # Numbered files: 21_CI_ENVIRONMENT → 21_CI_ENVIRONMENT
    if re.match(r'^\d+_', basename):
        return basename
    
    # README files: use parent directory name
    if basename == 'README':
        parent = os.path.basename(os.path.dirname(file_path))
        return parent.upper()
    
    # Default: use basename
    return basename.replace('-', '_').upper()


def extract_relationships_from_content(content, current_file):
    """Extract relationship references from document content"""
    relationships = set()
    
    # Pattern 1: "Related:" field in doc contract
    # Example: - Related: docs/adrs/ADR-0026.md, docs/40-delivery/12_GITOPS.md
    related_match = re.search(r'- Related:\s*([^\n]+)', content, re.IGNORECASE)
    if related_match:
        related_text = related_match.group(1)
        # Split by comma and extract file paths
        refs = [r.strip() for r in related_text.split(',')]
        for ref in refs:
            # Extract file path from reference
            path_match = re.search(r'(docs/[^\s,)]+\.md|[^\s/]+/[^\s,)]+\.md)', ref)
            if path_match:
                relationships.add(path_match.group(1))
    
    # Pattern 2: Inline `docs/...` references
    # Example: See `docs/adrs/ADR-0033-platform-ci-orchestrated-modes.md`
    inline_refs = re.findall(r'`(docs/[^`]+\.md)`', content)
    relationships.update(inline_refs)
    
    # Pattern 3: ADR mentions
    # Example: "ADR-0047" or "see ADR-0047"
    adr_mentions = re.findall(r'\bADR-(\d{4})\b', content)
    for adr_num in adr_mentions:
        relationships.add(f'docs/adrs/ADR-{adr_num}')
    
    # Pattern 4: Markdown links to local files
    # Example: [link](../adrs/ADR-0026.md)
    md_links = re.findall(r'\]\(([^)]+\.md)\)', content)
    for link in md_links:
        # Resolve relative paths
        if link.startswith('../') or link.startswith('./'):
            # Try to resolve relative to current file
            current_dir = os.path.dirname(current_file)
            resolved = os.path.normpath(os.path.join(current_dir, link))
            relationships.add(resolved)
        elif link.startswith('docs/'):
            relationships.add(link)
    
    # Pattern 5: ci-workflows references
    ci_workflow_refs = re.findall(r'`(ci-workflows/[^`]+\.md)`', content)
    relationships.update(ci_workflow_refs)
    
    # Pattern 6: apps/ references
    app_refs = re.findall(r'`(apps/[^`]+\.md)`', content)
    relationships.update(app_refs)
    
    # Pattern 7: Changelog mentions
    # Example: "CL-0042" or "see CL-0042"
    cl_mentions = re.findall(r'\bCL-(\d{4})\b', content)
    for cl_num in cl_mentions:
        relationships.add(f'docs/changelog/entries/CL-{cl_num}')
    
    # Pattern 8: policies/ references
    policy_refs = re.findall(r'`(docs/[^`]*policies[^`]+\.md)`', content)
    relationships.update(policy_refs)
    
    # Pattern 9: governance/ references  
    gov_refs = re.findall(r'`(docs/10-governance/[^`]+\.md)`', content)
    relationships.update(gov_refs)
    
    # Pattern 10: contracts/ references
    contract_refs = re.findall(r'`(docs/20-contracts/[^`]+\.md)`', content)
    relationships.update(contract_refs)
    
    # Pattern 11: runbooks/ references
    runbook_refs = re.findall(r'`(docs/runbooks/[^`]+\.md)`', content)
    relationships.update(runbook_refs)
    
    # Pattern 12: PR references
    # Example: "PR #107" or "#123"
    pr_mentions = re.findall(r'\bPR\s*#(\d+)', content, re.IGNORECASE)
    for pr_num in pr_mentions:
        relationships.add(f'PR-{pr_num}')
    
    # Pattern 13: GitHub workflow files
    # Example: `.github/workflows/pr-labeler.yml`
    workflow_refs = re.findall(r'`(\.github/workflows/[^`]+\.ya?ml)`', content)
    for wf in workflow_refs:
        # Convert to identifier: .github/workflows/pr-labeler.yml → workflow:pr-labeler
        wf_name = os.path.basename(wf).replace('.yml', '').replace('.yaml', '')
        relationships.add(f'workflow:{wf_name}')
    
    return relationships


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
        rest_of_file = '---'.join(['', parts[2]])
        
        return metadata, rest_of_file
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, None


def write_metadata(file_path, metadata, content):
    """Write updated metadata back to file"""
    try:
        # Serialize metadata to YAML
        yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(yaml_str)
            f.write('---')
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False


def process_file(file_path, all_doc_ids, dry_run=False, verbose=False):
    """Process a single file to extract and update relationships"""
    
    # Read metadata
    metadata, content = read_metadata(file_path)
    
    if metadata is None:
        if verbose:
            print(f"⏭️  {file_path} (no metadata)")
        return False
    
    # Read full content for relationship extraction
    with open(file_path, 'r') as f:
        full_content = f.read()
    
    # Extract relationships
    relationships = extract_relationships_from_content(full_content, file_path)
    
    if not relationships:
        if verbose:
            print(f"⏭️  {file_path} (no relationships found)")
        return False
    
    # Convert file paths to IDs
    related_ids = set()
    for rel_path in relationships:
        # Normalize path
        rel_path = rel_path.strip()
        
        # Skip self-references
        if os.path.normpath(rel_path) == os.path.normpath(file_path):
            continue
        
        # Convert to ID
        try:
            doc_id = extract_doc_id_from_path(rel_path)
            
            # Validate ID exists in our repository
            if doc_id in all_doc_ids or doc_id.startswith('ADR-') or doc_id.startswith('CL-'):
                related_ids.add(doc_id)
        except:
            if verbose:
                print(f"  Warning: Could not convert {rel_path} to ID")
    
    if not related_ids:
        if verbose:
            print(f"⏭️  {file_path} (no valid IDs after conversion)")
        return False
    
    # Update metadata
    current_relates = metadata.get('relates_to', [])
    
    # Convert to list if needed
    if not isinstance(current_relates, list):
        current_relates = []
    
    # Merge with existing relationships
    updated_relates = sorted(set(current_relates + list(related_ids)))
    
    # Check if anything changed
    if set(current_relates) == set(updated_relates):
        if verbose:
            print(f"⏭️  {file_path} (relationships unchanged)")
        return False
    
    if dry_run:
        print(f"🔍 Would update {file_path}:")
        print(f"   Current: {current_relates}")
        print(f"   Updated: {updated_relates}")
        return True
    
    # Update metadata
    metadata['relates_to'] = updated_relates
    
    # Write back
    if write_metadata(file_path, metadata, content):
        print(f"✅ {file_path}")
        print(f"   Added {len(updated_relates) - len(current_relates)} relationships: {updated_relates}")
        return True
    else:
        print(f"❌ Failed to write {file_path}")
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
        print("   2. Validate: python3 scripts/validate-metadata.py docs")
        print("   3. Commit: git add . && git commit -m 'docs: add document relationships'")


if __name__ == '__main__':
    main()
