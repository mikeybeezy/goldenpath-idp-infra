---
id: CL-0090-backstage-plugin-enablement-matrix
title: 'CL-0090: Backstage plugin enablement matrix'
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
  - CL-0090-backstage-plugin-enablement-matrix
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-08
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0090: Backstage plugin enablement matrix

Date: 2026-01-08
Owner: platform-team
Scope: backstage helm docs
Related: backstage-helm/PLUGIN_ENABLEMENT_MATRIX.md

## Summary

- document which Backstage plugins can be enabled via Helm config vs requiring a custom image
- add a V1 recommendation matrix with enabled status

## Impact

- clarifies plugin feasibility without affecting runtime behavior

## Changes

### Added

- `backstage-helm/PLUGIN_ENABLEMENT_MATRIX.md` with config-only guidance and V1 matrix

### Documented

- V1 plugin recommendations and enablement status

## Rollback / Recovery

- Not required

## Validation

- Not run (documentation update)
