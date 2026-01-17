---
id: CL-0028-dev-branch-apply-workflow
title: 'CL-0028: Dev-branch apply workflow and changelog exemption'
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
  - CL-0028-dev-branch-apply-workflow
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
