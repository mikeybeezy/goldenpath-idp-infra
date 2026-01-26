---
id: CL-0012-backstage-ci-apply-dev-template
title: 'CL-0012: Backstage template for dev Terraform apply'
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
  - CL-0012-backstage-ci-apply-dev-template
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-04
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

## CL-0012: Backstage template for dev Terraform apply

Date: 2025-12-31
Owner: platform
Scope: Backstage, CI workflow UX
Related: `backstage-helm/backstage-catalog/templates/ci-apply-dev/template.yaml`, `.github/workflows/infra-terraform-apply-dev.yml`

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

---

**Historical Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
- `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
- `backstage-helm/backstage-catalog/` → `catalog/`
