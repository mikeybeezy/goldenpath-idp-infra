---
id: ADR-0096-risk-based-ecr-controls
title: 'ADR-0096: Risk-Based ECR Security Controls'
type: adr
domain: platform-core
owner: platform-team
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
  - ADR-0092
  - ADR-0093
  - CL-0056
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-05
version: '1.0'
dependencies:
  - terraform
  - aws-ecr
breaking_change: false
---

# ADR-0096: Risk-Based ECR Security Controls

## Status
Accepted

## Context

ECR registries have different security requirements based on their risk level. Production workloads need stronger controls (KMS encryption, immutable tags) while development environments can use lighter controls. Manual configuration is error-prone and inconsistent.

## Decision

Implement automated risk-based security controls using Terraform locals that automatically apply appropriate settings based on registry risk level.

### Risk Levels

**High Risk (Production/Sensitive):**
- KMS encryption (customer-managed keys)
- Immutable tags (cannot overwrite)
- 50 image retention
- Use for: Production, customer-facing, PCI/HIPAA

**Medium Risk (Staging/Internal):**
- AES256 encryption (AWS-managed)
- Mutable tags (can overwrite)
- 30 image retention
- Use for: Staging, internal tools, non-critical production

**Low Risk (Development/Testing):**
- AES256 encryption (AWS-managed)
- Mutable tags (can overwrite)
- 20 image retention
- Use for: Dev environments, experiments, testing

### Implementation

```hcl
# modules/aws_ecr/locals.tf
locals {
  risk_policies = {
    low    = { tag_mutability = "MUTABLE", encryption_type = "AES256", keep_count = 20 }
    medium = { tag_mutability = "MUTABLE", encryption_type = "AES256", keep_count = 30 }
    high   = { tag_mutability = "IMMUTABLE", encryption_type = "KMS", keep_count = 50 }
  }
  policy = local.risk_policies[var.metadata.risk]
}
```

Developers just set `risk = "high"` and all controls apply automatically.

## Consequences

**Pros:**
- Automatic security controls (no manual configuration)
- Consistent enforcement across all registries
- Clear risk-based tiers
- Developers understand what they get

**Cons:**
- Less flexibility (can't customize per-registry)
- KMS requires key management for high-risk

**Mitigations:**
- Document risk levels clearly in runbooks
- Show controls in PR template before creation
- Allow exceptions via manual Terraform override if needed

## Related
- [ADR-0092: ECR Registry Product Strategy](./ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0093: Automated Policy Enforcement](./ADR-0093-automated-policy-enforcement.md)
