#!/usr/bin/env python3
"""
---
id: SCRIPT-0002
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
test:
  runner: pytest
  command: "pytest -q tests/unit/test_inject_script_metadata.py"
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""
from __future__ import annotations
import re
import argparse
from pathlib import Path
import yaml

SCRIPTS_DIR = Path("scripts")
ID_REGISTRY = Path("schemas/automation/script_ids.yaml")

PY_META_RE = re.compile(r'"""[\s\S]*?^---[\s\S]*?^---[\s\S]*?"""', re.MULTILINE)
SH_META_RE = re.compile(r'(?m)^\s*#\s*---\s*$')

def load_id_registry() -> dict:
    if ID_REGISTRY.exists():
        return yaml.safe_load(ID_REGISTRY.read_text()) or {}
    return {"next": 1, "map": {}}

def save_id_registry(reg: dict) -> None:
    ID_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    ID_REGISTRY.write_text(yaml.safe_dump(reg, sort_keys=False))

def alloc_id(reg: dict, script_path: str) -> str:
    if script_path in reg["map"]:
        return reg["map"][script_path]
    n = int(reg.get("next", 1))
    sid = f"SCRIPT-{n:04d}"
    reg["map"][script_path] = sid
    reg["next"] = n + 1
    return sid

def build_meta(sid: str, ext: str) -> dict:
    if ext == ".py":
        runner = "pytest"
        cmd = f'pytest -q tests/scripts/test_{sid.lower().replace("-", "_")}.py'
    elif ext in (".sh", ".bash"):
        runner = "shellcheck"
        cmd = "shellcheck "  # filled later by validator/enricher
    else:
        runner = "custom"
        cmd = "true"

    return {
        "id": sid,
        "type": "script",
        "owner": "platform-team",
        "status": "active",
        "maturity": 2,
        "dry_run": {"supported": True, "command_hint": "--dry-run"},
        "test": {"runner": runner, "command": cmd, "evidence": "declared"},
        "risk_profile": {"production_impact": "low", "security_risk": "low", "coupling_risk": "low"},
    }

def inject_py(path: Path, meta: dict, dry_run: bool = False) -> bool:
    txt = path.read_text(encoding="utf-8", errors="replace")
    if '---\n' in txt[:400] and PY_META_RE.search(txt[:800]):  # already has block
        return False
    
    block = '"""\n---\n' + yaml.safe_dump(meta, sort_keys=False) + '---\n"""\n\n'
    
    if dry_run:
        print(f"[DRY-RUN] Would inject metadata into {path}")
    else:
        path.write_text(block + txt, encoding="utf-8")
    return True

def inject_sh(path: Path, meta: dict, dry_run: bool = False) -> bool:
    txt = path.read_text(encoding="utf-8", errors="replace")
    if SH_META_RE.search(txt[:200]):
        return False
    y = yaml.safe_dump(meta, sort_keys=False).strip().splitlines()
    block = "\n".join(["# ---"] + [f"# {line}" for line in y] + ["# ---", ""])
    
    # keep shebang first if present
    if txt.startswith("#!"):
        first_line, rest = txt.split("\n", 1)
        new_txt = first_line + "\n" + block + rest
    else:
        new_txt = block + txt
        
    if dry_run:
        print(f"[DRY-RUN] Would inject metadata into {path}")
    else:
        path.write_text(new_txt, encoding="utf-8")
    return True

def main() -> int:
    parser = argparse.ArgumentParser(description="Inject metadata backfill")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    args = parser.parse_args()

    reg = load_id_registry()
    changed = 0

    for p in sorted(SCRIPTS_DIR.glob("*")):
        if p.is_dir():
            continue
        if p.suffix not in (".py", ".sh", ".bash"):
            continue
        if p.name == "inject_script_metadata.py":
            continue

        sid = alloc_id(reg, str(p))
        meta = build_meta(sid, p.suffix)

        if p.suffix == ".py":
            changed += 1 if inject_py(p, meta, args.dry_run) else 0
        else:
            # shellcheck cmd should include filename
            meta["test"]["command"] = f"shellcheck {p}"
            changed += 1 if inject_sh(p, meta, args.dry_run) else 0

    if not args.dry_run:
        save_id_registry(reg)
        
    print(f"[inject] updated {changed} scripts")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
