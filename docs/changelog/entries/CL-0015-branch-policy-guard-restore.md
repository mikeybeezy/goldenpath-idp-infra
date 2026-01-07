---
id: CL-0015-branch-policy-guard-restore
title: 'CL-0015: Restore branch policy guard for main'
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
  - ADR-0065
  - ADR-0065-platform-branch-policy-guard
  - CL-0015
supported_until: 2027-01-04
breaking_change: false
---

# CL-0015: Restore branch policy guard for main

Date: 2026-01-02
Owner: platform
Scope: CI, governance
Related: PR #104, `docs/adrs/ADR-0065-platform-branch-policy-guard.md`

## Summary

- Restore the branch policy guard to require development -> main merges.

## Impact

- Direct merges from non-development branches to main are blocked.

## Changes

### Changed

- Reinforced `development` as the only allowed source branch for main merges.

### Documented

- Added ADR for the branch policy guard restoration.

## Rollback / Recovery

- Revert the branch policy guard change in `.github/workflows/branch-policy.yml`.

## Validation

- CI guardrails enforce the policy on pull requests to main.
