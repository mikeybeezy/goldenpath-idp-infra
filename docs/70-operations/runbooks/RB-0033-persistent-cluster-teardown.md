---
id: RB-0033-persistent-cluster-teardown
title: Persistent Cluster Teardown
type: runbook
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
relates_to:
  - 32_TERRAFORM_STATE_AND_LOCKING
  - 36_STATE_KEY_STRATEGY
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ADR-0161
  - CL-0145
  - DOCS_RUNBOOKS_README
  - EC-0009-goldenpath-cli
  - RB-0007-tf-state-force-unlock
  - RB-0017-orphan-cleanup
  - RB-0030-rds-break-glass-deletion
  - RB-0031-idp-stack-deployment
  - RB-0034-persistent-cluster-deployment
  - agent_session_summary
  - session-2026-01-17-eks-backstage-scaffolder
category: runbooks
supported_until: 2028-01-17
version: '1.0'
breaking_change: false
---
# Persistent Cluster Teardown Runbook

This runbook covers teardown for **persistent** EKS clusters that use the root
state key (`envs/<env>/terraform.tfstate`). It does **not** apply to ephemeral
builds with a `build_id`.

## When to Use

- You deployed a persistent cluster (no `build_id`) and must destroy it.
- You need to remove a coupled RDS + EKS stack created in persistent mode.

## Preconditions

- Confirm the cluster is persistent (state key is `envs/<env>/terraform.tfstate`).
- Ensure the cluster is not shared by other teams.
- You have AWS credentials for the apply role.

## Inputs

- `ENV` (e.g., `dev`)
- `REGION` (e.g., `eu-west-2`)
- Optional `CLUSTER` override if the cluster name differs
- `CONFIRM_DESTROY=yes` (required safety gate)

## Step 1: Initialize Terraform (Persistent State)

Use the persistent state key (no `build_id`):

```bash
terraform -chdir=envs/dev init \
  -backend-config="bucket=goldenpath-idp-dev-bucket" \
  -backend-config="key=envs/dev/terraform.tfstate" \
  -backend-config="region=eu-west-2" \
  -backend-config="dynamodb_table=goldenpath-idp-dev-locks"
```

## Step 2: Run Persistent Teardown

```bash
make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes
```

This runs the teardown script with `TF_DIR=envs/<env>` and destroys the
persistent Terraform state.

## Step 3: Verify Deletion

```bash
aws eks list-clusters --region eu-west-2
aws rds describe-db-instances --region eu-west-2
aws secretsmanager list-secrets --region eu-west-2
```

## Troubleshooting

- **State lock error**: See `docs/70-operations/runbooks/RB-0007-tf-state-force-unlock.md`.
- **RDS deletion protection**: Disable in the AWS Console before teardown.
- **Leftover resources**: Use `RB-0017-orphan-cleanup.md` to remove orphans.

## Notes

- Persistent teardown is destructive and should be used sparingly.
- Ephemeral builds must use `make teardown` with `BUILD_ID`.
