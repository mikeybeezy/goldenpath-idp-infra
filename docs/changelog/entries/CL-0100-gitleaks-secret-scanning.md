---
id: CL-0100
title: 'CL-0100: Gitleaks secret scanning'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: medium
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 10_SECRET_SCANNING_POLICY
  - CL-0100
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-10
version: '1.0'
breaking_change: false
---
# CL-0100: Gitleaks secret scanning

Date: 2026-01-10
Owner: platform-team
Scope: security, governance, CI
Related: .github/workflows/gitleaks.yml, .pre-commit-config.yaml

## Summary

- Add Gitleaks scanning to pre-commit and CI.
- Publish a governance policy for secret scanning.

## Impact

- PRs to `main` fail if secrets are detected.
- Developers must pass Gitleaks locally before pushing.

## Changes

### Added

- `Security - Gitleaks` workflow for PRs to `main`.
- Gitleaks hook in `.pre-commit-config.yaml`.
- Secret scanning policy in `docs/10-governance/10_SECRET_SCANNING_POLICY.md`.

### Documented

- Governance rules for secret scanning and allowlisting.

## Rollback / Recovery

- Revert the workflow and pre-commit hook, then remove the policy doc.

## Validation

- Not run (policy/config change only). CI will enforce on PRs to `main`.
