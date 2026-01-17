---
id: CL-0102-backstage-docs-linkout
title: 'CL-0102: Backstage docs link-out (no TechDocs build)'
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
  - ADR-0133
  - CL-0102-backstage-docs-linkout
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0102: Backstage docs link-out (no TechDocs build)

Date: 2026-01-10
Owner: platform-team
Scope: backstage-helm catalog docs
Related: ADR-0133

## Summary

- Backstage doc entities now link directly to GitHub instead of using TechDocs.
- `scripts/generate_backstage_docs.py` updated to emit view/edit links and remove TechDocs refs.

## Impact

- Backstage shows GitHub links for ADRs, changelogs, and governance docs.
- No TechDocs build pipeline is required for doc visibility.

## Changes

### Changed

- Backstage doc entity generator now writes `backstage.io/view-url` and `backstage.io/edit-url`.
- TechDocs annotations removed from generated entities.

### Documented

- Catalog components point to `main` for source links.

## Rollback / Recovery

- Git revert this changelog and regenerate catalog docs if needed.

## Validation

- `python3 scripts/generate_backstage_docs.py`
