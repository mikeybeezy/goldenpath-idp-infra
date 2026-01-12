#!/usr/bin/env python3
"""
Purpose: Governance Registry Integrity Validator
Achievement: Enforces the ledger contract on the governance-registry branch by validating:
             1. Required folder structure (no random files)
             2. Chain-of-custody metadata headers in all artifacts
             3. Prevents manual commits without proper provenance
Value: Maintains the governance-registry as a high-integrity audit log, preventing drift
Relates-To: ADR-0145, RB-0028
"""
import os
import re
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "env",
    "generated_at",
    "source:",
    "branch:",
    "sha:",
    "pipeline:",
    "workflow:",
    "run_id:",
    "integrity:",
    "derived_only:",
]

ALLOWED_TOP_LEVEL = {"environments", "UNIFIED_DASHBOARD.md", ".git", ".github", "README.md"}

# Basic frontmatter extractor (--- ... ---)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def fail(msg: str) -> None:
    print(f"[govreg-validate] FAIL: {msg}", file=sys.stderr)
    sys.exit(1)

def warn(msg: str) -> None:
    print(f"[govreg-validate] WARN: {msg}", file=sys.stderr)

def is_markdown(p: Path) -> bool:
    return p.suffix.lower() in {".md", ".markdown"}

def validate_top_level(root: Path) -> None:
    """Ensure only allowed paths exist at the root of the registry branch."""
    for p in root.iterdir():
        name = p.name
        if name not in ALLOWED_TOP_LEVEL:
            fail(f"Unexpected top-level path in governance-registry: {name}")

def validate_env_layout(root: Path) -> None:
    """Ensure every environment has the required latest/ and history/ folders."""
    env_root = root / "environments"
    if not env_root.exists():
        fail("Missing required 'environments/' directory")

    for env_dir in env_root.iterdir():
        if not env_dir.is_dir():
            fail(f"Unexpected non-directory under environments/: {env_dir.name}")

        latest = env_dir / "latest"
        history = env_dir / "history"
        if not latest.exists():
            fail(f"Missing {env_dir.name}/latest/")
        if not history.exists():
            fail(f"Missing {env_dir.name}/history/")

def validate_frontmatter(md_file: Path) -> None:
    """Validate that the markdown file contains all required chain-of-custody fields."""
    content = md_file.read_text(encoding="utf-8", errors="replace")
    m = FRONTMATTER_RE.match(content)
    if not m:
        fail(f"Missing YAML frontmatter in: {md_file}")

    fm = m.group(1)
    # Simple presence checks (string-based) to keep this dependency-free
    for k in REQUIRED_KEYS:
        if k not in fm:
            fail(f"Missing required key '{k}' in frontmatter for: {md_file}")

def validate_markdown_headers(root: Path) -> None:
    """Validate frontmatter in all markdown artifacts under latest/ and history/."""
    env_root = root / "environments"
    for md in env_root.rglob("*.md"):
        # Only enforce under environments/*/(latest|history)/**
        parts = md.parts
        if "environments" in parts and ("latest" in parts or "history" in parts):
            validate_frontmatter(md)

    # Validate unified dashboard if present
    dash = root / "UNIFIED_DASHBOARD.md"
    if dash.exists():
        validate_frontmatter(dash)
    else:
        warn("UNIFIED_DASHBOARD.md not found (ok if you haven't enabled it yet)")

def main() -> None:
    root = Path(".").resolve()

    print("[govreg-validate] Validating governance registry integrity...")
    
    validate_top_level(root)
    validate_env_layout(root)
    validate_markdown_headers(root)

    print("[govreg-validate] ✅ OK: governance registry integrity validated")

if __name__ == "__main__":
    main()
