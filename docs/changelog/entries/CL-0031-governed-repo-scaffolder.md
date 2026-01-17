---
id: CL-0031-governed-repo-scaffolder
title: 'CL-0031: Governance-driven app repo scaffolder'
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
  - 00_INDEX
  - 42_APP_TEMPLATE_LIVING
  - ADR-0078-platform-governed-repo-scaffolder
  - CL-0031-governed-repo-scaffolder
  - US-0001-governance-driven-repo-scaffolder
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
## CL-0031: Governance-driven app repo scaffolder

Date: 2026-01-03
Owner: platform
Scope: backstage templates, workflows, app template
Related: docs/adrs/ADR-0078-platform-governed-repo-scaffolder.md

## Summary

- Add a workflow-driven repo scaffolder that renders the Golden Path app template.
- Extend the Backstage app template with governance metadata inputs.
- Document the scaffolder metadata contract.

## Impact

- New app repos can be created with consistent ownership, lifecycle, and data
  classification metadata.
- Backstage now exposes the app template alongside the CI apply template.

## Changes

### Added

- Workflow: `.github/workflows/repo-scaffold-app.yml`.
- Template renderer: `scripts/render-template.py`.
- ADR: `docs/adrs/ADR-0078-platform-governed-repo-scaffolder.md`.

### Changed

- `backstage-helm/backstage-catalog/templates/app-template/template.yaml` uses governance inputs and
  registers `catalog-info.yaml` at repo root.
- `apps/fast-api-app-template/catalog-info.yaml` includes governance annotations.
- Backstage catalog locations include the app template in all envs.

### Documented

- `docs/20-contracts/42_APP_TEMPLATE_LIVING.md` updated with scaffolder inputs.

## Rollback / Recovery

- Remove the workflow and revert the app template changes.

## Validation

- Not run (template/workflow change only).
