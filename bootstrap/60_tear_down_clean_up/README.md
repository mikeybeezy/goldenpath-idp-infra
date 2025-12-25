# Tear Down and Cleanup Scripts

This folder contains cleanup helpers for AWS resources. Run them when Terraform
or a manual teardown gets stuck.

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
