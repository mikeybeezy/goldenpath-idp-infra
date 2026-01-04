---
id: CL-0008-ci-managed-lb-cleanup-workflow
title: 'CL-0008: CI managed LB cleanup workflow'
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
- 08_MANAGED_LB_CLEANUP
- CL-0008
---

# CL-0008: CI managed LB cleanup workflow

Date: 2025-12-31
Owner: platform
Scope: CI teardown recovery
Related: `.github/workflows/ci-managed-lb-cleanup.yml`, `docs/runbooks/08_MANAGED_LB_CLEANUP.md`

## Summary

- Add a CI workflow to delete LBC-managed LBs, ENIs, and security groups when
  cluster access is gone and VPC deletion is blocked.

## Impact

- Operators can recover stuck teardowns without kube access by running a
  tag-scoped, AWS-only cleanup workflow.

## Changes

### Added

- `CI Managed LB Cleanup` workflow and runbook.
- Optional deletion of security groups tagged with `elbv2.k8s.aws/cluster`.

### Documented

- Teardown recovery guidance updated to reference the new workflow.

### Known limitations

- Cleanup is tag-scoped; if tags are missing or inconsistent, manual recovery
  may still be required.

## Rollback / Recovery

- Not required.

## Validation

- Not run (manual workflow).
