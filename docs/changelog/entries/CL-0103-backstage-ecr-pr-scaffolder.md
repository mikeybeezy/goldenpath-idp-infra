---
id: CL-0103
title: 'CL-0103: Backstage ECR scaffolder creates PRs directly'
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
  - CL-0103
  - ADR-0095
  - ADR-0128
supported_until: 2028-01-01
breaking_change: false
---

# CL-0103: Backstage ECR scaffolder creates PRs directly

Date: 2026-01-10
Owner: platform-team
Scope: Backstage scaffolder, ECR registry workflow
Related: PR #202, docs/adrs/ADR-0095-self-service-registry-creation.md, docs/adrs/ADR-0128-automated-ecr-catalog-sync.md

## Summary

- Replace GitHub Actions dispatch with Backstage PR creation for ECR registry requests.
- Update the ECR scaffold script to write both tfvars and the governance catalog.

## Impact

- Users now get a direct PR link from Backstage instead of a workflow-run link.
- ECR catalog updates stay aligned with the PR contents.

## Changes

### Added

- Backstage scaffolder steps to fetch repo, update files, and open a PR.
- Catalog update support in `scripts/scaffold_ecr.py`.

### Changed

- ECR request template output now links to the PR as the primary success signal.

### Fixed

- Eliminates “workflow-only” links that don’t point to the created PR.

### Deprecated

- None.

### Removed

- None.

### Documented

- No new documentation; template output updated.

### Known limitations

- Requires Backstage actions `fetch:plain`, `command:execute`, and `publish:github:pull-request` to be enabled.

## Rollback / Recovery

- Revert PR #202.

## Validation

- Not run (template + script change).
