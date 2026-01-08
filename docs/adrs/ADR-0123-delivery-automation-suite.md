---
id: ADR-0123
title: 'ADR-0123: Delivery Automation Suite (ECR & Logs)'
type: adr
lifecycle: active
schema_version: 1
---

# ADR-0123: Delivery Automation Suite (ECR & Logs)

## Status

Accepted (Backfill)

## Context

The GoldenPath IDP requires a standardized set of utilities to handle ECR registry provisioning and build/teardown telemetry. These utilities were developed early in the project but lacked formal architectural records.

## Decision

We officially adopt the following scripts as the core Delivery Automation Suite:

1.  **`scaffold_ecr.py`**: Handles standardized ECR repository creation with baseline policies.
2.  **`ecr-build-push.sh`**: The primary wrapper for ECR authentication and image delivery.
3.  **`generate-build-log.sh` / `generate-teardown-log.sh`**: Standardizes telemetry capture for build and destruction phases.
4.  **`resolve-cluster-name.sh`**: Provides deterministic cluster naming across environments.

## Consequences

- **Positive**: Consistent ECR configuration across all services.
- **Positive**: Uniform logs for CI auditability.
- **Positive**: Automated ECR lifecycle management.
- **Negative**: Adds shell dependencies for logging scripts.
