---
id: CL-0131
title: Ephemeral Stack Standardization
type: changelog
status: active
date: 2026-01-15
domain: platform-core
owner: platform-team
lifecycle: active
schema_version: 1
relates_to:
  - 20_TOOLING_APPS_MATRIX
  - 38_EPHEMERAL_STACK_STRATEGY
  - ADR-0161
  - ADR-0161-ephemeral-infrastructure-stack
tags:
  - ephemeral
  - localstack
  - minio
  - postgres
---
## Changelog: Ephemeral Stack Standardization

**Date**: 2026-01-15
**Related Items**:

- ADR-0161: Standard Ephemeral Infrastructure Stack
- Doc: 38_EPHEMERAL_STACK_STRATEGY.md

## 🚀 Added

### Strategy

- **Standard Ephemeral Stack**: Formalized the decision to use containerized mocks for all ephemeral and local environments.
  - **Database**: Bitnami PostgreSQL replacing AWS RDS.
  - **Storage**: MinIO replacing AWS S3.
  - **Cloud APIs**: LocalStack replacing AWS SQS/SNS/Lambda.

### Documentation

- `docs/adrs/ADR-0161-ephemeral-infrastructure-stack.md`: Architectural decision record.
- `docs/00-foundations/38_EPHEMERAL_STACK_STRATEGY.md`: Guide to the "Simulation" strategy.
- Updated `docs/70-operations/20_TOOLING_APPS_MATRIX.md` (Pending) to include local mock configurations.

## Rationale

This change decouples local development and CI previews from costly and slow-to-provision real AWS infrastructure, enabling a "seconds-based" feedback loop for developers.
