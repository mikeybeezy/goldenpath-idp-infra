---
id: CL-0005-teardown-finalizer-default-on
title: 'CL-0005: Teardown finalizer removal default-on'
type: changelog
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-04
  breaking_change: false
relates_to:
- CL-0005
---

# CL-0005: Teardown finalizer removal default-on

Date: 2025-12-31
Owner: platform
Scope: teardown
Related: bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh, .github/workflows/ci-teardown.yml

## Summary

- Default v2 teardown to remove stuck LoadBalancer Service finalizers to avoid
  teardown hangs when the LB controller is unavailable.

## Impact

- Teardown will force-delete stuck LoadBalancer Service finalizers unless explicitly disabled.

## Changes

### Added

- None.

### Changed

- `FORCE_DELETE_LB_FINALIZERS` now defaults to `true` in v2 teardown and CI workflow inputs.

### Fixed

- Reduce teardown stalls caused by Service finalizers when the LB controller is unavailable.

### Deprecated

- None.

### Removed

- None.

### Documented

- Updated teardown docs and runbook to reflect the new default.

### Known limitations

- Finalizer removal should only be used for disposable services in teardown.

## Rollback / Recovery

- Set `FORCE_DELETE_LB_FINALIZERS=false` to restore prior behavior.

## Validation

- Not run (manual teardown required).
