---
id: CL-0006
title: 'CL-0006: Loki single-binary default and monitoring namespace'
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

- CL-0006

---

# CL-0006: Loki single-binary default and monitoring namespace

Date: 2025-12-31
Owner: platform
Scope: observability
Related: gitops/argocd/apps/*/loki.yaml, gitops/helm/loki/values/*.yaml

## Summary

- Set Loki to Single Binary mode by default.
- Deploy Loki into the `monitoring` namespace.

## Impact

- Loki runs with a simpler topology by default.
- Loki now lives alongside the rest of the monitoring stack.

## Changes

### Added

- Explicit Single Binary mode settings in Loki values files.

### Changed

- Argo CD Loki apps now target the `monitoring` namespace.

### Fixed

- None.

### Deprecated

- None.

### Removed

- None.

### Documented

- Updated Loki README and observability decisions.

### Known limitations

- Single Binary mode is not HA and scales less than Simple Scalable.

## Rollback / Recovery

- Switch Loki values to Simple Scalable mode and deploy to a dedicated namespace if needed.

## Validation

- Not run (Argo CD will reconcile).
