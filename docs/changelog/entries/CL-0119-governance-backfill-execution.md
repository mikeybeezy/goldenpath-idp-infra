---
id: CL-0119
title: The Great Governance Backfill (Execution)
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
  - CL-0118
  - ADR-0147
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

# CL-0119: The Great Governance Backfill (Execution)

## Summary
Executed the `scripts/inject_script_metadata.py` migration tool, applying governance headers to 41 legacy scripts.

## Outcome
- **41 Scripts Backfilled**: Moved from Maturity 0 (Ungoverned) to Maturity 2 (Validated/Linted).
- **ID Registry Established**: `schemas/automation/script_ids.yaml` now tracks 43 unique script IDs.
- **Bash Compliance**: All Bash scripts immediately passed V1 validation as `shellcheck` runs against the source file.
- **Python Gap Identified**: 30+ Python scripts are now flagged as `FAIL` by the validator because their declared unit tests (`tests/scripts/test_script_XXXX.py`) do not yet exist.

## Next Steps
This migration successfully converted "Hidden Technical Debt" into "Explicit Check Failures". The platform team must now systematically create the missing test files to achieve green status.

## Change Details
- **Added Headers**: To all `scripts/*.py` and `scripts/*.sh` files.
- **Created Registry**: `schemas/automation/script_ids.yaml`
