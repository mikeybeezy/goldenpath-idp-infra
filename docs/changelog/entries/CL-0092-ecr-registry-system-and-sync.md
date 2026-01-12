---
id: CL-0092-ecr-registry-system-and-sync
title: 'CL-0092: ECR registry system boundary and sync updates'
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
  - ADR-0132
  - CL-0092
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

# CL-0092: ECR registry system boundary and sync updates

Date: 2026-01-09
Owner: platform-team
Scope: Backstage catalog, ECR sync
Related: docs/adrs/ADR-0132-platform-container-registry-system.md

## Summary

- model ECR registry as its own Backstage system
- make the ECR sync script region-portable and align output to AWS state
- document ECR catalog sync in an operations runbook

## Impact

- Backstage now groups ECR assets under a dedicated system boundary
- sync output reflects the physical AWS registry count for a given region

## Changes

### Added

- `backstage-helm/catalog/systems/container-registry-system.yaml`
- `backstage-helm/catalog/domains/delivery-domain.yaml`
- `docs/70-operations/runbooks/RB-0025-ecr-catalog-sync.md`

### Changed

- ECR component/resource system mapped to `container-registry`
- `scripts/sync_ecr_catalog.py` now accepts `--region` and uses AWS as source of truth
- `backstage-helm/catalog/all-systems.yaml` and `all-domains.yaml` include new entries

### Documented

- ECR catalog sync process and region configuration guidance

## Rollback / Recovery

- Revert the system/domain catalog entries and restore the prior sync output.

## Validation

- `python3 scripts/sync_ecr_catalog.py --region eu-west-2`
