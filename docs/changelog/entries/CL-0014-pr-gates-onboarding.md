---
id: CL-0014
title: 'CL-0014: PR gate onboarding guide'
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

- 24_PR_GATES
- CL-0014

---

# CL-0014: PR gate onboarding guide

Date: 2026-01-02
Owner: platform
Scope: Docs, onboarding
Related: PR #105

## Summary

- Document PR gate checks, triggers, and expected remediation steps in onboarding.

## Impact

- Developers have a single reference to understand why PRs are blocked and how to resolve them.

## Changes

### Documented

- Added `docs/80-onboarding/24_PR_GATES.md` and linked it from onboarding and the doc index.

## Rollback / Recovery

- Not required.

## Validation

- Docs-only change.
