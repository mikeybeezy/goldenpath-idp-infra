# AGENT_CONTEXT: Read .agent/README.md for rules
#!/usr/bin/env python3
"""
---
id: SCRIPT-0012
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0012.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

"""
YAML Syntax Fixer for Templates

Purpose:
    Automatically identifies and fixes common YAML syntax issues in template files,
    specifically focusing on unquoted Jinja2/Backstage template placeholders.

What it does:
    1. Scans .yaml and .yml files in specified directories.
    2. Enforces quoting on values containing {{ brackets }}.
    3. Enforces quoting on keys containing {{ brackets }}.
    4. Prevents common parsing errors when templates are used as raw YAML.

Usage:
    python3 scripts/fix_yaml_syntax.py [DIRECTORY]
"""
import re
import os

def fix_yaml_templates(directory):
    for root, _, files in os.walk(directory):
        if 'node_modules' in root or '.git' in root:
            continue
        for f in files:
            if f.endswith(('.yaml', '.yml')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8') as stream:
                        lines = stream.readlines()

                    new_lines = []
                    for line in lines:
                        # 1. Handle value: key: {{ template }}
                        # Match something like '  name: {{ values.name }}'
                        # but skip if already quoted or if it's a multiline marker | or >
                        if ':' in line and not any(c in line for c in ['"', "'", '|', '>']):
                            parts = line.split(':', 1)
                            key = parts[0]
                            val = parts[1].strip()
                            if '{{' in val and '}}' in val:
                                line = f'{key}: "{val}"\n'

                        # 2. Handle key: {{ template }}: value
                        # Match something like '  {{ template }}-foo: value'
                        if ':' in line and not any(c in line for c in ['"', "'"]):
                            parts = line.split(':', 1)
                            key = parts[0]
                            if '{{' in key and '}}' in key:
                                indent = len(key) - len(key.lstrip())
                                line = f'{" " * indent}"{key.lstrip()}":{parts[1]}'

                        new_lines.append(line)

                    new_content = "".join(new_lines)
                    with open(path, 'r', encoding='utf-8') as stream:
                        old_content = stream.read()

                    if new_content != old_content:
                        with open(path, 'w', encoding='utf-8') as stream:
                            stream.write(new_content)
                        print(f"Fixed: {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    fix_yaml_templates('apps')
    fix_yaml_templates('gitops/helm')
