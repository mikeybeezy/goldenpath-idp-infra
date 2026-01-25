<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: Changelog-template
title: 'CL-0001: <short title>'
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
  - 40_CHANGELOG_GOVERNANCE
  - CHANGELOG_LABELS
  - CL-0001-teardown-kubectl-timeout-guard
  - DOCS_CHANGELOG_README
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0001: <short title>

Date: <YYYY-MM-DD>
Owner: <team or person>
Scope: <envs or components>
Related: <ADR/PR/Issue links>

## Summary

- <1-3 bullets of what changed and why>

## Impact

- <who is affected and what changes in behavior>

## Changes

### Added

- <new capability>

### Changed

- <behavior or contract change>

### Fixed

- <operational fix>

### Deprecated

- <deprecated behavior>

### Removed

- <removed behavior>

### Documented

- <docs/70-operations/runbooks/ADR updates>

### Known limitations

- <known gaps or risks>

## Rollback / Recovery

- <rollback steps or "Not required">

## Validation

- <tests, runs, or evidence>
