---
id: goldenpath-idp-bootstrap
title: Helm Bootstrap Runner (Non-Production)
type: documentation
category: bootstrap
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - ONE_STAGE_VS_MULTISTAGE_BOOTSTRAP
  - ADR-0001
  - ADR-0002
  - ADR-0013
  - ARGOCD_HELM_README
  - 18_BACKSTAGE_MVP
---

# Helm Bootstrap Runner (Non-Production)

This document explains what `bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh` does and when to run it.

## Purpose

The runner orchestrates the full bootstrap flow against a fresh EKS cluster. It is intended for:

- Ephemeral eksctl clusters (daily teardown) so tooling comes online immediately.
- Terraform-managed clusters after provisioning completes.
- Local testing environments where you want the same GitOps flow as production.

## What the Script Does

1. Ensures the AWS, kubectl, and helm CLIs are installed.
2. Updates kubeconfig for the target cluster.
3. Runs the prereq checks.
4. Optionally applies Terraform-managed Kubernetes resources (service accounts) once kubeconfig is ready.
5. Installs Metrics Server early for scheduling sanity checks.
6. Installs Argo CD via Helm.
7. Validates core add-ons (AWS Load Balancer Controller, cert-manager).
8. Applies the Cluster Autoscaler app first and waits for it to be ready.
9. Applies the remaining Argo CD apps (excluding Kong).
10. Installs and validates Kong.
11. Runs the audit report.

Argo CD admin access is handled via the dedicated helper script:
`bootstrap/10_gitops-controller/20_argocd_admin_access.sh`.

## Usage

```sh
./bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh [<cluster-name> <region> [kong-namespace]]
```

If you omit `<cluster-name>` and `<region>`, the runner will try to read
`cluster_name` and `region` from `TF_DIR/terraform.tfvars`:

```sh
TF_DIR=envs/dev ./bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh
```

Run this once per cluster after it becomes reachable by kubectl.

## Runner vs individual scripts

Use the runner when you want a clean, repeatable one-shot bootstrap for a new
cluster. It enforces the full sequence and runs the standard checks.

Use individual scripts when you need to rerun or debug a specific step, or
when you are customizing the sequence (for example, skipping Kong until later).

## Current bootstrap defaults

These defaults keep the node group stable and reduce early pressure:

- `bootstrap_mode` = `true`
- `min_size` = 3
- `desired_size` = 3
- `max_size` = 5
- `enable_ssh_break_glass` = `false`
- `enable_storage_addons` = `true` (EBS/EFS/snapshot required for persistent monitoring data)
- `SKIP_ARGO_SYNC_WAIT` = `true` (default, skips Argo app sync waits)
 - `COMPACT_OUTPUT` = `false` (set to `true` to reduce noisy command output)

The runner prints an Argo status summary at the end and warns if any app shows
`HEALTH=Unknown`.

If `ENABLE_TF_K8S_RESOURCES=true` and `TF_DIR` is set, the runner performs a
second Terraform apply with `enable_k8s_resources=true` to create the
service accounts once the cluster is reachable.
The runner will fail if `BUILD_ID` and the Terraform `build_id` do not match.

If `SCALE_DOWN_AFTER_BOOTSTRAP=true`, the runner applies
`bootstrap_mode=false`. Set `TF_AUTO_APPROVE=true` to avoid the manual
Terraform approval prompt.

Recommendation: default `SCALE_DOWN_AFTER_BOOTSTRAP=false` so the initial
bootstrap has stable capacity while Argo apps and add-ons converge. Scale down
after verifying key pods are healthy.

## Suggested Enhancements / Alternatives

- **Terraform integration**: run this after `terraform apply` to standardize platform bring-up.
- **Secrets management**: store Git credentials in a secret manager and inject via CI/CD.
- **Runner hardening**: move to a CI pipeline once the flow is stable.
