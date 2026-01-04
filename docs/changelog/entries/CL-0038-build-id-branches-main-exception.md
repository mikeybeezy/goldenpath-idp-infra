---
id: CL-0038
title: Allow build-id branches to merge to main
type: changelog
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: low
relates_to:
- CL-0038
------

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
