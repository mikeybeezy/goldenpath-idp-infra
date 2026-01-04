---
id: CL-0017
title: "CL-0017: Fix review cadence output delimiter"
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
relates_to: []
---

# CL-0017: Fix review cadence output delimiter

Date: 2026-01-02
Owner: platform
Scope: CI, governance
Related: PR #108, `docs/adrs/ADR-0068-platform-review-cadence-output.md`

## Summary

- Fix the `GITHUB_OUTPUT` heredoc delimiter in the review cadence workflow.

## Impact

- Review cadence checks no longer fail due to output parsing.

## Changes

### Fixed

- Corrected output delimiter in `.github/workflows/production-readiness-review.yml`.

### Documented

- Added ADR for the review cadence output fix.

## Rollback / Recovery

- Revert the delimiter change in `.github/workflows/production-readiness-review.yml`.

## Validation

- Review cadence workflow completes without output parsing errors.
