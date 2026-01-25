"""
---
id: SCRIPT-0048
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0048.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

import os
import json
import yaml
import sys
from datetime import datetime
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
LEDGER_DIR = REPO_ROOT / ".goldenpath"
LEDGER_FILE = LEDGER_DIR / "value_ledger.json"

def get_script_value(script_name):
    """
    Look up the potential savings for a script from its metadata.
    Searches the scripts/ directory for the script's own frontmatter
    or its parent metadata.yaml.
    """
    scripts_dir = REPO_ROOT / "scripts"
    script_path = scripts_dir / script_name

    # 1. Try script's own frontmatter (if it's a .py file)
    if script_name.endswith('.py') and script_path.exists():
        try:
            with open(script_path, 'r') as f:
                content = f.read()
                import re
                match = re.search(r'---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    data = yaml.safe_load(match.group(1))
                    if isinstance(data, dict):
                        vq = data.get('value_quantification', {})
                        if isinstance(vq, dict) and 'potential_savings_hours' in vq:
                            return float(vq['potential_savings_hours'])
        except:
            pass

    # 2. Try parent metadata.yaml (Inheritance)
    metadata_path = script_path.parent / "metadata.yaml"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    vq = data.get('value_quantification', {})
                    if isinstance(vq, dict) and 'potential_savings_hours' in vq:
                        return float(vq['potential_savings_hours'])
        except:
            pass

    return 0.1 # Default fallback for untagged scripts

def log_heartbeat(script_name):
    """Log a successful execution of a script to the value ledger."""
    try:
        LEDGER_DIR.mkdir(parents=True, exist_ok=True)

        # Load existing ledger
        if LEDGER_FILE.exists():
            with open(LEDGER_FILE, 'r') as f:
                ledger = json.load(f)
        else:
            ledger = {
                "total_reclaimed_hours": 0.0,
                "history": []
            }

        # Calculate value
        value = get_script_value(script_name)

        # Update ledger
        entry = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "script": script_name,
            "reclaimed_hours": value
        }

        ledger["total_reclaimed_hours"] = round(ledger.get("total_reclaimed_hours", 0.0) + value, 2)
        ledger["history"].append(entry)

        # Keep history manageable (last 100 entries)
        if len(ledger["history"]) > 100:
            ledger["history"] = ledger["history"][-100:]

        with open(LEDGER_FILE, 'w') as f:
            json.dump(ledger, f, indent=2)
            f.write('\n')

        return True, f"Logged {value} hours for {script_name}"
    except Exception as e:
        return False, str(e)

def get_total_reclaimed_hours():
    """Retrieve the total reclaimed hours from the ledger."""
    if not LEDGER_FILE.exists():
        return 0.0
    try:
        with open(LEDGER_FILE, 'r') as f:
            ledger = json.load(f)
            return ledger.get("total_reclaimed_hours", 0.0)
    except Exception as e:
        sys.stderr.write(f"Error reading ledger: {e}\n")
        return 0.0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        success, msg = log_heartbeat(sys.argv[1])
        print(msg)
