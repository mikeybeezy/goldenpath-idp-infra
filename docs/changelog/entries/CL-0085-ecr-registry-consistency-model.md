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
