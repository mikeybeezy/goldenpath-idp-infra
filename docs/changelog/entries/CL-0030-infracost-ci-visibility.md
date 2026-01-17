---
id: CL-0030-infracost-ci-visibility
title: 'CL-0030: Lightweight CI cost visibility (Infracost)'
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
  - ADR-0076-platform-infracost-ci-visibility
  - CL-0030-infracost-ci-visibility
  - CL-0050-infracost-activation
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
# CL-0030: Lightweight CI cost visibility (Infracost)

Date: 2026-01-03
Owner: platform
Scope: CI, governance
Related: docs/adrs/ADR-0076-platform-infracost-ci-visibility.md, docs/10-governance/06_COST_GOVERNANCE.md, docs/70-operations/40_COST_VISIBILITY.md

## Summary

- Add lightweight Infracost cost visibility to PR Terraform plans.
- Define governance and operational guidance for cost visibility.

## Impact

- PRs gain cost visibility comments when `INFRACOST_API_KEY` is configured.
- No gating or budget thresholds are enforced in V1.

## Changes

### Added

- Infracost setup and comment steps in the PR Terraform plan workflow.
- Cost governance policy and operational runbook docs.
- ADR documenting the decision.

### Changed

- None.

### Fixed

- None.

### Deprecated

- None.

### Removed

- None.

### Documented

- Cost governance and cost visibility implementation.

### Known limitations

- Advisory only; no baseline diff or budget thresholds yet.

## Rollback / Recovery

- Not required. Remove the Infracost steps from the PR plan workflow if needed.

## Validation

- Not run (workflow/doc change).
