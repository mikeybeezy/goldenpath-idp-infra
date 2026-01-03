#!/usr/bin/env python3
import os
import sys
import yaml
import re

REQUIRED_FIELDS = ['id', 'type', 'owner', 'status']
OPTIONAL_FIELDS = ['risk_profile', 'lifecycle', 'relates_to', 'title', 'domain']

def parse_frontmatter(filepath):
    """
    Extracts and parses YAML frontmatter from a markdown file.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    # Frontmatter must start on line 1 with ---
    if not content.startswith('---'):
        return None, "Missing frontmatter (must start with ---)"

    try:
        # Extract content between first and second ---
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return None, "Malformed or unterminated frontmatter"
        
        data = yaml.safe_load(frontmatter_match.group(1))
        return data, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML: {e}"

def validate_schema(data, filepath):
    """
    Validates the parsed frontmatter against the schema.
    """
    errors = []
    
    # 1. Check Required Fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
    
    # 2. Start-Specific Checks (Optimization: Only check id format if present)
    if 'id' in data:
        # Check ID matches filename (roughly)
        filename = os.path.basename(filepath)
        doc_id = data['id']
        if doc_id not in filename:
             # Loose check: ID must be part of filename (e.g. ADR-0066 inside ADR-0066-title.md)
             errors.append(f"ID mismatch: '{doc_id}' found in header but filename is '{filename}'")

    if 'owner' in data:
        if not data['owner']:
             errors.append("Owner field cannot be empty")

    return errors

def scan_directory(root_dir):
    """
    Scans docs directory for markdown files and validates them.
    """
    fail_count = 0
    pass_count = 0
    
    print(f"🔍 Scanning {root_dir} for metadata compliance...")

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md') and not file == 'DOC_INDEX.md': # Skip index
                filepath = os.path.join(root, file)
                
                # Check if it SHOULD have metadata (ADRs, Changelogs, Policies)
                if 'adrs/' in filepath or 'changelog/entries/' in filepath or 'governance/' in filepath:
                    data, error = parse_frontmatter(filepath)
                    
                    if error:
                        # Warning only for now, as we are backfilling
                        print(f"⚠️  [MISSING] {filepath}: {error}")
                        # fail_count += 1 
                        continue
                    
                    validation_errors = validate_schema(data, filepath)
                    if validation_errors:
                        print(f"❌ [INVALID] {filepath}")
                        for err in validation_errors:
                            print(f"   - {err}")
                        fail_count += 1
                    else:
                        pass_count += 1

    print("-" * 40)
    print(f"✅ Passed: {pass_count}")
    print(f"❌ Failed: {fail_count}")
    
    if fail_count > 0:
        return 1
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        target_dir = "docs"
    else:
        target_dir = sys.argv[1]
        
    sys.exit(scan_directory(target_dir))
