---
id: CL-0011-app-template-contract
title: 'CL-0011: App template contract and reference bundle'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
version: '1.0'
lifecycle: active
relates_to:
  - 42_APP_TEMPLATE_LIVING
  - ADR-0062
  - ADR-0062-platform-app-template-contract
  - CL-0011
supported_until: 2027-01-04
breaking_change: false
---

# CL-0011: App template contract and reference bundle

Date: 2025-12-31
Owner: platform
Scope: app onboarding, deployment templates
Related: `apps/fast-api-app-template/`, `docs/adrs/ADR-0062-platform-app-template-contract.md`, `docs/20-contracts/42_APP_TEMPLATE_LIVING.md`

## Summary

- Add a reference app template bundle with explicit platform vs app ownership.
- Publish a living doc for the template structure and boundaries.

## Impact

- App teams get a consistent starting point for deployments.
- Platform ownership boundaries are explicit and reviewable.

## Changes

### Added

- `apps/fast-api-app-template/` reference manifests with placeholders.
- `docs/20-contracts/42_APP_TEMPLATE_LIVING.md` living structure doc.
- ADR-0062 to document the contract.

### Documented

- Template ownership boundaries and update expectations.

## Rollback / Recovery

- Revert the template and ADR if the contract changes.

## Validation

- Not run (documentation/template change).
