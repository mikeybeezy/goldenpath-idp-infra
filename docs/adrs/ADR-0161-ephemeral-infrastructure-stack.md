# ADR-0161: Standard Ephemeral Infrastructure Stack

**Status**: Accepted
**Date**: 2026-01-15
**Context**: "Feature/Tooling-Apps-Config" Branch

## Context

Our platform supports multiple deployment contexts:
1.  **Production**: Requires robust, managed AWS infrastructure (RDS, S3, SQS).
2.  **Ephemeral/CI**: Requires fast startup, low cost, and isolation.
3.  **Local Development**: Requires offline capability and zero cost.

Provisioning real AWS resources (e.g., RDS instances) for every CI build or local test is:
*   **Slow**: RDS takes ~10-15 minutes to provision.
*   **Expensive**: Hourly costs accumulate for idling CI resources.
*   **Complex**: Requires credential management and internet connectivity.

## Decision

We will standardize on a **"Containerized Mock Stack"** for all ephemeral and local environments (Day 0 & Development).

The canonical stack consists of:
1.  **Database**: **Bitnami PostgreSQL** (Simulates AWS RDS).
2.  **Object Storage**: **MinIO** (Simulates AWS S3).
3.  **Cloud APIs**: **LocalStack** (Simulates AWS SQS, SNS, Lambda, IAM).

### Usage by Environment

| Component | Production / Staging | Ephemeral (CI/PR) | Local (Kind/Docker) |
| :--- | :--- | :--- | :--- |
| **Database** | AWS RDS (Multi-AZ) | **Bitnami PostgreSQL** | **Bitnami PostgreSQL** |
| **Storage** | AWS S3 | **MinIO** | **MinIO** |
| **Queue/Msg** | AWS SQS/SNS | **LocalStack** | **LocalStack** |

## Implementation Strategy

1.  **Uniform GitOps Interfaces**:
    *   Applications will continue to use `ExternalSecrets` and standard connection strings.
    *   Helm Charts will support a `global.localDev: true` toggle that switches dependencies from "External AWS" to "In-Cluster Charts".

2.  **Default Inclusion**:
    *   The `bootstrap` scripts for Ephemeral/Local modes will automatically install these charts.
    *   `make apply` (in ephemeral mode) will eventually trigger the installation of these mocks via ArgoCD.

4.  **Persistence**:
    *   **Default**: Ephemeral (emptyDir) for speed.
    *   **Option**: Supports standard PVC/EBS persistence for debugging if needed.

## Consequences

### Positive
*   **Speed**: Environment provisioning drops from ~20 mins to ~2 mins.
*   **Cost**: Zero cloud spend for CI previews and local dev.
*   **Offline**: Developers can work without internet access.
*   **Reset**: `make destroy` or `kubectl delete` instantly wipes state (great for testing).

### Negative
*   **Parity Gap**: "It works in LocalStack" does not guarantee "It works in AWS". We must maintain Staging environments with real infra for final verification.
*   **Complexity**: Helm charts need logic to switch between "Real" and "Mock" dependencies.

## References
*   [LocalStack](https://localstack.cloud/)
*   [MinIO](https://min.io/)
*   [Bitnami Charts](https://github.com/bitnami/charts)
