---
id: CL-0022-pr-guardrails-template-copy
title: 'CL-0022: PR guardrails template copy'
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
  - 24_PR_GATES
  - ADR-0072
  - CL-0022
---

# CL-0022: PR guardrails template copy

Date: 2026-01-02
Owner: platform
Scope: docs
Related: docs/adrs/ADR-0072-platform-pr-checklist-template.md, PR #114

## Summary

Added a copy of the PR checklist template to the PR gates guide to reduce
guardrail friction for contributors.

## Changes

### Changed

- `docs/80-onboarding/24_PR_GATES.md`: added the checklist template block.

## Validation

- Not required (documentation only).
