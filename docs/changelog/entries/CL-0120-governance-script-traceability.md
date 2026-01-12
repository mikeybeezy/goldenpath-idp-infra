---
id: CL-0120
title: Governance Script Traceability
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
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0146
  - ADR-0147
  - ADR-0121
  - ADR-0124
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

# CL-0120: Governance Script Traceability

## Summary
Ensured full traceability for the platform's core governance and utility scripts by linking them to ADRs and Changelog entries.

## Problem Statement
The "Script Traceability Auditor" (`check_script_traceability.py`) identified several critical scripts that were being governed but lacked explicit links to architectural decisions (ADRs) or historical change logs (CLs). This created "Dark Automation" pockets.

## Solution Implemented
Registered the following scripts in the platform knowledge graph:

1.  **`generate_script_matrix.py`**: Linked to ADR-0146 for automated certification reporting.
2.  **`scaffold_test.py`**: Linked to ADR-0146 for standardized test scaffolding.
3.  **`check-policy-compliance.py`**: Linked to ADR-0146 (and ADR-0093) for automated policy governance.
4.  **`repair_shebangs.py`**: Linked to ADR-0147 for automated script dialect correction during backfill.
5.  **`cost_logger.py`**: Linked to ADR-0121 for ROI and spend telemetry.
6.  **`generate_doc_system_map.py`**: Linked to ADR-0124 for documentation hierarchy visualization.

## Benefits
- **Audit Compliance**: Every script is now multi-dimensionally traceable.
- **Improved Context**: New joiners can find the "why" behind every utility script by following the link back to the ADR.
- **Gate Stability**: Resolves CI blockers in the `PR Guardrails` suite.

## Next Steps
- Continue periodic audits using `check_script_traceability.py`.
