# Tear Down and Cleanup Scripts

This folder contains cleanup helpers for AWS resources. Run them when Terraform
or a manual teardown gets stuck.

## goldenpath-idp-teardown.sh

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
  - Orphan cleanup is running (when CLEANUP_ORPHANS=true).

Set `HEARTBEAT_INTERVAL` to change the cadence (default `30` seconds).

Terraform destroy instead of aws eks delete:

```bash
TEARDOWN_CONFIRM=true TF_DIR=envs/dev \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
```

Optional cleanup by BuildId:

```bash
TEARDOWN_CONFIRM=true CLEANUP_ORPHANS=true BUILD_ID=20250115-01 \
  bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster> <region>
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
  SGs, IGWs, VPCs).

Examples:

```bash
bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
DRY_RUN=false bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
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
