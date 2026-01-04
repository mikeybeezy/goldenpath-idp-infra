---
id: CL-0003
title: 'CL-0003: Teardown v2 LoadBalancer finalizer guard'
type: changelog
owner: platform-team
status: active
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

- CL-0003

---

# CL-0003: Teardown v2 LoadBalancer finalizer guard

Date: 2025-12-31
Owner: platform
Scope: teardown
Related: bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh, docs/70-operations/15_TEARDOWN_AND_CLEANUP.md

## Summary

- Reorder v2 teardown cleanup to avoid LoadBalancer Service finalizer deadlocks.
- Add a break-glass flag to remove stuck LoadBalancer Service finalizers.

## Impact

- v2 teardown no longer hangs when LB Services are stuck in `Terminating`.
- Operators can force finalizer removal when the LB controller cannot clear it.

## Changes

### Added

- `FORCE_DELETE_LB_FINALIZERS` and `LB_FINALIZER_WAIT_MAX` flags for v2 teardown.
- Cluster existence preflight to skip Kubernetes stages if the cluster is gone.

### Changed

- Scale down the LB controller only after LB Services are deleted.

### Fixed

- Prevent teardown stalling at Stage 2 when the LB controller is not running.

### Deprecated

- None.

### Removed

- None.

### Documented

- Updated teardown docs and runbook guidance for stuck finalizers.

### Known limitations

- Finalizer removal should only be used for disposable resources.

## Rollback / Recovery

- Disable v2 or unset `FORCE_DELETE_LB_FINALIZERS`.

## Validation

- Not run (manual teardown required).
