# Ephemeral Stack Strategy: "The Simulation"

**Owner**: Platform Team
**Status**: Living Document
**Updated**: 2026-01-15

## Philosophy: "Speed in Dev, Solidity in Prod"

We believe that developer feedback loops should be measured in seconds, not minutes. Waiting 15 minutes for an RDS instance to spin up just to test a schema migration is unacceptable.

To achieve this, we employ a **"Simulation Strategy"**:
*   **Local & CI** environments run on a **Simulated Cloud** inside the cluster.
*   **Staging & Production** environments run on the **Real Cloud** (AWS).

## The Tech Stack

### 1. LocalStack (The Cloud Emulator)
*   **Purpose**: Act as "AWS-in-a-Box". It intercepts API calls to specific endpoints (like SQS, SNS, DynamoDB) and processes them locally.
*   **When to deploy**: Standard in all Ephemeral/Local environments.
*   **Endpoint**: `http://localstack.local-infra.svc.cluster.local:4566` (Internal K8s DNS)

### 2. MinIO (The Object Store)
*   **Purpose**: High-performance, S3-compatible object storage.
*   **Why**: Simulating S3 behaviors (Buckets, Policies, Presigned URLs) without IAM complexity.
*   **Connection**:
    *   Endpoint: `http://minio.local-infra.svc.cluster.local:9000`
    *   Access Key: `minioadmin` (Default Dev)
    *   Secret Key: `minioadmin` (Default Dev)

### 3. Bitnami PostgreSQL (The Database)
*   **Purpose**: Reliable, fast-starting Postgres database.
*   **Why**: It provides the exact same wire protocol as AWS RDS Postgres. Your application cannot tell the difference.
*   **Configuration**:
    *   Configured to match Prod version (e.g., PostgreSQL 15.4).

## How It Works (The "Switch")

We use **Helm** and **ArgoCD** to manage the switch.

1.  **The Toggle**: A global value `global.isEphemeral: true` is set for CI/Local builds.
2.  **The Wiring**:
    *   If **True**: Connect apps to the internal Kubernetes Services (`minio`, `postgresql`).
    *   If **False**: Connect apps to External Names or IPs resolved from Terraform Outputs (`rds-endpoint`, `s3-bucket-name`).

## Developer Experience

### "It works on my machine"
Because the entire stack runs inside the cluster, you can replicate a bug found in CI exactly on your laptop using `Kind` or a remote ephemeral cluster.

### Limitations
*   **IAM Policies**: LocalStack's IAM emulation is permissive. It won't catch strict permission errors.
*   **Performance**: MinIO is often *faster* than S3. Don't benchmark performance locally.
*   **Quotas**: You won't hit AWS limits locally.

## Related ADRs
*   [ADR-0161: Standard Ephemeral Infrastructure Stack](../adrs/ADR-0161-ephemeral-infrastructure-stack.md)
