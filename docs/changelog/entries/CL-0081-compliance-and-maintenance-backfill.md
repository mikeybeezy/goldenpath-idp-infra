<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0081
title: 'CL-0081: Compliance & Maintenance Backfill'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0125
  - CL-0081
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
---

# CL-0081: Compliance & Maintenance Backfill

Date: 2026-01-07
Owner: platform-team
Scope: Governance
Related: ADR-0125

## Summary

This entry backfills the governance record for the Compliance & Maintenance suite, which handles metadata health, migrations, and platform reliability reporting.

## Changes

### Added
- `scripts/check_compliance.py`: Compliance scanner.
- `scripts/fix_yaml_syntax.py`: Template repair.
- `scripts/migrate_partial_metadata.py`: Bulk schema migration.
- `scripts/backfill_metadata.py`: Tag injection.
- `scripts/reliability-metrics.sh`: Metric dashboard feeder.
- `scripts/test_platform_health.py`: Logic validation.
- `scripts/test_hotfix.py`: Guardrail tests.
- `scripts/render_template.py`: Template rendering.

## Validation

- Verified via `bin/governance lint` and regular automated compliance audits.
