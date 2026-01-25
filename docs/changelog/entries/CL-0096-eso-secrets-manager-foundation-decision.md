---
id: CL-0096
title: 'CL-0096: Secrets Manager + ESO foundation decision'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0135
  - CL-0096
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-09
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0096: Secrets Manager + ESO foundation decision

Date: 2026-01-09
Owner: platform-team
Scope: platform foundations (secrets)
Related: ADR-0135

## Summary

- Establish Secrets Manager as the secrets source of truth for V1.
- Adopt External Secrets Operator as the sync mechanism into Kubernetes.
- Defer runbooks and operational playbooks until first rollout proves stable.

## Impact

- No runtime changes yet; this is a governance decision only.
- Implementation will introduce IAM/IRSA and ESO controller dependencies.

## Changes

### Added

- Decision to standardize on Secrets Manager + ESO for secrets.

### Documented

- ADR-0135 outlines the platform contract and scope.

### Known limitations

- Runbooks and incident playbooks are not yet defined.

## Rollback / Recovery

- Not required (decision only).

## Validation

- Not applicable (no code changes yet).
