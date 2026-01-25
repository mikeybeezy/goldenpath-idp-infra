<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0118
title: Automated Governance Backfill & V1 Acceptance Rules
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
  - ADR-0146
  - ADR-0147
  - CL-0118
  - CL-0119
  - GUIDE-002
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

# CL-0118: Automated Governance Backfill & V1 Acceptance Rules

## Summary
Released the **Governance Backfill Injector** to automate the migration of legacy scripts to the "Born Governed" standard, and upgraded the **Validator** with V1 Acceptance Rules.

## Problem Statement
While the governance standard (ADR-0146) was established, manual adoption across 45+ legacy scripts was slow and error-prone. Additionally, the validator lacked specific logic to enforce "Test File Existence" and "Risk Policy Compliance".

## Solution Implemented

### 1. Automated Backfill Injector
New tool `scripts/inject_script_metadata.py`:
- Scans `scripts/` recursively.
- Assigns deterministic, persistent IDs (`SCRIPT-XXXX`) via `script_ids.yaml` registry.
- Injects fully compliant V1 headers into Python and Bash scripts.
- Supports Dry-Run mode.

### 2. V1 Acceptance Rules
Upgraded `scripts/validate_scripts_tested.py` to enforce:
- **Test Existence**: If `runner: pytest`, the referenced test file MUST exist on disk.
- **Risk Policy**: Scripts with `production_impact: medium|high` CANNOT use `evidence: manual`.
- **Command Integrity**: `shellcheck` commands must reference the script file.

## Usage
To backfill the entire repository:
```bash
python3 scripts/inject_script_metadata.py
```

To validate compliance:
```bash
python3 scripts/validate_scripts_tested.py
```

## Benefits
- **Zero-Touch Migration**: Moving from 2% to 100% governance coverage takes < 1 minute.
- **Strict Safety**: Impossible to declare "Manual Testing" for critical scripts.
- **Broken Link Detection**: Validator catches verified test commands pointing to missing files.
