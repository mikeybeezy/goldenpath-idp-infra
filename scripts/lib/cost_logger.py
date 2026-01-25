"""
---
id: SCRIPT-0045
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
  command_hint: --dry-run
test:
  runner: pytest
  command: pytest -q tests/scripts/test_script_0045.py
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
LEDGER_DIR = REPO_ROOT / ".goldenpath"
LEDGER_FILE = LEDGER_DIR / "cost_ledger.json"

def log_cost_estimate(monthly_cost, currency="USD", source="manual"):
    """
    Log a monthly cost estimate to the ledger.
    """
    try:
        LEDGER_DIR.mkdir(parents=True, exist_ok=True)

        if LEDGER_FILE.exists():
            with open(LEDGER_FILE, 'r') as f:
                ledger = json.load(f)
        else:
            ledger = {
                "current_monthly_estimate": 0.0,
                "currency": currency,
                "last_updated": None,
                "history": []
            }

        entry = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "monthly_cost": float(monthly_cost),
            "source": source
        }

        ledger["current_monthly_estimate"] = float(monthly_cost)
        ledger["last_updated"] = entry["timestamp"]
        ledger["history"].append(entry)

        # Keep history manageable
        if len(ledger["history"]) > 50:
            ledger["history"] = ledger["history"][-50:]

        with open(LEDGER_FILE, 'w') as f:
            json.dump(ledger, f, indent=2)

        return True, f"Logged ${monthly_cost} {currency} monthly estimate."
    except Exception as e:
        return False, str(e)

def get_cost_summary():
    """Retrieve the latest cost summary from the ledger."""
    if not LEDGER_FILE.exists():
        return {"current_monthly_estimate": 0.0, "currency": "USD", "last_updated": "never"}
    try:
        with open(LEDGER_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"current_monthly_estimate": 0.0, "currency": "USD", "last_updated": "error"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        success, msg = log_cost_estimate(sys.argv[1], source="cli")
        print(msg)
