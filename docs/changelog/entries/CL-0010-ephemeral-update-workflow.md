---
id: CL-0010-ephemeral-update-workflow
title: 'CL-0010: Dev ephemeral update workflow'
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
  - ADR-0060-platform-ephemeral-update-workflow
  - CL-0010-ephemeral-update-workflow
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
# CL-0010: Dev ephemeral update workflow

Date: 2025-12-31
Owner: platform
Scope: CI, dev, Terraform
Related: `.github/workflows/infra-terraform-update-dev.yml`, `ci-workflows/CI_WORKFLOWS.md`, `docs/adrs/ADR-0060-platform-ephemeral-update-workflow.md`

## Summary

- Add a manual dev update workflow for existing ephemeral BuildIds with plan and state guards.

## Impact

- Operators can apply changes to an existing ephemeral dev cluster without relaxing the new-build guard.
- Updates are gated by a successful plan and an existing state key.

## Changes

### Added

- `Apply - Infra Terraform Update (dev)` workflow for update-only applies.

### Documented

- Workflow index updated to include the new update path.

### Known limitations

- Dev-only for now; other environments require follow-up.

## Rollback / Recovery

- Remove the update workflow and use the standard apply path with new BuildIds.

## Validation

- Not run (manual workflow).
