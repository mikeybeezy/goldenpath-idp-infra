---
id: CL-0117
title: Schema-Driven Script Certification
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
  - ADR-0146
  - CL-0116
  - CL-0117
  - SCRIPT_SCHEMA_V1
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
date: 2026-01-12
breaking_change: false
---
# CL-0117: Schema-Driven Script Certification

## Summary
Introduced a rigid, schema-driven contracts system for script certification, replacing heuristic checks with explicit metadata governance.

## Problem Statement
Previously, script "quality" was assessed by checking for the existence of files (e.g., `if test_X.py exists`). This:
- Allowed empty or irrelevant tests to pass
- Failed to capture dry-run support explicitely
- Had no mechanism to enforce "proof of execution" in CI
- Was hardcoded in Python, making policy changes difficult

## Solution Implemented

### 1. The Contract (`schemas/automation/script.schema.yaml`)
Defined a formal JSON Schema for script metadata that strictly enforces:
- **Identity**: `id`, `type`, `owner`
- **Maturity**: Level 1-3
- **Test Strategy**: `runner`, `command`, `evidence` type
- **Safety**: `dry_run.supported` boolean

### 2. The Enforcer (`scripts/validate_scripts_tested.py`)
A new validator that:
- Parses YAML Frontmatter from Python (`""" --- ... """`) and Bash (`# --- ...`) scripts
- Validates fields against the schema
- **(Future)** Verifies CI Proof files for high-risk scripts

### 3. Reference Implementation
Updated `scripts/standardize_metadata.py` and `scripts/validate_scripts_tested.py` to include full schema-compliant headers.

## Benefits
- **Explicit Quality**: Every script declares *exactly* how it is tested.
- **Policy-as-Code**: We can now write rules like "If Risk=High, Evidence MUST = CI".
- **Visual Compliance**: Browsing a script source code immediately reveals its maturity and safety profile.

## Migration Guide
To certify a script:
1. Add the metadata header to your script.
2. Run `python3 scripts/validate_scripts_tested.py path/to/script.py`.

**Python Example:**
```python
"""
---
id: my_script
type: script
owner: platform-team
status: active
maturity: 3
test:
  runner: pytest
  command: "pytest tests/unit/test_my.py"
  evidence: declared
dry_run:
  supported: true
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
---
"""
```

## Next Steps
- Roll out headers to P0 scripts.
- Integrate validation into `pre-commit` (Replacing the old heuristic script).
