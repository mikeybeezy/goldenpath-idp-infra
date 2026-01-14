---
id: ADR-0153
title: Cluster Provisioning Identity and Script Resilience
status: Accepted
date: 2026-01-14
deciders:
  - Michael Nouriel
  - Platform Team
consents:
  - Architecture Review Board
relates_to:
  - ADR-0148
  - ADR-0150
---

# Cluster Provisioning Identity and Script Resilience

## Context

During the implementation of the "Seamless Build Deployment" (ADR-0148), two significant operational blockers were identified that affected the reliability and portability of the build process:

1.  **Identity Collision**: When running Terraform as a user (e.g., `michaelnouriel`) who creates the EKS cluster, AWS automatically grants `system:masters` permissions to that user. However, our Terraform configuration explicitly attempted to create an `aws_eks_access_entry` for the current caller identity. This resulted in `ResourceInUseException` errors, causing the build to fail because the entry already existed implicitly.
2.  **Script Portability & Resilience**: The build telemetry script (`record-build-timing.sh`) utilized `grep -P` (Perl-compatible regex), which is not supported by default on macOS BSD based utilities. Furthermore, git operations within the script (checking out the governance registry) were "blocking," meaning a failure to fetch the remote branch caused the entire cluster deployment to fail (Error 1).

## Decision

We are adopting the following strategies to ensure robust and portable provisioning:

### 1. Implicit Admin Access for Provisioner
We will **NOT** explicitly manage the `aws_eks_access_entry` for the Terraform Runner (the principal executing the build) within the Terraform state.
*   **Rationale**: The creator of the EKS cluster is automatically granted admin permissions by AWS. Attempting to manage this resource explicitly causes unnecessary state conflicts and `ResourceInUse` errors.
*   **Implementation**: The `terraform_admin` access entry resource in `main.tf` will be removed or commented out. We rely on the AWS default behavior for the creator's access.

### 2. Transition to Dedicated Provisioning Role (Strategic)
In the future, we will transition away from using personal user credentials for provisioning and adopt a dedicated IAM Role (e.g., `GoldenPathProvisioner`).
*   **Pros**:
    *   **Continuity**: The cluster is owned by a Role, not a specific transient employee.
    *   **Security**: Minimal least-privilege permissions scoped to provisioning.
    *   **Consistency**: Eliminates "it works on my machine" issues related to varying user permissions.
*   **Cons**: Requires initial bootstrapping of the Role and `sts:AssumeRole` workflow integration.

### 3. Non-Blocking Governance Telemetry ("Fail Open")
Auxiliary scripts such as `record-build-timing.sh` must operate in a **Non-Blocking (Fail Open)** mode.
*   **Rationale**: Governance and telemetry are critical, but they should not prevent a cluster from coming online if the registry is unreachable or if a local tool version mismatch occurs.
*   **Implementation**:
    *   Git operations (checkout/push) in reporting scripts will be wrapped in try/catch blocks or use `exit 0` on failure, logging a warning instead of halting the pipeline.
    *   Scripts will use standard POSIX or broadly compatible utilities (e.g., `sed` instead of `grep -P`) to ensure compatibility across Linux (CI) and macOS (Local Dev).

## Consequences

### Positive
*   **Reliability**: Builds will no longer fail due to benign identity collisions.
*   **Portability**: Scripts will function correctly on both macOS and Linux environments.
*   **Resilience**: Network glitches affecting the governance registry will not block infrastructure delivery.

### Negative
*   **Traceability Risk**: If the governance registry is unreachable, build timing data for that specific run may be lost (local log only), creating a gap in the central metric store. This is an acceptable trade-off for operational uptime.
