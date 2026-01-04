---
id: TEARDOWN_README
title: Tear Down and Cleanup Scripts
type: documentation
category: bootstrap
version: 1.0
owner: platform-team
status: active
dependencies:
- module:kubernetes
- module:terraform
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- BOOTSTRAP_README
- GOLDENPATH_IDP_BOOTSTRAP
- ADR-0036
- 15_TEARDOWN_AND_CLEANUP
- 17_BUILD_RUN_FLAGS
---

# Tear Down and Cleanup Scripts

This folder contains cleanup helpers for AWS resources. Run them when Terraform
or a manual teardown gets stuck.

## Teardown runner versions

We keep a stable teardown runner and a v2 iteration track:

- `goldenpath-idp-teardown.sh` (v1, default)
- `goldenpath-idp-teardown-v2.sh` (v2, iteration track)

The Makefile selects the script via `TEARDOWN_VERSION` (`v1` or `v2`).
CI exposes the same choice as a workflow input.

## goldenpath-idp-teardown.sh (v1)

What it does:

- Updates kubeconfig for the target cluster.
- Removes LoadBalancer services to release AWS LBs and SGs.
- Drains and deletes node groups.
- Deletes the cluster (or runs Terraform destroy if TF_DIR is set).
- Optionally runs tag-based orphan cleanup by BuildId.

Safety:

- Requires `TEARDOWN_CONFIRM=true` to run destructive steps.
- You can skip parts with flags (see usage below).

Examples:

```bash
TEARDOWN_CONFIRM=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Run the v2 runner directly:

```bash
TEARDOWN_CONFIRM=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh <cluster> <region>
```

Select v2 via Makefile:

```bash
TEARDOWN_VERSION=v2 make teardown ENV=dev BUILD_ID=<build_id> CLUSTER=<cluster> REGION=<region>
```

PDB-safe drain (default behavior):

```bash
TEARDOWN_CONFIRM=true RELAX_PDB=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Drain timeout and retry behavior:

- The drain step uses `DRAIN_TIMEOUT` (default `300s`).
- If the drain times out, it relaxes CoreDNS PDBs and retries once.

Example:

```bash
TEARDOWN_CONFIRM=true RELAX_PDB=true DRAIN_TIMEOUT=300s \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Progress heartbeats:

- The teardown runner prints a heartbeat every 30s while:
  - LoadBalancer services are deleting.
  - Node groups are deleting.
  - The cluster is deleting.
  - Terraform destroy is running (when TF_DIR is set).
  - Orphan cleanup is running (when CLEANUP_ORPHANS=true and mode is not `none`).

Set `HEARTBEAT_INTERVAL` to change the cadence (default `30` seconds).

LoadBalancer cleanup retries:

- The runner re-attempts LoadBalancer Service deletion in case the controller
  or AWS is slow to reconcile.
- `LB_CLEANUP_ATTEMPTS` controls how many retry loops run (default `5`).
- `LB_CLEANUP_INTERVAL` controls the delay between loops (default `20` seconds).
- `LB_CLEANUP_MAX_WAIT` caps the LoadBalancer wait loop in Stage 2
  to avoid hanging (default `900` seconds).
- v2 defaults to break-glass finalizer removal with
  `FORCE_DELETE_LB_FINALIZERS=true` when Services are stuck in `Terminating`.
  This default prevents teardown hangs when the LB controller is not available.
- If Kubernetes access is unavailable, v2 skips Kubernetes cleanup and performs
  AWS-only LoadBalancer cleanup before destroy.

LoadBalancer ENI wait (prevents stuck subnet deletes):

- After LoadBalancer Services are gone, the script waits for any
  network load balancer ENIs to disappear.
- `WAIT_FOR_LB_ENIS` controls this wait (default `true`).
- `LB_ENI_WAIT_MAX` caps the ENI wait loop (default `LB_CLEANUP_MAX_WAIT`).
- `FORCE_DELETE_LBS` defaults to `true` and deletes remaining Kubernetes LBs
  if ENIs do not disappear in time. Deletion is scoped to LBs with
  `elbv2.k8s.aws/cluster=${cluster_name}`.

Example:

```bash
TEARDOWN_CONFIRM=true LB_CLEANUP_ATTEMPTS=8 LB_CLEANUP_INTERVAL=30 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Force delete remaining cluster LBs (optional override):

