---
id: ADR-0151-enforce-makefile-usage
title: 'ADR-0151: Enforce Makefile Usage and Break-Glass Protocol'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---

# ADR-0151: Enforce Makefile Usage and Break-Glass Protocol

## Proposer
Platform Team

## Status
Proposed

## Context
The "Golden Path" platform relies on `make` targets to ensure consistency, capture telemetry (as per ADR-0150), and enforce policy validation. However, developers can currently bypass these controls by running "naked" `terraform apply` commands directly.

This bypass capability poses risks:
1.  **Metric Gaps**: Builds run outside `make` are not logged in `build-timings.csv`.
2.  **Safety**: `make` targets often include safety checks (e.g., verifying cluster context or environment variables) that direct CLI usage skips.
3.  **Supportability**: Troubleshooting is harder when infrastructure is applied with unknown local flags.

## Decision
We will enforce the usage of the `Makefile` as the primary interface for infrastructure changes.

1.  **Terraform Guardrail**: We will implement a `check` in Terraform that fails the plan/apply unless a specific variable (`is_pipeline` or `break_glass`) is set to `true`.
2.  **Makefile Updates**: The standard `make` targets will automatically inject `is_pipeline=true`.
3.  **Break-Glass Protocol**: We will document a formal procedure for bypassing this check (`break_glass=true`) for emergency recovery or debugging scenarios where the Makefile abstraction is broken.

## Consequences
### Positive
*   **Completeness**: 100% of standard operational builds will be captured in telemetry.
*   **Safety**: Reduces "fat-finger" accidents by ensuring standardized entry points.
*   **Consistency**: All developers (and CI) use the exact same command path.

### Negative
*   **Friction**: Developers used to running `terraform apply` from muscle memory will encounter errors and must learn the `make` targets (or the bypass flag).
*   **Maintenance**: The guardrail logic must be maintained in the Terraform root modules.

## Governance
This decision enforces the "Paved Road" philosophy: staying on the path (Makefile) is easy and safe; going off-road (naked Terraform) requires explicit intent.
