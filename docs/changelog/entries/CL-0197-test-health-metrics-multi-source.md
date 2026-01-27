---
id: CL-0197-test-health-metrics-multi-source
title: 'CL-0197: Multi-source test health metrics capture'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - ci
  - governance-registry
  - platform-health
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
  - PRD-0007-platform-test-health-dashboard
  - ADR-0183-test-health-metrics-schema
  - CL-0190-tdd-foundation-and-testing-stack
supersedes: []
superseded_by: []
tags:
  - testing
  - metrics
  - governance
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: ⚪ MV/LQ
  impact_tier: medium
  potential_savings_hours: 6.0
version: '1.0'
breaking_change: false
---

# CL-0197: Multi-source test health metrics capture

Date: 2026-01-26  
Owner: platform-team  
Scope: CI test metrics, governance-registry sync, Platform Health dashboard  
Related: PRD-0007, ADR-0183

## Summary

- Standardized test-metrics capture for infra bats + Backstage Jest.
- Added terraform test (-json) metrics capture for module tests.
- Added governance-registry sync path for Backstage test metrics.
- Updated Platform Health to render multi-source Test Health.

## Impact

- Test health metrics are now visible for infra and Backstage in the governance registry.
- Platform Health surfaces pass/fail/coverage status across both repos.

## Changes

### Added

- Test-metrics record step for bats tests.
- Backstage metrics ingestion into infra governance-registry sync.

### Changed

- Platform Health “Test Health Metrics” renders multiple sources.

### Fixed

- n/a

### Deprecated

- n/a

### Removed

- n/a

### Documented

- Session capture updated with dependencies and branch setup details.

### Known limitations

- Backstage import requires `BACKSTAGE_REPO_TOKEN` (read access) in infra.

## Rollback / Recovery

- Revert changes in CI workflows and `scripts/platform_health.py`.

## Validation

- Pending: next CI runs on infra + Backstage should publish test_metrics.json to governance-registry.