```bash
TEARDOWN_CONFIRM=true FORCE_DELETE_LBS=true \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Terraform destroy guard:

- `REQUIRE_KUBE_FOR_TF_DESTROY` (default `true`) verifies kube access before
  Terraform destroy to avoid localhost Kubernetes provider errors.
- `REMOVE_K8S_SA_FROM_STATE` (default `true`) removes Kubernetes service
  accounts from state before Terraform destroy to avoid kube access failures.
  The script will attempt a lightweight `terraform init` if state access fails.
- `TF_AUTO_APPROVE` (default `false`) uses `-auto-approve` for Terraform
  destroy. The Makefile teardown targets set this to `true`.
- If Terraform destroy fails or is skipped, the script can fall back to AWS
  cluster deletion when `TF_DESTROY_FALLBACK_AWS=true` (default: false).

Argo CD application cleanup:

- Teardown deletes the configured Argo CD Application before deleting
  LoadBalancer Services to prevent GitOps reconciliation from recreating them.
- `DELETE_ARGO_APP` (default `true`) skips or enables this step.
- `ARGO_APP_NAMESPACE` (default `kong-system`) selects the namespace.
- `ARGO_APP_NAME` (default `dev-kong`) selects the application.

Terraform destroy instead of aws eks delete:

```bash
TEARDOWN_CONFIRM=true TF_DIR=envs/dev \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Optional cleanup by BuildId:

```bash
TEARDOWN_CONFIRM=true CLEANUP_ORPHANS=true ORPHAN_CLEANUP_MODE=delete BUILD_ID=20250115-01 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Dry-run orphan discovery during teardown:

```bash
TEARDOWN_CONFIRM=true CLEANUP_ORPHANS=true ORPHAN_CLEANUP_MODE=dry_run BUILD_ID=20250115-01 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

## remove-k8s-service-accounts-from-state.sh

What it does:

- Removes `kubernetes_service_account_v1` entries from Terraform state.
- Useful when the cluster is already gone and Terraform would otherwise fail.

Examples:

```bash
bootstrap/60_tear_down_clean_up/remove-k8s-service-accounts-from-state.sh envs/dev
```

## cleanup-iam.sh

What it does:

- Finds IAM roles and policies that start with `goldenpath-`.
- Detaches policies, deletes inline policies, then deletes the roles.
- Deletes local IAM policies with the same prefix.

Safety:

- Runs in **dry-run** mode by default.
- Use `--yes` to actually delete.

Examples:

```bash
bootstrap/60_tear_down_clean_up/cleanup-iam.sh
bootstrap/60_tear_down_clean_up/cleanup-iam.sh --yes
```

## cleanup-orphans.sh

What it does:

- Deletes AWS resources tagged with a `BuildId` (EKS, LBs, EC2, NAT, subnets,
  EIPs, ENIs, route tables, SGs, IGWs, VPCs, IAM roles).

Safety:

- Never deletes the Terraform state S3 bucket or the DynamoDB lock table.

Examples:

```bash
bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
DRY_RUN=false bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
```

## cleanup-managed-lb-resources.sh

What it does:

- Deletes AWS Load Balancer Controller managed LBs, ENIs, and security groups
  tagged with `elbv2.k8s.aws/cluster=<cluster>`.
- Optionally narrows the scope with `service.k8s.aws/stack=<stack>`.

Safety:

- Runs in **dry-run** mode by default.
- Deletes only resources tagged to the cluster (and optional stack).
- `DELETE_CLUSTER_TAGGED_SGS=true` expands scope to any security group tagged
  with `elbv2.k8s.aws/cluster=<cluster>`.

Examples:

```bash
bootstrap/60_tear_down_clean_up/cleanup-managed-lb-resources.sh <cluster> <region>
DRY_RUN=false bootstrap/60_tear_down_clean_up/cleanup-managed-lb-resources.sh <cluster> <region>
STACK_TAG="kong-system/dev-kong-kong-proxy" DRY_RUN=false \
  bootstrap/60_tear_down_clean_up/cleanup-managed-lb-resources.sh <cluster> <region>
DELETE_CLUSTER_TAGGED_SGS=true DRY_RUN=false \
  bootstrap/60_tear_down_clean_up/cleanup-managed-lb-resources.sh <cluster> <region>
```

## pre-destroy-cleanup.sh

What it does:

- Deletes Kubernetes `LoadBalancer` services to release AWS LBs and SGs before
  destroying the VPC.

Examples:

```bash
bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh <cluster> <region>
bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh <cluster> <region> --yes
```

## drain-nodegroup.sh

What it does:

- Cordon and drain nodes in a node group before replacement.

Examples:

```bash
bootstrap/60_tear_down_clean_up/drain-nodegroup.sh <nodegroup-name>
```
