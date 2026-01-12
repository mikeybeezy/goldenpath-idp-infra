---
id: CL-0023-bootstrap-v3-irsa-skip
title: 'CL-0023: Bootstrap v3 skips IRSA apply'
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
  - ADR-0073
  - CL-0023
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-04
version: '1.0'
breaking_change: false
---

# CL-0023: Bootstrap v3 skips IRSA apply

Date: 2026-01-02
Owner: platform
Scope: infra
Related: docs/adrs/ADR-0073-platform-bootstrap-v3-irsa-skip.md, PR #114

## Summary

Added a v3 bootstrap script that skips Terraform IRSA apply in Stage 3B and
validates existing service accounts instead.

## Changes

### Added

- `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh`

### Changed

- `Makefile`: allow `BOOTSTRAP_VERSION=v3`.
- `.github/workflows/ci-bootstrap.yml`: add `v3` option to the selector.

## Validation

- Not run (workflow-only change).
