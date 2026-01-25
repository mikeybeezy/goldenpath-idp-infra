# AGENT_CONTEXT: Read .agent/README.md for rules
#!/usr/bin/env python3
"""
---
id: repair_shebangs
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
test:
  runner: pytest
  command: "pytest -q tests/unit/test_repair_shebangs.py"
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
---
Purpose: Fixes scripts where metadata injection pushed the Shebang down.
"""
import os
import argparse
from pathlib import Path

SCRIPTS_DIR = Path("scripts")

def repair_file(path: Path, dry_run: bool) -> bool:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"Skipping {path}: {e}")
        return False

    if not lines:
        return False

    # Find shebang location
    shebang_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("#!"):
            shebang_idx = i
            break

    # If shebang is already at 0, or not found, we are good
    if shebang_idx <= 0:
        return False

    # Shebang found at > 0. Verify index 0 is metadata start
    if not lines[0].strip().startswith('"""'):
        # It's displaced, but not by our metadata block?
        # Still, we should probably move it up.
        pass

    print(f"🔧 Repairing {path}: Shebang found at line {shebang_idx+1}")

    shebang_line = lines.pop(shebang_idx)
    lines.insert(0, shebang_line)

    if dry_run:
        print(f"[DRY-RUN] Would write fixed content to {path}")
    else:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    count = 0
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        if repair_file(p, args.dry_run):
            count += 1

    print(f"Repaired {count} files.")

if __name__ == "__main__":
    main()
