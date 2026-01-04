---
id: CL-0028
title: 'CL-0028: Dev-branch apply workflow and changelog exemption'
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
- CL-0028
------

# CL-0028: Dev-branch apply workflow and changelog exemption

Date: 2026-01-03
Owner: platform
Scope: CI/CD guardrails
Related: PR #125

## Summary

- add a dev-branch apply workflow for ephemeral dev builds
- allow `changelog-exempt` to skip changelog enforcement

## Impact

- dev-branch applies can be run with explicit confirmation and matching plan
- test-only changes can skip changelog entry when explicitly labeled

## Changes

### Added

- workflow: `.github/workflows/infra-terraform-apply-dev-branch.yml`
- label: `changelog-exempt`

### Changed

- changelog guardrail honors `changelog-exempt`

## Rollback / Recovery

- Remove the dev-branch workflow and the exemption check if needed.

## Validation

- Not run (workflow change)
