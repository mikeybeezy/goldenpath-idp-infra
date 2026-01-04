---
id: CL-0012-backstage-ci-apply-dev-template
title: 'CL-0012: Backstage template for dev Terraform apply'
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
- CL-0012
---

# CL-0012: Backstage template for dev Terraform apply

Date: 2025-12-31
Owner: platform
Scope: Backstage, CI workflow UX
Related: `backstage/templates/ci-apply-dev/template.yaml`, `.github/workflows/infra-terraform-apply-dev.yml`

## Summary

- Add a Backstage Scaffolder template to trigger the dev Terraform apply workflow.

## Impact

- Developers can launch the dev apply workflow from Backstage with guardrails.

## Changes

### Added

- `CI Apply (dev)` Backstage template and catalog location in Backstage values.

## Rollback / Recovery

- Remove the template file and catalog location.

## Validation

- Not run (manual workflow).
