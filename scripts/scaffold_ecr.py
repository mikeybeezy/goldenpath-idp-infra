#!/usr/bin/env python3
"""
Purpose: Standardized ECR Repository Scaffolding.
Creates Terraform config and ensures governance metadata sidecars (Owner, Risk, ID).
"""
import sys
import os
import argparse
import re

def get_input(prompt, default=None):
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ")
            return user_input if user_input else default
        else:
            user_input = input(f"{prompt} (Required): ")
            if user_input.strip():
                return user_input
            print("❌ This field is required.")

def validate_id(val):
    if not val or not re.match(r'^[A-Z0-9_]+$', val):
        print("Error: ID must be UPPERCASE_WITH_UNDERSCORES (e.g. APP_MYAPP_MAIN)")
        sys.exit(1)
    return val

def generate_tfvars_entry(app_name, app_id, owner, risk):
    return f'''
  "{app_name}" = {{
    metadata = {{
      id    = "{app_id}"
      owner = "{owner}"
      risk  = "{risk}"
    }}
  }}
'''

def update_tfvars(environment, entry):
    tfvars_path = f"envs/{environment}/terraform.tfvars"

    # Ensure file exists
    if not os.path.exists(tfvars_path):
        with open(tfvars_path, "w") as f:
            f.write("ecr_repositories = {\n}\n")

    with open(tfvars_path, "r") as f:
        lines = f.readlines()

    # Find the start of ecr_repositories
    start_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("ecr_repositories = {"):
            start_index = i
            break

    if start_index == -1:
        # Append new block if not found
        with open(tfvars_path, "a") as f:
            f.write(f"\necr_repositories = {{\n{entry}}}\n")
        print(f"✅ Created new ecr_repositories block in {tfvars_path}")
        return

    # Find the matching closing brace
    # Simple heuristic: Identify the closing brace corresponding to the opening one
    # Assuming standard indentation (closing brace on its own line)

    insert_index = -1
    brace_count = 0
    found_start = False

    # Re-scan to track braces carefully
    for i, line in enumerate(lines):
        if i < start_index: continue

        brace_count += line.count("{")
        brace_count -= line.count("}")

        if brace_count == 0:
            insert_index = i
            break

    if insert_index != -1:
        # Insert before the closing brace
        lines.insert(insert_index, entry)
        with open(tfvars_path, "w") as f:
            f.writelines(lines)
        print(f"✅ Injected entry into {tfvars_path}")
    else:
        print("❌ Could not parse ecr_repositories block structure.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Scaffold an ECR registry config.")
    parser.add_argument("--app-name", help="Name of the application/repo")
    parser.add_argument("--app-id", help="Governance ID (e.g. APP_WORDPRESS_MAIN)")
    parser.add_argument("--owner", help="Team owner (e.g. platform-team)")
    parser.add_argument("--risk", help="Risk profile (low, medium, high)", default="medium")
    parser.add_argument("--environment", help="Target environment (dev, prod)", default="dev")
    parser.add_argument("--dry-run", action="store_true", help="Print instead of writing")

    args = parser.parse_args()

    # Determine validation mode
    interactive = not any([args.app_name, args.app_id, args.owner])

    if not interactive:
        missing = []
        if not args.app_name: missing.append("--app-name")
        if not args.app_id: missing.append("--app-id")
        if not args.owner: missing.append("--owner")
        if missing:
            print(f"❌ Error: Required: {', '.join(missing)}")
            sys.exit(1)

    # Interactive mode inputs
    if interactive: print(f"--- ECR Scaffolding ({args.environment}) ---")
    app_name = args.app_name or get_input("Application Name (e.g. goldenpath-wordpress-app)")
    app_id = args.app_id or get_input("Governance ID (e.g. APP_{NAME}_MAIN)")
    validate_id(app_id)
    owner = args.owner or get_input("Owner Team (e.g. app-team-alpha)")
    risk = args.risk or get_input("Risk Profile", "medium")
    environment = args.environment or get_input("Environment", "dev")

    tfvars_entry = generate_tfvars_entry(app_name, app_id, owner, risk)

    if args.dry_run:
        print(f"\n--- Preview (envs/{environment}/terraform.tfvars) ---")
        print(tfvars_entry)
    else:
        update_tfvars(environment, tfvars_entry)
        print("🚀 Next: Run 'terraform plan' to verify.")

if __name__ == "__main__":
    main()
