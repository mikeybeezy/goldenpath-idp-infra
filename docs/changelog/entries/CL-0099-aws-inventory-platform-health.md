---
id: CL-0099
title: 'CL-0099: AWS inventory in platform health'
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
  - PLATFORM_HEALTH
supported_until: 2028-01-09
breaking_change: false
---

# CL-0099: AWS inventory in platform health

Date: 2026-01-09
Owner: platform-team
Scope: governance, reporting
Related: scripts/aws_inventory.py, PLATFORM_HEALTH.md

## Summary

- Add an AWS inventory snapshot to the platform health report.

## Impact

- No runtime impact. Improves visibility into tagged/untagged resources.

## Changes

### Added

- Loader in `scripts/platform_health.py` to read the latest AWS inventory report.

### Documented

- Platform health report now includes an AWS inventory snapshot section.

## Rollback / Recovery

- Revert this changelog and the platform health loader changes.

## Validation

- Run `python3 scripts/aws_inventory.py --config inventory-config.yaml` and
  `python3 scripts/platform_health.py`.
