---
id: ADR-0128
title: 'ADR-0128: Automated IDP Catalog Mapping for AWS ECR'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - ADR-0092
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-08
version: 1.0
breaking_change: false
---

# ADR-0128: Automated IDP Catalog Mapping for AWS ECR

## Status
Accepted

## Context
To minimize "Friction Tax," developers need visibility into container registries without leaving the IDP. Manually maintaining this inventory in Backstage is error-prone and leads to documentation drift.

## Decision
We will implement an automated "Catalog Bridge" script (`scripts/generate_backstage_ecr.py`) that performs the following steps:
1.  **Ingestion**: Reads the primary governance catalog at `docs/20-contracts/resource-catalogs/ecr-catalog.yaml`.
2.  **Transformation**: Translates each entry into a Backstage-compliant `Resource` entity.
3.  **Synchronization**: Updates the Backstage resource index (`all-resources.yaml`) to ensure all repositories are discoverable.
4.  **Operational Integration**: Automatically runs as a pre-step in the Backstage deployment pipeline.

## Consequences
- **Eliminates Drift**: The IDP is always a high-fidelity mirror of the governance catalog.
- **Granular Ownership**: Every container repository in the IDP is now linked to its specific owner and risk profile.
- **Reduced Friction**: Developers find registry details directly in the portal they use daily.
