---
id: 2026-01-04_2339_trusted-delivery-pipeline-phase-4-final
title: Walkthrough - IDP Productization V2
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
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
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies: []
supported_until: '2028-01-01'
breaking_change: false
---

# Walkthrough - IDP Productization V2

## Phase 4: Trusted Delivery Pipeline (Poly-Repo)

We have successfully implemented the "Trusted Delivery Pipeline" enabling distributed teams to build and ship containers securely.

### Architecture (The Bridge)
- **Platform Repo**: Owns the ECR Registry (The Vault). Created via standard `modules/aws_ecr`.
- **App Repo**: Owns the Dockerfile & CI (The Factory). Pushes to ECR via OIDC.

### New Capabilities
1.  **Metric**: "Born Governed" Registries.
    - Verified: `aws_ecr` module enforces `metadata` tags (ID, Owner, Danger).
2.  **Automation**: Deterministic Registry Creation.
    - Command: `make create-ecr APP=my-app ...`
    - Result: Appends fully compliant Terraform to `envs/dev/ecr.tf`.
3.  **Documentation**:
    - [Trusted Delivery Strategy](docs/10-governance/TRUSTED_DELIVERY_STRATEGY.md)
    - [Terraform Standard](docs/10-governance/METADATA_INJECTION_GUIDE.md#4-terraform-module-standard)

### ✅ Verification Results
- **ECR Module**: `terraform validate` passed (Governance Logic Valid).
- **Automation**: `scripts/scaffold_ecr.py` successfully generates valid blocks.
- **Pipeline Config**: `ci-build-push.yml` committed to App Repo.

### Next Steps (User Action)
1.  **Merge Infra**: Merge `delivery/ecr-pipeline` -> `main` & `terraform apply`.
2.  **Activate App**: Set `TF_AWS_IAM_ROLE_DEV` secret in `goldenpath-wordpress-app`.
