#!/usr/bin/env python3
"""
Scaffold Test Utility
Standardize the creation of test structures to make testing a forethought.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = REPO_ROOT / "tests" / "templates"
UNIT_TEST_DIR = REPO_ROOT / "tests" / "unit"
FEATURE_TEST_DIR = REPO_ROOT / "tests" / "features"

def scaffold_unit_test(script_path):
    """Create a unit test boilerplate for a given script."""
    script_path = Path(script_path)
    if not script_path.exists():
        print(f"❌ Error: Script {script_path} does not exist.")
        return False
    
    test_file_name = f"test_{script_path.name}"
    target_path = UNIT_TEST_DIR / test_file_name
    
    if target_path.exists():
        print(f"⚠️ Warning: Test file {target_path} already exists. Skipping.")
        return False
    
    template_path = TEMPLATES_DIR / "UNIT_TEST_TEMPLATE.py"
    if not template_path.exists():
        print(f"❌ Error: Template {template_path} not found.")
        return False
    
    # Copy and replace
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Basic replacements
    module_name = script_path.stem
    content = content.replace("from scripts.your_module import your_function", f"from scripts.{module_name} import *")
    content = content.replace("TestYourModule", f"Test{module_name.title().replace('_', '')}")
    content = content.replace("[Module Name]", script_path.name)
    
    # Add Agent "START HERE" block
    agent_block = """
# 🤖 AGENT START HERE
# 1. Run this test: python3 tests/unit/{} -v
# 2. Capture output: python3 tests/unit/{} -v 2>&1 | tee tests/unit/actual_output.txt
# 3. Update Dashboard: tests/README.md
""".format(test_file_name, test_file_name)
    
    content = agent_block + content

    with open(target_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created unit test: {target_path}")
    return True

def scaffold_feature_test(feature_name):
    """Create a feature test directory structure."""
    target_dir = FEATURE_TEST_DIR / feature_name
    if target_dir.exists():
        print(f"⚠️ Warning: Feature test directory {target_dir} already exists. Skipping.")
        return False
    
    # Create structure
    os.makedirs(target_dir / "test-data", exist_ok=True)
    os.makedirs(target_dir / "expected-output", exist_ok=True)
    os.makedirs(target_dir / "actual-output", exist_ok=True)
    
    # Create metadata.yaml
    with open(target_dir / "metadata.yaml", 'w') as f:
        f.write(f"""id: {feature_name.upper()}_TEST
title: {feature_name.replace('_', ' ').title()} Test Scenario
type: documentation
owner: platform-team
lifecycle: active
reliability:
  maturity: 1
  rollback_strategy: git-revert
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
schema_version: 1
""")

    # Copy templates
    shutil.copy(TEMPLATES_DIR / "FEATURE_TEST_TEMPLATE.md", target_dir / "README.md")
    shutil.copy(TEMPLATES_DIR / "TEST_PLAN_TEMPLATE.md", target_dir / "test-plan.md")
    
    # Append Agent "START HERE" to README
    with open(target_dir / "README.md", 'a') as f:
        f.write("\n---\n\n## 🤖 AGENT START HERE\n- **Objective**: Execute the steps in `test-plan.md`.\n- **Evidence**: Save outputs to `actual-output/`.\n- **Record**: Update dashboard in `tests/README.md`.\n")

    print(f"✅ Created feature test directory: {target_dir}")
    print(f"👉 Next steps: Edit {target_dir}/test-plan.md to define your objectives.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Scaffold testing structures for the platform.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--script", help="Path to the python script to create a unit test for.")
    group.add_argument("--feature", help="Name of the feature to create a feature test structure for.")
    
    args = parser.parse_args()
    
    if args.script:
        scaffold_unit_test(args.script)
    elif args.feature:
        scaffold_feature_test(args.feature.replace(" ", "-").lower())

if __name__ == "__main__":
    main()
