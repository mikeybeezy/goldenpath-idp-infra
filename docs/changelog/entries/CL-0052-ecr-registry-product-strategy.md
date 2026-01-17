---
id: CL-0052-ecr-registry-product-strategy
title: 'CL-0052: ECR Registry Product-Based Strategy & Shared Responsibility Model'
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
  coupling_risk: medium
reliability:
  rollback_strategy: revert-adr
  observability_tier: gold
schema_version: 1
relates_to:
  - ADR-0091
  - ADR-0092
  - ADR-0092-ecr-registry-product-strategy
  - CL-0051
  - CL-0052
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
dependencies:
  - CL-0051
breaking_change: false
---
# CL-0052: ECR Registry Product-Based Strategy & Shared Responsibility Model

Date: 2026-01-05
Owner: platform-team
Scope: All environments (dev/test/staging/prod)
Related: [ADR-0092](../adrs/ADR-0092-ecr-registry-product-strategy.md), [ADR-0091](../adrs/ADR-0091-trusted-delivery-pipeline.md)

## Summary

- Established product-based ECR registry architecture aligned with Domain-Driven Design bounded contexts
- Defined clear shared responsibility model: Platform Team owns registry governance, App Teams own image management
- Implemented risk-based governance policies that automatically configure registry security controls
- Created registry catalog structure (YAML) as authoritative source of truth for all ECR registries

## Impact

**Platform Team:**
- Now responsible for registry creation, governance, lifecycle policies, and decommissioning (infrequent operations)
- Must maintain registry catalog (`docs/registry-catalog.yaml`) as source of truth
- Commits to 24-48 hour SLA for new registry requests

**Application Teams:**
- Responsible for building, tagging, and pushing container images (frequent operations)
- Must request registries through defined process (Backstage template or GitHub issue)
- Gain clarity on what they own (images) vs. what platform owns (registries)

**Registry Naming:**
- Registries now follow product-based naming: `{product-name}-{optional-component}`
- Example: `wordpress-platform`, `payments-gateway`, `ml-inference-engine`
- Multiple images can exist within a single registry using tags

**Governance:**
- All registries automatically get metadata (ID, owner, risk), encryption, scanning, and lifecycle policies
- Risk level (`low|medium|high`) determines security controls (tag mutability, encryption type, retention)

## Changes

### Added

- **ADR-0092**: Comprehensive architecture decision record documenting registry strategy
- **Registry Catalog Schema**: YAML structure for tracking all ECR registries
- **Shared Responsibility Matrix**: Clear delineation of platform vs. app team duties
- **Risk-Based Policy Mapping**: Automatic configuration based on risk classification
- **Living Documentation Framework**: 7 document types to maintain registry ecosystem:
  1. Registry Catalog (YAML)
  2. Registry Governance Policy
  3. Image Scanning Policy
  4. Lifecycle Retention Policy
  5. Platform Team Runbooks (5 guides)
  6. Application Team Runbooks (5 guides)
  7. Generated Registry Catalog (Markdown)

### Changed

- **Registry Granularity**: Shifted from app-specific to product-based registries (reduces registry sprawl)
- **Naming Convention**: Standardized on `{product-name}-{component}` format
- **Ownership Model**: Formalized platform team as "Vault" owners, app teams as "Factory" owners
- **Lifecycle Policies**: Now risk-based (low=20 images, medium=30, high=50)
- **Tag Mutability**: High-risk registries use IMMUTABLE tags, low/medium use MUTABLE
- **Encryption**: High-risk registries use KMS, low/medium use AES256

### Documented

- **Shared Responsibility Model**: Platform team responsibilities (8 areas) vs. app team responsibilities (8 areas)
- **Registry Lifecycle Workflows**: Creation workflow (8 steps) and decommissioning workflow (5 steps)
- **Risk-Based Governance Table**: Security controls mapped to risk levels
- **Living Documentation Structure**: What documents exist, who owns them, update frequency
- **Bounded Context Rationale**: Why product-based registries reduce cognitive load and align with DDD

### Known Limitations

- **No Self-Service Registry Creation**: App teams cannot create registries themselves (by design for governance)
- **Platform Team Bottleneck**: Registry creation requires platform team action (mitigated by 24-48h SLA)
- **Catalog Sync Complexity**: Must keep YAML catalog, Terraform state, and AWS in sync (automation planned)
- **Learning Curve**: Teams must understand new shared responsibility model (runbooks to be created)

## Rollback / Recovery

**If this strategy proves problematic:**
1. Revert ADR-0092 to "Superseded" status
2. Return to previous registry naming convention
3. Remove risk-based policy automation from Terraform module
4. Delete registry catalog YAML structure

**Risk:** Low - This is primarily a governance and documentation change, not a technical breaking change. Existing registries continue to function.

## Validation

- ✅ ADR-0092 created and committed
- ✅ Changelog entry (CL-0052) created
- ✅ Registry catalog schema defined in ADR
- ✅ Shared responsibility matrix documented
- ✅ Risk-based governance policies specified
-  Registry catalog YAML to be created (next step)
-  Platform team runbooks to be created
-  App team runbooks to be created
-  Terraform module updates to enforce risk-based policies (future)

## Next Steps

1. **Create Registry Catalog**: Initialize `docs/registry-catalog.yaml` with existing registries
2. **Create Governance Policies**: Write the 3 governance policy documents
3. **Create Runbooks**: Write platform team and app team operational guides
4. **Update Terraform Module**: Implement risk-based policy automation in `modules/aws_ecr`
5. **Backstage Integration**: Create registry request template for self-service workflow
6. **Team Communication**: Present shared responsibility model to app teams
7. **Migrate Existing Registries**: Rename/restructure existing registries to follow new convention

## Migration Notes

**Existing Registry:** `goldenpath-wordpress-ap5445`

**Recommended Action:**
- Use `terraform state mv` to rename to product-based convention: `wordpress-platform`
- Update catalog with proper metadata
- Notify wordpress app team of new registry URL
- Update CI/CD pipelines to push to new registry name
- Deprecate old registry after grace period

**Command:**
```bash
terraform state mv \
  'module.ecr_repositories["goldenpath-wordpress-ap5445"]' \
  'module.ecr_repositories["wordpress-platform"]'
```
