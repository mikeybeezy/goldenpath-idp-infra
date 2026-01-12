"""
---
id: SCRIPT-0031
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0031.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

#!/usr/bin/env python3
"""
Purpose: Standardized ECR Repository Scaffolding.
Relates-To: how-it-works/ECR_REQUEST_FLOW.md
"""
import sys
import os
import argparse
import re
from datetime import datetime

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

def get_optional(prompt):
    user_input = input(f"{prompt} (Optional): ")
    return user_input.strip() or None

def to_registry_id(app_name):
    return "REGISTRY_" + re.sub(r'[^a-z0-9]+', '_', app_name.lower()).strip('_').upper()

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

def ensure_catalog(catalog_path):
    if os.path.exists(catalog_path):
        return

    with open(catalog_path, "w") as f:
        f.write(
            'version: "1.0"\n'
            "domain: delivery\n"
            "owner: platform-team\n"
            f'last_updated: "{datetime.utcnow().strftime("%Y-%m-%d")}"\n'
            "managed_by: platform-team\n"
            'physical_registry: "goldenpath-idp-main"\n'
            "repositories:\n"
        )

def update_ecr_catalog(catalog_path, name, registry_id, owner, risk, environment, requester, domain):
    ensure_catalog(catalog_path)

    with open(catalog_path, "r") as f:
        content = f.read()

    if re.search(rf"(?m)^\\s{{2}}{re.escape(name)}:", content):
        print(f"⚠️  Catalog already contains registry {name}; skipping catalog update.")
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    content = re.sub(r'(?m)^last_updated:.*$', f'last_updated: "{today}"', content)

    metadata_lines = [
        f"      id: {registry_id}",
        f"      owner: {owner}",
        f"      risk: {risk}",
        f"      environment: {environment}",
        f'      created_date: "{today}"',
        "      status: pending",
    ]
    if requester:
        metadata_lines.insert(3, f"      requested_by: {requester}")
    if domain:
        metadata_lines.insert(4, f"      domain: {domain}")

    entry = "\n".join(
        [f"  {name}:", "    metadata:"] + metadata_lines
    )

    if "repositories:" not in content:
        content = content.rstrip() + "\nrepositories:\n"

    content = content.rstrip() + "\n" + entry + "\n"

    with open(catalog_path, "w") as f:
        f.write(content)
    print(f"✅ Updated catalog for registry: {name}")

def main():
    parser = argparse.ArgumentParser(description="Scaffold an ECR registry config.")
    parser.add_argument("--app-name", help="Name of the application/repo")
    parser.add_argument("--app-id", help="Governance ID (e.g. REGISTRY_WORDPRESS_MAIN)")
    parser.add_argument("--owner", help="Team owner (e.g. platform-team)")
    parser.add_argument("--risk", help="Risk profile (low, medium, high)", default="medium")
    parser.add_argument("--environment", help="Target environment (dev, prod)", default="dev")
    parser.add_argument("--requester", help="Requesting user (e.g. daniel-deans)")
    parser.add_argument("--domain", help="Domain (e.g. delivery)")
    parser.add_argument("--catalog-path", default="docs/20-contracts/catalogs/ecr-catalog.yaml")
    parser.add_argument("--skip-catalog", action="store_true", help="Skip catalog update")
    parser.add_argument("--dry-run", action="store_true", help="Print instead of writing")

    args = parser.parse_args()

    # Determine validation mode
    interactive = not any([args.app_name, args.app_id, args.owner])

    if not interactive:
        missing = []
        if not args.app_name: missing.append("--app-name")
        if not args.owner: missing.append("--owner")
        if missing:
            print(f"❌ Error: Required: {', '.join(missing)}")
            sys.exit(1)

    # Interactive mode inputs
    if interactive: print(f"--- ECR Scaffolding ({args.environment}) ---")
    app_name = args.app_name or get_input("Application Name (e.g. goldenpath-wordpress-app)")
    default_id = to_registry_id(app_name)
    app_id = args.app_id or get_input("Governance ID (e.g. REGISTRY_{NAME})", default_id)
    validate_id(app_id)
    owner = args.owner or get_input("Owner Team (e.g. app-team-alpha)")
    risk = args.risk or get_input("Risk Profile", "medium")
    environment = args.environment or get_input("Environment", "dev")
    if interactive:
        requester = args.requester or get_optional("Requesting User (e.g. daniel-deans)")
        domain = args.domain or get_optional("Domain (e.g. delivery)")
    else:
        requester = args.requester
        domain = args.domain

    tfvars_entry = generate_tfvars_entry(app_name, app_id, owner, risk)

    if args.dry_run:
        print(f"\n--- Preview (envs/{environment}/terraform.tfvars) ---")
        print(tfvars_entry)
    else:
        update_tfvars(environment, tfvars_entry)
        if not args.skip_catalog:
            update_ecr_catalog(
                args.catalog_path,
                app_name,
                app_id,
                owner,
                risk,
                environment,
                requester,
                domain,
            )
        print("🚀 Next: Run 'terraform plan' to verify.")

if __name__ == "__main__":
    main()
