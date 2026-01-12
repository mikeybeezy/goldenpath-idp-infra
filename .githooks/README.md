---
id: APPS_.GITHOOKS
title: Script Certification Enforcement
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
---

# Script Certification Enforcement

This directory contains git hooks to enforce script certification standards.

## Pre-Commit Hook: Script Certification

**Purpose:** Prevents committing new scripts without tests or dry-run support  
**Enforcement Level:** Local (developer machine) + CI (GitHub Actions)

### Installation

```bash
# One-time setup (run from repo root)
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit-script-certification
```

### What It Checks

When you try to commit a new script in `scripts/`, it validates:

1. **✅ Structured Docstring**  
   Must include: Purpose, Achievement, Value, Relates-To

2. **✅ Test Coverage OR Dry-Run**  
   Must have at least ONE of:
   - Unit test at `tests/unit/test_<script>.py`
   - `--dry-run` flag implementation

### Example: Blocked Commit

```
$ git commit -m "add new script"

🔍 Scanning new scripts for certification requirements...
------------------------------------------------------------
❌ COMMIT BLOCKED: New scripts missing certification requirements

📄 scripts/my_new_script.py
   ❌ Missing structured docstring (Purpose/Achievement/Value/Relates-To)
   ❌ Missing BOTH unit test AND dry-run support (need at least one)

============================================================
📋 TO FIX:
============================================================

Option 1: Add structured docstring
  python3 scripts/scaffold_test.py --script my_new_script.py

Option 2: Add unit test
  Create: tests/unit/test_my_new_script.py

Option 3: Add dry-run support
  Add --dry-run flag to script (see SCRIPT_CERTIFICATION_AUDIT.md)

============================================================
```

### Bypass (Emergency Only)

If you MUST commit without certification:

```bash
git commit --no-verify -m "WIP: emergency hotfix"
```

**⚠️ Warning:** CI will still block the PR. This only skips the local check.

### CI Enforcement

Even if local hook is bypassed, the **Script Certification Gate** workflow will:
1. Detect new scripts in PR
2. Run the same validation
3. Block merge if requirements not met
4. Post helpful comment with remediation steps

**You cannot merge without certification.**

---

## Troubleshooting

### Hook not running?

```bash
# Verify hooks path
git config core.hooksPath
# Should output: .githooks

# Verify hook is executable
ls -la .githooks/pre-commit-script-certification
# Should show: -rwxr-xr-x (executable)

# Re-enable hooks
chmod +x .githooks/pre-commit-script-certification
```

### False positive for library module?

Move it to `scripts/lib/`:
```bash
mv scripts/my_util.py scripts/lib/my_util.py
```

Library modules in `scripts/lib/` are exempt from testing requirements.

---

## See Also

- [Script Certification Audit](/docs/10-governance/SCRIPT_CERTIFICATION_AUDIT.md)
- [Confidence Matrix](/docs/antig-implementations/CONFIDENCE_MATRIX.md)
- [Testing Standards](/tests/TESTING_STANDARDS.md)
