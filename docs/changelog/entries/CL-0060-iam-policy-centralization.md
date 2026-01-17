---
id: CL-0060-iam-policy-centralization
title: 'CL-0060: IAM Policy Centralization'
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
  - ADR-0099-standardized-iam-policy-management
  - CL-0060-iam-policy-centralization
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0060: IAM Policy Centralization

## Summary
Centralized all raw IAM JSON policy fragments into a dedicated governance directory and established a mapping index for Terraform variables.

## Changes
- **New Directory**: Created `docs/10-governance/policies/iam/` for all machine-readable governance fragments.
- **Combined ECR Policy**: Created `ecr-combined-policy.json` covering both registry management and image pushing.
- **Migration**: Moved existing CI teardown and IAM read JSON policies to the new centralized home.
- **Mapping Index**: Created `VARIABLE_MAPPING_INDEX.md` to map policies to infrastructure variables.
- **Decision Record**: Added `ADR-0099` to codify this management strategy.

## Impact
- **Security**: Easier auditing of raw IAM permissions.
- **Ops**: Improved traceability between documentation and Terraform implementation.
- **Governance**: 100% compliance with machine-readable policy standards.
