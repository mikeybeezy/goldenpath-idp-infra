---
id: CL-0091-platform-health-outcome-metrics
title: 'CL-0091: Platform health outcome metrics proposal'
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
  - ADR-0131
  - CL-0091-platform-health-outcome-metrics
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-08
version: '1.0'
breaking_change: false
---

## CL-0091: Platform health outcome metrics proposal

Date: 2026-01-08
Owner: platform-team
Scope: governance, health reporting
Related: docs/adrs/ADR-0131-platform-health-outcome-metrics.md

## Summary

- propose outcome metrics for the platform health dashboard
- add a matrix of recommended metrics, sources, and effort
- extend catalog scans to include `docs/20-contracts/resource-catalogs`

## Impact

- improves visibility into delivery outcomes without changing runtime behavior

## Changes

### Added

- `PLATFORM_HEALTH_PROPOSED_UPDATES.md` with outcome metric proposals
- ADR for outcome metric adoption

### Changed

- platform health catalog scan now includes `docs/20-contracts/resource-catalogs`

### Documented

- ECR time-to-ready metric proposal

## Rollback / Recovery

- Not required

## Validation

- `python3 scripts/platform_health.py`
