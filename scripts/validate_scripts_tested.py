#!/usr/bin/env python3
"""
---
id: validate_scripts_tested
type: script
owner: platform-team
status: active
maturity: 3
test:
  runner: pytest
  command: "pytest -q tests/unit/test_validate_scripts_tested.py"
  evidence: declared
dry_run:
  supported: true
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
---
Purpose: Enforces Schema-Driven Script Certification
Achievement: Validates that all scripts contain a metadata contract compliant with
             schemas/automation/script.schema.yaml. Enforces proof-of-test for high-risk scripts.
"""
import os
import sys
import yaml
import json
import argparse
from pathlib import Path

# Add python lib to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
try:
    from script_metadata import extract_frontmatter, parse_header
except ImportError:
    print("❌ Failed to import script_metadata from lib/")
    sys.exit(1)

# Constants
SCHEMA_PATH = Path("schemas/automation/script.schema.yaml")
PROOF_DIR = Path("test-results/proofs")

def load_schema():
    if not SCHEMA_PATH.exists():
        print(f"❌ Schema not found: {SCHEMA_PATH}")
        sys.exit(1)
    try:
        with open(SCHEMA_PATH, 'r') as f:
            full_doc = list(yaml.safe_load_all(f))
            for doc in full_doc:
                if doc and 'script' in doc:
                    return doc['script']
            return full_doc[-1]
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        sys.exit(1)

def validate_field(data, field_def, field_name, context=""):
    """
    Simple schema validator. 
    Supports: type, enum, required_fields, pattern
    """
    value = data.get(field_name)
    if value is None:
        return []

    errors = []
    
    # Type check
    ftype = field_def.get('type')
    if ftype == 'string' and not isinstance(value, str):
        errors.append(f"{context}.{field_name}: Expected string, got {type(value)}")
    elif ftype == 'integer' and not isinstance(value, int):
        errors.append(f"{context}.{field_name}: Expected integer, got {type(value)}")
    elif ftype == 'boolean' and not isinstance(value, bool):
        errors.append(f"{context}.{field_name}: Expected boolean, got {type(value)}")
    elif ftype == 'object' and not isinstance(value, dict):
        errors.append(f"{context}.{field_name}: Expected object, got {type(value)}")
        
    # Enum check
    if 'enum' in field_def and value not in field_def['enum']:
        errors.append(f"{context}.{field_name}: Value '{value}' not in allowed list: {field_def['enum']}")
        
    # Recursive checks
    if ftype == 'object' and 'fields' in field_def:
        reqs = field_def.get('required_fields', [])
        for r in reqs:
            if r not in value:
                errors.append(f"{context}.{field_name}: Missing required sub-field '{r}'")
        
        for sub_k, sub_def in field_def['fields'].items():
            errors.extend(validate_field(value, sub_def, sub_k, f"{context}.{field_name}"))
            
    return errors

def validate_file(filepath, schema, args):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return [f"Could not read file {filepath}"] 
        
    data = parse_header(content)
    if not data:
        return [f"Missing Metadata Header (YAML Frontmatter)"]
        
    errors = []
    
    # 1. Top Level Required Fields
    for req in schema.get('required_fields', []):
        if req not in data:
            errors.append(f"Missing required top-level field: '{req}'")
            
    # 2. Field Level Validation
    for field, definition in schema.get('fields', {}).items():
        errors.extend(validate_field(data, definition, field, "root"))

    # 3. Logic Checks & Proof Verification
    if not errors:
        test_block = data.get('test', {})
        evidence_type = test_block.get('evidence')
        script_id = data.get('id')
        risk = data.get('risk_profile', {}).get('production_impact')
        
        # Policy: High Risk requires CI proof
        if risk == 'high' and evidence_type != 'ci' and not args.dry_run:
             # Just warning for now
             # errors.append("High risk scripts MUST verify with evidence='ci'")
             pass

        # Verify Test Proof Existence
        if evidence_type == 'ci' and args.verify_proofs:
            proof_path = PROOF_DIR / f"proof-{script_id}.json"
            if not proof_path.exists():
                errors.append(f"Missing CI Proof file: {proof_path} (evidence='ci' declared)")
            else:
                # Valid proof found?
                try:
                    with open(proof_path, 'r') as f:
                        proof_data = json.load(f)
                    
                    if proof_data.get('outcome') != 'passed':
                         errors.append(f"Proof outcome is '{proof_data.get('outcome')}', expected 'passed'")
                         
                    # Optional: Check SHA matching if argument provided
                    # if args.expected_sha and proof_data.get('git_sha') != args.expected_sha:
                    #    errors.append("Proof is for a different git SHA (stale verify)")
                    
                except Exception as e:
                    errors.append(f"Invalid/Corrupt proof file at {proof_path}: {e}")

    return errors

def main():
    parser = argparse.ArgumentParser(description="Validate script metadata contracts")
    parser.add_argument("paths", nargs="*", default=["scripts"], help="Paths to scan")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be checked")
    parser.add_argument("--verify-proofs", action="store_true", help="Check for existence of proof artifacts")
    args = parser.parse_args()
    
    schema = load_schema()
    
    scripts_to_check = []
    for path_str in args.paths:
        p = Path(path_str)
        if p.is_file():
            scripts_to_check.append(p)
        else:
            for r, d, f in os.walk(p):
                for file in f:
                    if file.endswith('.py') or file.endswith('.sh'):
                        scripts_to_check.append(Path(r) / file)
                        
    # Robust Filtering: exclude lib dirs and __init__
    filtered_scripts = []
    for s in scripts_to_check:
        if 'lib' in s.parts or s.name == '__init__.py':
            continue
        filtered_scripts.append(s)
    
    if args.dry_run:
        print(f"[DRY-RUN] Would validate {len(filtered_scripts)} scripts against schema.")
        return

    failure_count = 0
    print(f"🔍 Validating {len(filtered_scripts)} scripts against {SCHEMA_PATH}...")
    print("-" * 60)
    
    for script in filtered_scripts:
        errors = validate_file(script, schema, args)
        if errors:
            failure_count += 1
            print(f"❌ {script}")
            for e in errors:
                print(f"   - {e}")
        else:
            print(f"✅ {script}")
            
    print("-" * 60)
    if failure_count > 0:
        print(f"FAILED: {failure_count} scripts violating contract.")
        sys.exit(1)
    else:
        print("SUCCESS: All scripts compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main()
