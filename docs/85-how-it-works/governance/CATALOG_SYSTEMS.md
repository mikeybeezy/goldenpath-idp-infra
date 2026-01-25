---
id: CATALOG_SYSTEMS
title: 'How It Works: Platform Catalog Systems'
type: documentation
relates_to:
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0159-backstage-catalog-registry-sync
  - DOCS_20-CONTRACTS_RESOURCE-CATALOGS_README
  - ECR_REQUEST_FLOW
  - RDS_REQUEST_FLOW
---

## How It Works: Platform Catalog Systems

This document explains the two catalog systems in the platform and how they work together.

## Overview: Two Systems, One Purpose

The platform uses two complementary catalog systems:

|System|Location|Purpose|Audience|
|--------|----------|---------|----------|
|**Resource Catalogs**|`docs/20-contracts/resource-catalogs/`|Source of truth for governance|Automation, Terraform, CI|
|**Backstage Catalog**|`backstage-helm/backstage-catalog/`|Developer portal UI|Developers via Backstage|

Think of it as:

- **Resource Catalogs** = The database (authoritative record)
- **Backstage Catalog** = The frontend (user interface)

## 1. Resource Catalogs (Source of Truth)

### What They Are

Simple YAML files that track **what resources exist** and **who owns them**.

```yaml
# docs/20-contracts/resource-catalogs/ecr-catalog.yaml
version: "1.0"
domain: delivery
owner: platform-team
repositories:
  wordpress-platform:
    metadata:
      id: REGISTRY_WORDPRESS_PLATFORM
      owner: app-team-wordpress
      risk: high
      environment: prod
      status: active
```

### What They Track

|Catalog|Resources|
|---------|-----------|
|`ecr-catalog.yaml`|ECR container registries|
|`rds-catalog.yaml`|RDS databases|
|`s3-catalog.yaml`|S3 buckets|
|`secrets-catalog.yaml`|AWS Secrets Manager secrets|
|`vpc-catalog.yaml`|VPC configurations|
|`eks-catalog.yaml`|EKS clusters|

### Who Uses Them

```text
┌─────────────────────────────────────────────────────────────┐
│                  RESOURCE CATALOGS                          │
│              (docs/20-contracts/resource-catalogs/)         │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Terraform    │   │  CI Workflows │   │   Scripts     │
│               │   │               │   │               │
│ Reads catalog │   │ Validates &   │   │ Generates     │
│ to provision  │   │ updates       │   │ reports &     │
│ AWS resources │   │ entries       │   │ Backstage     │
└───────────────┘   └───────────────┘   └───────────────┘
```

## 2. Backstage Catalog (Developer Portal)

### What It Is

Backstage-formatted entities that appear in the **developer portal UI**.

```yaml
# backstage-helm/backstage-catalog/templates/rds-request.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: rds-request
  title: Request Platform RDS Database
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Database Details
      properties:
        databaseName:
          title: Database Name
          type: string
```

### What It Contains

|Content|Purpose|
|---------|---------|
|**Templates**|Self-service forms (ECR, RDS requests)|
|**Components**|Services, applications|
|**Systems**|Logical groupings|
|**Resources**|Infrastructure displayed in UI|
|**APIs**|API documentation|
|**Domains**|Business domains|

### Where It Lives

```text
backstage-helm/
├── backstage-catalog/           # ← Catalog entities
│   ├── all.yaml                 # Entry point (Location entity)
│   ├── templates/               # Self-service templates
│   │   ├── ecr-request.yaml
│   │   └── rds-request.yaml
│   ├── components/              # Service entities
│   ├── systems/                 # System groupings
│   └── resources/               # Infrastructure entities
└── charts/backstage/
    └── values.yaml              # Points to governance-registry
```

## 3. How They Work Together

### The Self-Service Flow

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         SELF-SERVICE REQUEST FLOW                       │
└─────────────────────────────────────────────────────────────────────────┘

  BACKSTAGE CATALOG                 RESOURCE CATALOGS              AWS
  (Developer Portal)                (Source of Truth)         (Infrastructure)
         │                                 │                        │
         │  1. Developer fills             │                        │
         │     template form               │                        │
         ▼                                 │                        │
