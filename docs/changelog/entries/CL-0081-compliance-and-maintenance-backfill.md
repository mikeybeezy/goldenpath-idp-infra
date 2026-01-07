---
id: CL-0081
title: 'CL-0081: Compliance & Maintenance Backfill'
type: changelog
lifecycle: active
schema_version: 1
relates_to:
  - ADR-0125
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
