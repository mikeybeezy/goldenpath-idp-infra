---
id: CL-0038-build-id-branches-main-exception
title: Allow build-id branches to merge to main
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - CL-0038-build-id-branches-main-exception
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
## CL-0038: Allow build-id branches to merge to main

Date: 2026-01-03
Author: Antigravity

## Summary

Allow build-id branches to merge into `main` alongside `development` for build validation runs.

## Changes

- Branch policy guard accepts head refs matching `build-<dd-mm-yy-NN>` or `build/<dd-mm-yy-NN>` when targeting `main`.
- PR guardrails documentation updated to describe the exception.

## Impact

- `main` still requires PRs and checks, but build validation branches are no longer blocked.
