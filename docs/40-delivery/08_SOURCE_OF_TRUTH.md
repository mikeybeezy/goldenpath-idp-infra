---
id: 08_SOURCE_OF_TRUTH
title: Source of Truth (Stub)
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:

- 12_GITOPS_AND_CICD

---

# Source of Truth (Stub)

## Intent

Clarify which system is authoritative for infrastructure, platform config, and
runtime state so drift can be detected and reconciled consistently.

## Current stance (summary)

- Git repos define desired state for platform apps and manifests.
- Terraform state is authoritative for cloud infrastructure.
- Runtime clusters are observed state, not the source of truth.

## Notes

- This file is a stub to anchor ADR references until expanded.
- Related: `docs/40-delivery/12_GITOPS_AND_CICD.md`.
