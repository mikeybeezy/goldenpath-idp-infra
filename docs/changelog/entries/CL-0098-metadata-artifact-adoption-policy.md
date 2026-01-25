---
id: CL-0098
title: 'CL-0098: Metadata placement policy for configs and reports'
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
  - ADR-0137
  - CL-0098
  - METADATA_ARTIFACT_ADOPTION_POLICY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-09
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0098: Metadata placement policy for configs and reports

Date: 2026-01-09
Owner: platform-team
Scope: governance, metadata, reporting
Related: ADR-0137, docs/10-governance/METADATA_ARTIFACT_ADOPTION_POLICY.md

## Summary

- Standardize metadata placement for configs and reports using sidecars.
- Add initial inventory config, report artifacts, and inventory generator script.
- Add governance references for Backstage and living docs index.

## Impact

- No runtime impact. Improves governance clarity and traceability.

## Changes

### Added

- Metadata placement policy doc for configs and reports.
- Inventory config, report artifacts, and `scripts/aws_inventory.py`.
- Backstage governance catalog entry for the new policy doc.

### Documented

- Living docs index updated to include the policy doc.

## Rollback / Recovery

- Revert this changelog and the associated policy/config/report files.

## Validation

- Not required (documentation and configuration only).
