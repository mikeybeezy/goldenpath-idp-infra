---
id: CL-0101
title: 'CL-0101: Doc scaffold + metadata auto-fix'
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
  - ADR-0140
  - CL-0101
  - METADATA_STRATEGY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-10
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0101: Doc scaffold + metadata auto-fix

Date: 2026-01-10
Owner: platform-team
Scope: docs/ (Markdown authoring flow)
Related: ADR-0140

## Summary

- Add a doc scaffold script to generate compliant metadata headers.
- Normalize doc metadata automatically in pre-commit for changed Markdown files.
- Keep CI validation as the backstop for metadata drift.

## Impact

- Authors get compliant headers at creation time.
- PRs should fail less often due to missing metadata.

## Changes

### Added

- `scripts/scaffold_doc.py` for policy-aligned doc creation.

### Changed

- Pre-commit now runs metadata normalization for changed docs under `docs/`.

### Fixed

- Reduced late-stage metadata failures by auto-fixing headers locally.

### Documented

- Updated metadata strategy and validation guides for the new workflow.

## Rollback / Recovery

- Revert this changelog and remove the pre-commit hook and scaffold script.

## Validation

- Run `python3 scripts/validate_metadata.py docs` locally or rely on CI.
