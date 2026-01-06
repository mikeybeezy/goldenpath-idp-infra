---
id: ADR-0099
title: 'ADR-0099: Standardized IAM Policy Management'
type: adr
category: security
status: active
owner: platform-team
version: '1.0'
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
  - 33_IAM_ROLES_AND_POLICIES
---

# ADR-0099: Standardized IAM Policy Management

## Status
Active

## Context
Previously, IAM JSON policy fragments were scattered across documentation files or placed loosely in the `docs/policies/` directory. This made it difficult to:
1.  Verify exactly what permissions were assigned to specific Terraform variables.
2.  Maintain a clear mapping between governance requirements and technical implementation.
3.  Reuse policy logic across different environments or roles.

## Decision
We will centralize all machine-readable IAM policy fragments into a dedicated directory: `docs/policies/iam/`.

1.  **Strict File Format**: All policies must be valid JSON to ensure compatibility with Terraform's `file()` function and CI/CD linting.
2.  **Mapping Index**: A `VARIABLE_MAPPING_INDEX.md` will be maintained in the `iam/` directory, explicitly linking each JSON file to its corresponding Terraform variable and intended use case.
3.  **Versioning**: Policies follow the repository's main versioning and are treated as part of the infrastructure state.
4.  **Least Privilege**: The transition used to audit and consolidate permissions, starting with the `ecr-combined-policy.json`.

## Consequences
- **Positive**: Direct "Documentation-to-Code" traceability.
- **Positive**: Simplified security audits by having all raw policies in one place.
- **Positive**: Reduced risk of misconfiguration when populating Terraform variables.
- **Neutral**: Requires keeping the mapping index updated as new policies are added.
