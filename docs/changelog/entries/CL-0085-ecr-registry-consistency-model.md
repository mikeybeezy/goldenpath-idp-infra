---
id: CL-0085-ecr-registry-consistency-model
title: 'CL-0085: ECR Registry Consistency Model'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
lifecycle: active
version: '1.0'
relates_to:
  - CL-0085
supported_until: 2028-01-08
breaking_change: false
---

# CL-0085: ECR Registry Consistency Model

## Date
2026-01-08

## Type
Governance / Architecture

## Description
Shifted the ECR Registry discovery model from distributed file sprawl to an eventually consistent "Mirror Script" model to ensure 100% referential integrity between the IDP Catalog and the physical infrastructure.

## Impact
- **Governance**: Adopted ADR-0129, prioritizing catalog integrity over immediate speed.
- **Consistency**: Implemented a "Time to Parity" target of ~3 minutes across the synchronization pipeline.
- **Infrastructure**: Prepared for the deprecation of orphaned ECR `Resource` YAML files in favor of a centralized master registry entity.
- **Performance**: Optimized Backstage catalog polling intervals to support faster synchronization.
