---
id: CL-0095-ecr-backstage-sync-automation
title: 'CL-0095: ECR Backstage sync automation'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0128
  - ADR-0129
  - ADR-0132
  - CL-0095
supported_until: 2028-01-09
breaking_change: false
---

# CL-0095: ECR Backstage sync automation

Date: 2026-01-09
Owner: platform-team
Scope: Backstage catalog, ECR governance
Related: docs/adrs/ADR-0128-automated-ecr-catalog-sync.md

## Summary

- automate Backstage ECR catalog sync after registry PR merge

## Impact

- Backstage ECR registry entity updates via a PR after successful apply
- human approval remains required (HITL)

## Changes

### Added

- `.github/workflows/ecr-backstage-sync.yml`

### Changed

- runbook `RB-0025` updated to document automation

## Rollback / Recovery

- Disable or remove the workflow

## Validation

- Workflow run opens a PR after ECR auto-apply succeeds

## Notes

- Manual workflow dispatch testing is deferred until the workflow is promoted to `main`.
