#!/usr/bin/env python3
"""
Metadata Backfill Script

Automatically adds YAML frontmatter metadata to all markdown files
in the docs/ directory that don't already have it.

Usage:
    python3 scripts/backfill-metadata.py [--dry-run] [--verbose]
"""

import os
import re
import glob
import argparse
from datetime import datetime, timedelta


def get_title_from_file(filepath):
    """Extract title from first # heading in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    return line.lstrip('#').strip()
        # Fallback to filename
        basename = os.path.basename(filepath).replace('.md', '')
        return basename.replace('_', ' ').replace('-', ' ').title()
    except Exception as e:
        print(f"Warning: Could not extract title from {filepath}: {e}")
        basename = os.path.basename(filepath).replace('.md', '')
        return basename.replace('_', ' ').replace('-', ' ').title()


def determine_doc_type(filepath):
    """Determine document type based on file location and name"""
    if '/adrs/' in filepath or filepath.endswith('adr_template.md'):
        return 'adr'
    elif '/changelog/' in filepath and '/entries/' in filepath:
        return 'changelog'
    elif '/changelog/' in filepath:
        return 'documentation'
    elif '/contracts/' in filepath:
        return 'contract'
    elif '/runbooks/' in filepath:
        return 'runbook'
    elif '/policies/' in filepath:
        return 'policy'
    elif '/operations/' in filepath:
        return 'runbook'
    elif '/security/' in filepath:
        return 'policy'
    elif 'TEMPLATE' in filepath or 'template' in filepath:
        return 'template'
    else:
        return 'documentation'


def get_id_from_filepath(filepath):
    """Extract ID from filepath"""
    basename = os.path.basename(filepath).replace('.md', '')
    
    # Changelog entries
    if '/changelog/entries/' in filepath and basename.startswith('CL-'):
        return basename.split('-')[0] + '-' + basename.split('-')[1]
    
    # ADRs
    if '/adrs/' in filepath and basename.startswith('ADR-'):
        return basename.split('-')[0] + '-' + basename.split('-')[1]
    
    # Default: use basename
    return basename


def get_lifecycle_date(filepath, doc_type):
    """Calculate appropriate lifecycle date based on doc type"""
    if doc_type == 'changelog':
        # Changelogs: 1 year from now
        return (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    elif doc_type == 'adr':
        # ADRs: 2 years from now
        return (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d')
    else:
        # Everything else: 2028-01-01
        return '2028-01-01'


def get_risk_profile(doc_type):
    """Get appropriate risk profile based on document type"""
    if doc_type == 'contract':
        return {
            'production_impact': 'high',
            'security_risk': 'none',
            'coupling_risk': 'high'
        }
    elif doc_type == 'policy':
        return {
            'production_impact': 'medium',
            'security_risk': 'access',
            'coupling_risk': 'medium'
        }
    elif doc_type == 'runbook':
        return {
            'production_impact': 'medium',
            'security_risk': 'access',
            'coupling_risk': 'low'
        }
    else:
        return {
            'production_impact': 'low',
            'security_risk': 'none',
            'coupling_risk': 'low'
        }


def get_observability_tier(doc_type):
    """Get observability tier based on document type"""
    if doc_type in ['contract', 'policy']:
        return 'gold'
    elif doc_type in ['adr', 'runbook']:
        return 'silver'
    else:
        return 'bronze'


def generate_metadata(filepath, title, doc_type):
    """Generate YAML frontmatter metadata for a file"""
    doc_id = get_id_from_filepath(filepath)
    lifecycle_date = get_lifecycle_date(filepath, doc_type)
    risk_profile = get_risk_profile(doc_type)
    obs_tier = get_observability_tier(doc_type)
    
    # Quote title if it contains special characters
    if ':' in title and not title.startswith('"'):
        title = f'"{title}"'
    
    metadata = f"""---
id: {doc_id}
title: {title}
type: {doc_type}
owner: platform-team
status: active
risk_profile:
  production_impact: {risk_profile['production_impact']}
  security_risk: {risk_profile['security_risk']}
  coupling_risk: {risk_profile['coupling_risk']}
reliability:
  rollback_strategy: git-revert
  observability_tier: {obs_tier}
lifecycle:
  supported_until: {lifecycle_date}
  breaking_change: false
relates_to: []
---

"""
    return metadata


def has_frontmatter(filepath):
    """Check if file already has YAML frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return content.startswith('---')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return True  # Skip on error


def add_metadata_to_file(filepath, dry_run=False, verbose=False):
    """Add metadata to a single file"""
    if has_frontmatter(filepath):
        if verbose:
            print(f"⏭️  {filepath} (already has metadata)")
        return False
    
    try:
        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate metadata
        title = get_title_from_file(filepath)
        doc_type = determine_doc_type(filepath)
        metadata = generate_metadata(filepath, title, doc_type)
        
        if dry_run:
            print(f"🔍 Would add metadata to: {filepath}")
            print(f"   ID: {get_id_from_filepath(filepath)}, Type: {doc_type}")
            return True
        
        # Write new content
        new_content = metadata + content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Backfill metadata to markdown files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--verbose', action='store_true', help='Show all files including skipped ones')
    args = parser.parse_args()
    
    # Find all markdown files in the repository (excluding .gemini and node_modules)
    all_md_files = []
    for pattern in ['**/*.md', '*.md']:
        all_md_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out excluded directories
    excluded_paths = ['.gemini', 'node_modules', '.git']
    all_md_files = [f for f in all_md_files if not any(exc in f for exc in excluded_paths)]
    
    # Remove duplicates and sort
    all_md_files = sorted(set(all_md_files))
    
    print(f"Found {len(all_md_files)} markdown files in repository")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    
    updated_count = 0
    skipped_count = 0
    
    for filepath in all_md_files:
        if add_metadata_to_file(filepath, dry_run=args.dry_run, verbose=args.verbose):
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
        print("\n✅ Metadata backfill complete!")
        print("   Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Validate: python3 scripts/validate-metadata.py docs")
        print("   3. Commit: git add . && git commit -m 'docs: complete metadata backfill'")


if __name__ == '__main__':
    main()
