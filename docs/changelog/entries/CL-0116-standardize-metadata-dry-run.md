<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0116
title: Standardize Metadata Dry-Run Implementation
type: changelog
status: active
owner: platform-team
domain: platform-governance
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 3
schema_version: 1
relates_to:
  - ADR-0126
  - CL-0116
  - CL-0117
  - SCRIPT_CERTIFICATION_AUDIT
  - standardize_metadata.py
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
date: 2026-01-12
breaking_change: false
---

# CL-0116: Standardize Metadata Dry-Run Implementation

## Summary
Implemented mandatory `--dry-run` support in `scripts/standardize_metadata.py`, enforcing safety gates on the platform's primary metadata remediation engine ("The Healer").

## Problem Statement
The `standardize_metadata.py` script performs mass edits on hundreds of files to enforce governance schemas. Previously, it lacked a preview mode, meaning any execution immediately modified disk state. This created high operational risk and prevented safe validation in CI.

## Solution Implemented
Refactored `standardize_metadata.py` to support `argparse` and a `--dry-run` flag.

### Key Changes
1.  **State Protection**: All file write operations (`metadata.yaml` injection, frontmatter updates) are now wrapped in `if not dry_run:` checks.
2.  **CLI Interface**: Updated from raw `sys.argv` to structured `argparse`.
3.  **Preview Logging**: In dry-run mode, the script prints exactly what *would* be modified (e.g., `[DRY-RUN] Would standardize: ...`).
4.  **Function Signatures**: Propagated `dry_run` context through `standardize_file()` and `inject_governance()`.

## Benefits
- ✅ **Operational Safety**: Developers can preview remediation scope before applying changes.
- ✅ **CI Integration**: Enables safe "compliance checks" in CI without dirtying the git tree.
- ✅ **Certification**: Moves `standardize_metadata.py` closer to ⭐⭐⭐ maturity (Safety requirement met).

## Verification
New CLI usage:
```bash
# Preview changes (Safe)
python3 scripts/standardize_metadata.py --dry-run

# Apply changes (Destructive)
python3 scripts/standardize_metadata.py
```

## Related Work
- Part of **Script Certification Blitz** (Day 1)
- Blocks [CL-0117] (Unit Test coverage for standardized metadata)
