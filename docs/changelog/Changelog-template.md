---
id: Changelog-template
title: 'CL-0001: <short title>'
type: changelog
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle: active
version: '1.0'
relates_to:
  - CL-0001
supported_until: 2028-01-01
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

- <docs/runbooks/ADR updates>

### Known limitations

- <known gaps or risks>

## Rollback / Recovery

- <rollback steps or "Not required">

## Validation

- <tests, runs, or evidence>
