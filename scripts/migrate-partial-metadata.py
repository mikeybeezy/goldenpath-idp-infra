#!/usr/bin/env python3
"""
Migrate partial metadata to enhanced schema

Adds missing category, version, dependencies fields to files that have
old metadata schema.
"""

import os
import glob
import yaml
import re


def extract_category(filepath):
    """Extract category from directory structure"""
    if '/docs/' in filepath:
        match = re.search(r'docs/(\d+-[^/]+)', filepath)
        if match:
            return match.group(1)
        return 'docs-root'
    
    parts = filepath.split('/')
    if len(parts) > 1:
        return parts[0]
    return 'root'


def read_file(filepath):
    """Read file and split frontmatter from content"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return None, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    
    try:
        metadata = yaml.safe_load(parts[1])
        rest = '---'.join(['', parts[2]])
        return metadata, rest
    except:
        return None, content


def write_file(filepath, metadata, content):
    """Write updated metadata back to file"""
    # Remove duplicate keys
    if 'status' in metadata and isinstance(metadata.get('status'), list):
        metadata['status'] = metadata['status'][0]
    
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    with open(filepath, 'w') as f:
        f.write('---\n')
        f.write(yaml_str)
        f.write('---')
        f.write(content)


def needs_migration(metadata):
    """Check if metadata needs migration"""
    if not metadata:
        return False
    
    # Check for missing fields
    missing_fields = []
    if 'category' not in metadata:
        missing_fields.append('category')
    if 'version' not in metadata:
        missing_fields.append('version')
    if 'dependencies' not in metadata:
        missing_fields.append('dependencies')
    
    return len(missing_fields) > 0


def migrate_file(filepath):
    """Migrate a single file"""
    metadata, content = read_file(filepath)
    
    if not needs_migration(metadata):
        return False
    
    # Add missing fields
    if 'category' not in metadata:
        metadata['category'] = extract_category(filepath)
    
    if 'version' not in metadata:
        metadata['version'] = '1.0'
    
    if 'dependencies' not in metadata:
        metadata['dependencies'] = []
    
    # Fix field order
    ordered_metadata = {}
    field_order = ['id', 'title', 'type', 'category', 'version', 'owner', 'status', 'dependencies', 
                   'risk_profile', 'reliability', 'lifecycle', 'relates_to']
    
    for field in field_order:
        if field in metadata:
            ordered_metadata[field] = metadata[field]
    
    # Add any remaining fields
    for key, value in metadata.items():
        if key not in ordered_metadata:
            ordered_metadata[key] = value
    
    write_file(filepath, ordered_metadata, content)
    return True


def main():
    # Find all markdown files
    patterns = [
        'modules/**/*.md',
        'apps/**/*.md',
        'envs/**/*.md',
        'gitops/**/*.md',
        'idp-tooling/**/*.md',
        'bootstrap/**/*.md',
        'compliance/**/*.md'
    ]
    
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    all_files = sorted(set(all_files))
    
    print(f"Found {len(all_files)} files to check")
    
    migrated = 0
    skipped = 0
    
    for filepath in all_files:
        if migrate_file(filepath):
            print(f"✅ Migrated: {filepath}")
            migrated += 1
        else:
            skipped += 1
    
    print(f"\n✅ Migrated: {migrated}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"📊 Total: {len(all_files)}")


if __name__ == '__main__':
    main()
