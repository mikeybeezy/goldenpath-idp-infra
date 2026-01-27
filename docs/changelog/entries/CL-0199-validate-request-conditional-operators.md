---
id: CL-0199-validate-request-conditional-operators
title: Fix missing conditional rule operators in bespoke schema validator
type: changelog
domain: governance
applies_to:
  - policies
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
  maturity: 2
schema_version: 1
relates_to:
  - EC-0016-bespoke-schema-validator
  - SCRIPT-0062
supersedes: []
superseded_by: []
tags:
  - bug-fix
  - governance
  - validation
inheritance: {}
status: active
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0199: Fix missing conditional rule operators in bespoke schema validator

## Summary

Fixed a bug in `scripts/validate_request.py` where the `_validate_conditional_rule` function only checked `required` and `equals` operators, silently ignoring other operators used in request schemas like `rds.schema.yaml`.

## Problem

The RDS schema defines conditional rules using operators that were not implemented:
- `minimum` (prod_requires_backup) - not enforced
- `enum` (dev_max_size) - not enforced
- `greater_than_field` (storage_max_must_exceed_allocated) - not enforced
- `defined` in when conditions - not evaluated
- `recommended` with warnings - not generated

This allowed invalid requests to pass validation, defeating governance constraints.

## Fix

Added support for all conditional rule operators:

| Operator | Purpose | Example |
|----------|---------|---------|
| `minimum` | value >= N | `backupRetentionDays >= 14` for prod |
| `maximum` | value <= N | (new capability) |
| `enum` | value in list | `size` in `['small']` for dev |
| `greater_than_field` | field > other_field | `maxStorageGb > storageGb` |
| `defined` | field is present | Check if optional field exists |
| `recommended` | warning not error | Multi-AZ recommendation for prod |

## Tests Added

13 new tests covering all operators plus integration test with RDS schema.

## Files Changed

- `scripts/validate_request.py` - Added operator implementations
- `tests/scripts/test_validate_request.py` - Added 13 new tests

## Validation

```bash
pytest tests/scripts/test_validate_request.py -v
# 41 tests, all passing
```

## Impact

- Governance constraints in RDS schema are now properly enforced
- Invalid requests (e.g., prod with 7-day backups) will fail validation
- No breaking changes to valid requests
