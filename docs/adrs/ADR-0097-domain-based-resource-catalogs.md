---
id: ADR-0097-domain-based-resource-catalogs
title: 'ADR-0097: Domain-Based Resource Catalogs'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0094-automated-catalog-docs
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - ADR-0110-idp-knowledge-graph-architecture
  - CATALOG_INDEX
  - CATALOG_SYSTEMS
  - CL-0057-domain-based-catalogs
  - CL-0062-documentation-generator-metadata-compliance
  - DOCS_20-CONTRACTS_RESOURCE-CATALOGS_README
  - REGISTRY_CATALOG
  - SCRIPT_CERTIFICATION_AUDIT
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
  - backstage
breaking_change: true
---

## ADR-0097: Domain-Based Resource Catalogs

## Status

Accepted

## Context

As the platform grows, we need to manage multiple resource types (ECR registries, RDS databases, S3 buckets, EKS clusters, etc.). We must decide between:

1. **Single platform-wide catalog** - One YAML file for all resources
2. **Domain-based catalogs** - Separate YAML files per resource domain

### Current State

```text
docs/
└── registry-catalog.yaml  # ECR only
```

### Future State (Option 1: Single Catalog)

```text
docs/
└── platform-catalog.yaml  # Everything in one file
    ├── ecr_registries
    ├── rds_databases
    ├── s3_buckets
    └── eks_clusters
```

### Future State (Option 2: Domain-Based)

```text
docs/20-contracts/resource-catalogs/
├── ecr-catalog.yaml
├── rds-catalog.yaml
├── s3-catalog.yaml
└── eks-catalog.yaml
```

## Decision

**Adopt domain-based catalogs** - separate YAML files per resource domain.

### Catalog Structure

```text
docs/20-contracts/resource-catalogs/
├── README.md              # Index of all catalogs
├── ecr-catalog.yaml       # Container registries
├── rds-catalog.yaml       # Databases (future)
├── s3-catalog.yaml        # Storage (future)
└── eks-catalog.yaml       # Clusters (future)
```

### Catalog Schema

Each catalog follows this structure:

```yaml
# docs/20-contracts/resource-catalogs/ecr-catalog.yaml
version: "1.0"
domain: delivery
owner: platform-team
last_updated: "2026-01-05"
managed_by: platform-team

registries:
  wordpress-platform:
    metadata:
      id: REGISTRY_WORDPRESS_PLATFORM
      owner: app-team-wordpress
      risk: high
      environment: prod
```

### Terraform Integration

Each Terraform module reads its domain catalog:

```hcl
# envs/dev/main.tf
locals {
  ecr_catalog = yamldecode(file("../../docs/20-contracts/resource-catalogs/ecr-catalog.yaml"))
}

module "ecr_repositories" {
  source   = "../../modules/aws_ecr"
  for_each = local.ecr_catalog.registries
  # ...
}
```

### Backstage Integration

Backstage aggregates all catalogs:

```yaml
# app-config.yaml
catalog:
  locations:
    - type: url
      target: <https://github.com/.../docs/20-contracts/resource-catalogs/ecr-catalog.yaml>
    - type: url
      target: <https://github.com/.../docs/20-contracts/resource-catalogs/rds-catalog.yaml>
```

## Architecture Diagram

```text
┌─────────────────────────────────────────────────────┐
│  DOMAIN-BASED CATALOG ARCHITECTURE                  │
└─────────────────────────────────────────────────────┘

DEVELOPERS
    ↓
GitHub Workflow (Self-Service)
    ↓
    ├─→ ECR Workflow → docs/20-contracts/resource-catalogs/ecr-catalog.yaml
    ├─→ RDS Workflow → docs/20-contracts/resource-catalogs/rds-catalog.yaml
    └─→ S3 Workflow  → docs/20-contracts/resource-catalogs/s3-catalog.yaml

    ↓
TERRAFORM (Per-Domain)
    ↓
    ├─→ ECR Module reads ecr-catalog.yaml
    ├─→ RDS Module reads rds-catalog.yaml
    └─→ S3 Module reads s3-catalog.yaml

    ↓
AWS RESOURCES

BACKSTAGE (Aggregated View)
    ↓
Reads all catalogs → Unified service catalog
```

## Consequences

### Pros

### Scalability

- Small, focused files (easier to work with)
- No single file bottleneck
- Scales to hundreds of resources

### Ownership

- Different teams can own different catalogs
- Database team owns `rds-catalog.yaml`
- Storage team owns `s3-catalog.yaml`
- Clear responsibility boundaries

### Blast Radius

- Changes to ECR don't affect RDS
- Reduced merge conflicts
- Isolated failures

### Performance

- Terraform only reads relevant catalog
- Faster parsing
- Lower memory usage

### Flexibility

- Different schemas per domain
- Domain-specific metadata
- Independent versioning

### Cons

### Complexity

- More files to maintain
- Need catalog discovery mechanism
- Aggregation required for platform-wide view

### Migration

- Breaking change (need to update references)
- Workflow updates required
- Documentation updates required

### Mitigations

### Catalog Discovery

- Create `docs/20-contracts/resource-catalogs/README.md` as index
- Backstage auto-discovers via config

### Migration Path

1. Create `docs/20-contracts/resource-catalogs/` directory
2. Move `registry-catalog.yaml` → `ecr-catalog.yaml`
3. Update all references (workflows, Terraform)
4. Update documentation

### Backward Compatibility

- Not possible (breaking change)
- Acceptable since no production usage yet

## Trade-offs

|Aspect|Single Catalog|Domain-Based|Winner|
|--------|---------------|--------------|--------|
|**Simplicity**|One file|Multiple files|Single|
|**Scalability**|Gets huge|Stays small|Domain|
|**Ownership**|Shared|Distributed|Domain|
|**Performance**|Parse all|Parse needed|Domain|
|**Merge Conflicts**|High risk|Low risk|Domain|
|**Discovery**|Easy|Need index|Single|

**Overall:** Domain-based wins 4-2

## Implementation

### Phase 1: Structure

- Create `docs/20-contracts/resource-catalogs/` directory
- Create `docs/20-contracts/resource-catalogs/README.md` index
- Move `registry-catalog.yaml` → `ecr-catalog.yaml`

### Phase 2: Update References

- Update `.github/workflows/create-ecr-registry.yml`
- Update `scripts/generate_catalog_docs.py`
- Update Terraform (when implemented)

### Phase 3: Documentation

- Update runbooks
- Update ADRs
- Create changelog

## Related

- [ADR-0092: ECR Registry Product Strategy](./ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0094: Automated Catalog Documentation](./ADR-0094-automated-catalog-docs.md)
