---
id: ADR-0092-ecr-registry-product-strategy
title: 'ADR-0092: ECR Registry Product-Based Strategy & Shared Responsibility Model'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
  - ADR-0094-automated-catalog-docs
  - ADR-0095-self-service-registry-creation
  - ADR-0096-risk-based-ecr-controls
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0098-standardized-pr-gates
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - ADR-0128
  - ADR-0129
  - CAPABILITY_LEDGER
  - CATALOG_INDEX
  - CL-0052-ecr-registry-product-strategy
  - CL-0053-daily-policy-enforcement-workflow
  - CL-0054-automated-catalog-docs
  - CL-0055-self-service-registry-creation
  - CL-0056-risk-based-ecr-controls
  - CL-0057-domain-based-catalogs
  - RB-0024-request-registry
  - REGISTRY_CATALOG
  - SCRIPTS_POLICIES
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
version: '1.0'
breaking_change: false
---

## ADR-0092: ECR Registry Product-Based Strategy & Shared Responsibility Model

## Status

Accepted

## Context

We need a clear strategy for ECR registry management that aligns with Domain-Driven Design principles and establishes clear ownership boundaries between platform and application teams.

## Decision

### 1. Product-Based Repositories

Repositories are created **per-product** (bounded context), not per-app or per-team. These reside within the shared platform Registry.

**Naming:** `{product-name}-{optional-component}`

### Examples

- `wordpress-platform`
- `payments-gateway`
- `ml-inference-engine`

**Rationale:** Aligns with DDD, reduces cognitive load, contains blast radius.

### 2. Shared Responsibility Model

### Platform Team (The "Vault")

- Create/decommission registries
- Enforce governance (metadata, scanning, encryption)
- Set lifecycle policies
- Grant IAM permissions
- Maintain registry catalog

### Application Team (The "Factory")

- Build and push images
- Tag images (semantic versioning)
- Remediate CVEs
- Document images

### 3. Registry & Repository Catalog

**Format:** YAML (`docs/20-contracts/resource-catalogs/ecr-catalog.yaml`)

### Schema

```yaml
version: "1.0"
physical_registry: "main-registry-name"
repositories:
  {repository-name}:
    metadata:
      id: "REGISTRY_{PRODUCT}"
      owner: "app-team-{name}"
      risk: "low|medium|high"
      status: "active|deprecated|decommissioned"
    aws:
      repository_url: "FULL_ECR_URL"
    governance:
      image_scanning: true
      encryption: "AES256|KMS"
      lifecycle_policy:
        keep_image_count: 20|30|50
```

### 4. Risk-Based Policies

|Risk|Tag Mutability|Encryption|Retention|Scanning|
|------|---------------|------------|-----------|----------|
|Low|MUTABLE|AES256|20 images|Standard|
|Medium|MUTABLE|AES256|30 images|Enhanced|
|High|IMMUTABLE|KMS|50 images|Critical|

### 5. Registry Lifecycle

### Creation

1. App team requests registry (Backstage/GitHub issue)
2. Platform team reviews and approves
3. Platform team provisions via Terraform
4. Platform team grants IAM permissions

### Decommissioning

1. Team lead requests decommissioning
2. Platform team verifies no active deployments
3. Platform team backs up (if compliance required)
4. Platform team runs `terraform destroy`
5. Platform team revokes IAM permissions

## Consequences

### Pros

- Clear ownership boundaries
- Scalable (platform manages registries, apps manage images)
- Governed by default
- Risk-appropriate controls

### Cons

- App teams can't self-service registry creation
- Platform team is bottleneck for registry creation
- Catalog sync complexity

### Mitigations

- 24-48 hour SLA for registry creation
- Automation for catalog ↔ Terraform sync

## Related

- [ADR-0091: Trusted Delivery Pipeline](./ADR-0091-trusted-delivery-pipeline.md)
- [ADR-0093: Automated Policy Enforcement](./ADR-0093-automated-policy-enforcement.md)
