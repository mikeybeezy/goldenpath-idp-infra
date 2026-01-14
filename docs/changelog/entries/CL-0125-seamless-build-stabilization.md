---
id: CL-0125
date: 2026-01-14
author: Michael Nouriel
status: Released
relates_to:
  - ADR-0148
  - ADR-0153
title: Seamless Build Stabilization and Identity Fixes
description: |
  Comprehensive fixes to the Seamless Build Deployment workflow to resolve identity collisions, script portability issues, and resource constraint failures.
---

# Seamless Build Stabilization

This release stabilizes the `make deploy` workflow, enabling true zero-touch provisioning of the EKS platform.

## 🐛 Bug Fixes

### 1. Identity Collision (ResourceInUseException)
*   **Issue**: Terraform attempted to create an `aws_eks_access_entry` for the cluster creator (current caller), conflicting with the default entry created by AWS.
*   **Fix**: Removed/Commented out the explicit `terraform_admin` access entry in `envs/dev/main.tf` (See [ADR-0153](../adrs/ADR-0153-cluster-provisioning-identity.md)).

### 2. Governance Script Portability (grep -P)
*   **Issue**: `scripts/record-build-timing.sh` failed on macOS due to incompatible Perl-regex syntax in `grep`.
*   **Fix**: Rewrote script to use `sed` for rigorous cross-platform compatibility.

### 3. Bootstrap Metadata Failure
*   **Issue**: `kubectl apply` in the bootstrap script failed when encountering `metadata.yaml` governance files in the ArgoCD apps directory.
*   **Fix**: Updated `bootstrap/40_platform-tooling/10_argocd_apps.sh` to strictly ignore `metadata.yaml` files.

### 4. Git Registry Resilience
*   **Issue**: Build pipeline crashed if the `governance-registry` branch was unreachable.
*   **Fix**: Implemented "Fail Open" logic in reporting scripts; connection failures now log a warning and proceed with the build.

### 5. Resource Constraints (vCPU Limit)
*   **Issue**: Default node counts (8+4) exceeded the AWS account vCPU quota (16), preventing cluster launch.
*   **Fix**: Optimised `terraform.tfvars` default node counts to 3 (Main) + 3 (Bootstrap) to fit within standard quotas.

## 🚀 Improvements

*   **Two-Phase Reliability**: The `_phase1-infrastructure` and `_phase2-bootstrap` targets are now fully idempotent and decoupled.
*   **Documentation**: Added `ADR-0153` to document the Identity Provisioning Strategy.
