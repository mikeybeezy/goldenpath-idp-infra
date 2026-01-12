---
id: CL-0097
title: 'CL-0097: Tooling config identity sidecars'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0136
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-09
version: '1.0'
breaking_change: false
---

# CL-0097: Tooling config identity sidecars

Date: 2026-01-09
Owner: platform-team
Scope: governance tooling configs
Related: ADR-0136

## Summary

- Add metadata sidecars for root tooling configs to make ownership and audit
  trails explicit.

## Impact

- No runtime behavior changes.
- Additional metadata files accompany tooling configs.

## Changes

### Added

- Sidecar metadata for `.pre-commit-config.yaml`, `.yamllint`,
  `.markdownlint.json`, and `mkdocs.yml`.
- ADR-0136 documents the identity-sidecar pattern.

### Known limitations

- Enforcement is advisory until validators are extended.

## Rollback / Recovery

- Remove the sidecar files and revert the ADR/CL if needed.

## Validation

- `python3 scripts/validate_metadata.py .`