┌──────────────────┐                       │                        │
│ rds-request.yaml │                       │                        │
│ (Backstage       │                       │                        │
│  Template)       │                       │                        │
└────────┬─────────┘                       │                        │
         │                                 │                        │
         │  2. Triggers GitHub             │                        │
         │     Actions workflow            │                        │
         ▼                                 │                        │
┌──────────────────┐                       │                        │
│ create-rds-      │                       │                        │
│ database.yml     │ ─────────────────────►│                        │
│ (Workflow)       │  3. Updates catalog   │                        │
└──────────────────┘                       ▼                        │
                                 ┌──────────────────┐               │
                                 │ rds-catalog.yaml │               │
                                 │ (Resource        │               │
                                 │  Catalog)        │               │
                                 └────────┬─────────┘               │
                                          │                         │
                                          │  4. Creates PR          │
                                          │     for approval        │
                                          ▼                         │
                                 ┌──────────────────┐               │
                                 │ PR Review &      │               │
                                 │ Merge            │               │
                                 └────────┬─────────┘               │
                                          │                         │
                                          │  5. Terraform reads     │
                                          │     catalog, applies    │
                                          ▼                         ▼
                                 ┌──────────────────┐    ┌──────────────────┐
                                 │ make rds-apply   │───►│ AWS RDS Database │
                                 │ ENV=dev          │    │ + Secrets        │
                                 └──────────────────┘    └──────────────────┘
```

### Sync to Governance Registry

The Backstage catalog is synced to the `governance-registry` branch for stable access:

```text
development/main branch              governance-registry branch
        │                                      │
        │  Push to dev/main                    │
        ▼                                      │
┌───────────────────────┐                      │
│ governance-registry-  │                      │
│ writer.yml            │ ────────────────────►│
└───────────────────────┘                      │
                                               ▼
                              ┌────────────────────────────────┐
                              │ backstage-catalog/             │
                              │ ├── all.yaml                   │
                              │ ├── templates/                 │
                              │ └── ...                        │
                              └────────────────────────────────┘
                                               │
                              All Backstage instances read from
                              governance-registry (stable URL)
```

## 4. Directory Naming Convention

### Current Structure

```text
docs/
└── 20-contracts/
    └── resource-catalogs/        # ← Renamed from "catalogs"
        ├── README.md
        ├── ecr-catalog.yaml      # ECR registries
        ├── rds-catalog.yaml      # RDS databases
        ├── s3-catalog.yaml       # S3 buckets
        └── ...

backstage-helm/
└── backstage-catalog/            # ← Renamed from "catalog"
    ├── all.yaml
    ├── templates/
    │   ├── ecr-request.yaml
    │   └── rds-request.yaml
    └── ...
```

### Why This Naming?

|Old Name|New Name|Reason|
|----------|----------|--------|
|`docs/20-contracts/catalogs/`|`docs/20-contracts/resource-catalogs/`|Clarifies these are **resource governance** catalogs|
|`backstage-helm/catalog/`|`backstage-helm/backstage-catalog/`|Clarifies this is the **Backstage UI** catalog|

## 5. Quick Reference

### "Where do I look for...?"

|Question|Location|
|----------|----------|
|What ECR repos exist?|`docs/20-contracts/resource-catalogs/ecr-catalog.yaml`|
|What RDS databases exist?|`docs/20-contracts/resource-catalogs/rds-catalog.yaml`|
|How do I request a new database?|Backstage → "Request Platform RDS Database" template|
|How do I request a new ECR repo?|Backstage → "Request ECR Registry" template|
|Who owns a resource?|Check the resource catalog (authoritative)|
|What templates are available?|`backstage-helm/backstage-catalog/templates/`|

### "What happens when...?"

|Action|Flow|
|--------|------|
|Developer requests resource|Template → Workflow → Resource Catalog → PR → Terraform|
|Resource catalog updated|CI validates → Terraform provisions (after merge)|
|Backstage catalog changed|Synced to governance-registry → All envs see update|

## Related Documentation

- [ADR-0097: Domain-Based Resource Catalogs](../../adrs/ADR-0097-domain-based-resource-catalogs.md)
- [ADR-0159: Backstage Catalog Registry Sync](../../adrs/ADR-0159-backstage-catalog-registry-sync.md)
- [ECR Request Flow](../self-service/ECR_REQUEST_FLOW.md)
- [RDS Request Flow](../self-service/RDS_REQUEST_FLOW.md)
