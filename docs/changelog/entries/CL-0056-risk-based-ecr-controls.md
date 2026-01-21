---
id: CL-0056-risk-based-ecr-controls
title: 'CL-0056: Risk-Based ECR Security Controls'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
  - ADR-0096-risk-based-ecr-controls
  - CL-0056-risk-based-ecr-controls
  - CL-0058-testing-framework
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-05
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
dependencies:
  - terraform
  - aws-ecr
breaking_change: false
---

# CL-0056: Risk-Based ECR Security Controls

**Date:** 2026-01-05
**Type:** Feature
**Category:** Governance
**Status:** Active

## Summary

Implemented automated risk-based security controls for ECR registries that automatically apply encryption, tag mutability, and lifecycle policies based on risk level.

## Changes

### Modified Files
- `modules/aws_ecr/main.tf` - Updated to use risk-based policies from locals
- `modules/aws_ecr/locals.tf` - Added risk policy definitions
- `.github/workflows/create-ecr-registry.yml` - Enhanced PR template to show controls

### Risk-Based Controls

**High Risk (Production):**
- KMS encryption (customer-managed keys)
- Immutable tags (cannot overwrite)
- 50 image retention
- Enhanced scanning

**Medium Risk (Staging):**
- AES256 encryption (AWS-managed)
- Mutable tags (can overwrite)
- 30 image retention
- Standard scanning

**Low Risk (Development):**
- AES256 encryption (AWS-managed)
- Mutable tags (can overwrite)
- 20 image retention
- Standard scanning

## Impact

### Platform Team
- Consistent security controls across all registries
- No manual configuration needed
- Automatic compliance with risk policies

### Application Teams
- Clear understanding of what they get
- Risk level visible in PR before creation
- Appropriate controls for workload type

## Implementation

Developers simply set risk level in catalog:
```yaml
registries:
  my-registry:
    metadata:
      risk: high  # Controls applied automatically
```

Terraform automatically applies:
- Encryption type
- Tag mutability
- Lifecycle retention
- Scanning configuration

## Validation

- Added Terraform precondition to validate risk level
- PR template shows controls before creation
- Lifecycle policy description includes risk level

## Related
- [ADR-0096: Risk-Based ECR Controls](../adrs/ADR-0096-risk-based-ecr-controls.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0093: Automated Policy Enforcement](../adrs/ADR-0093-automated-policy-enforcement.md)
