---
id: CL-0094-backstage-docs-pr-workflow
title: 'CL-0094: Backstage docs PR workflow'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0133
  - CL-0094-backstage-docs-pr-workflow
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
# CL-0094: Backstage docs PR workflow

Date: 2026-01-09
Owner: platform-team
Scope: CI/CD, documentation automation
Related: docs/adrs/ADR-0133-human-in-the-loop-backstage-docs-prs.md

## Summary

- add a workflow that generates Backstage catalog docs and opens a PR for review

## Impact

- doc catalog updates are automated but still require human approval

## Changes

### Added

- `.github/workflows/backstage-docs-pr.yml`

### Documented

- HITL policy captured in ADR-0133

## Rollback / Recovery

- Disable or remove the workflow

## Validation

- Workflow run produces a PR when docs change
