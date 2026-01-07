---
id: CL-0007-ci-force-unlock-workflow
title: 'CL-0007: CI force-unlock workflow'
type: changelog
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
version: '1.0'
lifecycle: active
relates_to:
  - CL-0007
supported_until: 2027-01-04
breaking_change: false
---

# CL-0007: CI force-unlock workflow

Date: 2025-12-31
Owner: platform
Scope: terraform/ci
Related: .github/workflows/ci-force-unlock.yml, docs/70-operations/runbooks/07_TF_STATE_FORCE_UNLOCK.md

## Summary

- Add a break-glass CI workflow to force-unlock Terraform state.

## Impact

- Operators can clear stale state locks without local access.

## Changes

### Added

- `CI Force Unlock` workflow with explicit confirmation input.
- Runbook for safe usage and lock discovery.

### Changed

- Teardown documentation now references the workflow.

### Fixed

- None.

### Deprecated

- None.

### Removed

- None.

### Documented

- Added runbook and references.

### Known limitations

- Misuse can unlock active Terraform runs.

## Rollback / Recovery

- Remove the workflow and runbook if break-glass is not desired.

## Validation

- Not run (manual workflow run required).
