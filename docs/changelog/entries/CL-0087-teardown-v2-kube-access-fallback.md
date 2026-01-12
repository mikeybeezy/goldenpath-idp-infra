---
id: CL-0087-teardown-v2-kube-access-fallback
title: 'CL-0087: Teardown v2 kube access fallback'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - CL-0087
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-04
version: '1.0'
breaking_change: false
---

# CL-0087: Teardown v2 kube access fallback

Date: 2025-12-31
Owner: platform
Scope: teardown
Related: bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh, .github/workflows/ci-teardown.yml

## Summary

- Add a Kubernetes access check to v2 teardown and fall back to AWS-only cleanup.
- Expose break-glass finalizer removal in CI inputs.

## Impact

- Teardown no longer hangs when Kubernetes access is lost.
- Operators can trigger finalizer removal from CI without editing code.

## Changes

### Added

- `force_delete_lb_finalizers` workflow input (maps to `FORCE_DELETE_LB_FINALIZERS`).
- AWS-only cleanup path when Kubernetes API is unreachable.

### Changed

- v2 teardown skips Kubernetes cleanup stages when kube access fails.

### Fixed

- Avoid indefinite waits on LoadBalancer services when Kubernetes access is lost.

### Deprecated

- None.

### Removed

- None.

### Documented

- Updated teardown docs and runbook guidance for kube-access fallback.

### Known limitations

- AWS-only cleanup cannot remove Kubernetes finalizers.

## Rollback / Recovery

- Re-run teardown with Kubernetes access restored to remove stuck Services.

## Validation

- Not run (manual teardown required).
