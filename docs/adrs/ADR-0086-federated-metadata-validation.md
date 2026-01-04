---
id: ADR-0086-federated-metadata-validation
title: 'ADR-0086: Federated Metadata Validation Strategy'
type: adr
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies:
  - module:github-actions
  - module:pre-commit
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
  - ADR-0086
---

# ADR-0086: Federated Metadata Validation Strategy

## Context
Our current metadata compliance engine (`validate-metadata.py`) is locked within the `goldenpath-idp-infra` repository. As the platform scales, new application repositories (workloads) are being created without consistent metadata, leading to gaps in the IDP Knowledge Graph and inaccurate Health Reports.

## Decision
We will decentralize the **execution** of metadata validation while centralizing the **definition** of the policy.

1.  **Shared Action**: Extract `validate-metadata.py` into a standalone GitHub Action repo.
2.  **Global pre-commit**: Mandate the inclusion of this hook in all "Golden Templates."
3.  **Soft-fail Grace Period**: Initially implement as a warning (non-blocking) for 30 days before moving to hard-fail PR blocking.

## Consequences
- **Positive**: 100% visibility into all workload ownership and risk profiles across the org.
- **Negative**: Adds a mandatory check to developer workflows; may cause friction if metadata requirements are too complex.
- **Neutral**: Requires a centralized "Governance Registry" to manage allowed owners/categories.
