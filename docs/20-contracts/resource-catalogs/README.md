<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CATALOG_INDEX
title: Platform Resource Catalogs
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0165
  - ADR-0166
  - CL-0057-domain-based-catalogs
  - agent_session_summary
  - session-2026-01-17-eks-backstage-scaffolder
supported_until: 2028-01-05
version: '1.0'
breaking_change: false
---

## Platform Resource Catalogs

**Purpose:** Index of all domain-based resource catalogs

---

## Active Catalogs

### Container Registries

**File:** [ecr-catalog.yaml](./ecr-catalog.yaml)
**Domain:** `container-registries`
**Owner:** platform-team
**Resources:** ECR container registries
**Self-Service:** [Create ECR Registry Workflow](../../.github/workflows/create-ecr-registry.yml)

### Databases - RDS

**File:** [rds-catalog.yaml](./rds-catalog.yaml)
**Domain:** `databases-rds`
**Owner:** platform-team
**Resources:** RDS databases
**Self-Service:** [Create RDS Database Workflow](../../.github/workflows/create-rds-database.yml)

### Clusters - EKS

**File:** [eks-catalog.yaml](./eks-catalog.yaml)
**Domain:** `platform-core`
**Owner:** platform-team
**Resources:** EKS clusters
**Self-Service:** EKS request flow (PR + manual apply workflow)

---

## Placeholder Catalogs (Schema Defined, Awaiting Implementation)

### Databases - DynamoDB

**File:** [dynamodb-catalog.yaml](./dynamodb-catalog.yaml) (PLACEHOLDER)
**Domain:** `databases-dynamodb`
**Owner:** database-team
**Resources:** DynamoDB tables
**Status:** Placeholder - needs Terraform module & workflow

### Storage - S3

**File:** [s3-catalog.yaml](./s3-catalog.yaml) (PLACEHOLDER)
**Domain:** `storage-s3`
**Owner:** platform-team
**Resources:** S3 buckets
**Status:** Placeholder - needs Terraform module & workflow

### Storage - EFS

**File:** [efs-catalog.yaml](./efs-catalog.yaml) (PLACEHOLDER)
**Domain:** `storage-efs`
**Owner:** platform-team
**Resources:** EFS file systems
**Status:** Placeholder - needs Terraform module & workflow

### Secrets Manager

**File:** [secrets-catalog.yaml](./secrets-catalog.yaml) (PLACEHOLDER)
**Domain:** `secrets-management`
**Owner:** platform-team
**Resources:** AWS Secrets Manager secrets
**Status:** Placeholder - needs Terraform module & workflow

### Compute - EC2

**File:** [ec2-catalog.yaml](./ec2-catalog.yaml) (PLACEHOLDER)
**Domain:** `compute-ec2`
**Owner:** platform-team
**Resources:** EC2 instances
**Status:** Placeholder - needs Terraform module & workflow

### Networking - VPC

**File:** [vpc-catalog.yaml](./vpc-catalog.yaml) (PLACEHOLDER)
**Domain:** `networking-vpc`
**Owner:** platform-team
**Resources:** VPCs, subnets, route tables
**Status:** Placeholder - needs Terraform module & workflow

---

## Catalog Schema

Each catalog follows this structure:

```yaml
version: "1.0"
domain: <domain-name>
owner: <team-name>
last_updated: "YYYY-MM-DD"
managed_by: <team-name>

<resources>:
  <resource-name>:
    metadata:
      id: <RESOURCE_ID>
      owner: <team-name>
      risk: <low|medium|high>
      environment: <dev|test|staging|prod>
```

---

## How Catalogs Work

```text
Developer Request
    ↓
GitHub Workflow
    ↓
1. Updates Catalog YAML
2. Runs generate_catalog_docs.py     <-- Atomic Sync
3. Updates REGISTRY_CATALOG.md
    ↓
Creates PR
    ↓
Platform Team Reviews
    ↓
Merge PR
    ↓
Terraform Reads YAML Catalog
    ↓
Creates AWS Resources
```

---

## Adding a New Catalog

1. Create `<domain>-catalog.yaml` in this directory
2. Follow the schema above
3. Create GitHub Actions workflow for self-service
4. Update Terraform to read the catalog
5. Update this README

---

## Related Documentation

- [ADR-0097: Domain-Based Resource Catalogs](../adrs/ADR-0097-domain-based-resource-catalogs.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
