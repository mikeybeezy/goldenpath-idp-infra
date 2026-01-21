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
- Determine whether RDS is coupled (`rds_config.enabled=true` in `envs/<env>/terraform.tfvars`)
  or managed in standalone state (`envs/<env>-rds/`).

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

## Step 2 (Optional): Break-Glass Standalone RDS Teardown

If RDS is deployed in its own state (`envs/<env>-rds/`) and must be deleted,
complete this **before** cluster teardown. This preserves VPC and subnet
dependencies until the database is gone.

You have two supported options:

**Option A: Manual toggle (main.tf)**
1. Edit `envs/<env>-rds/main.tf` and set `prevent_destroy = false` (temporary).
2. Run: `terraform -chdir=envs/<env>-rds destroy -auto-approve`
3. Restore `prevent_destroy = true` after completion.

**Option B: Break-glass target (recommended)**
```bash
make rds-destroy-break-glass ENV=dev CONFIRM_DESTROY_DATABASE_PERMANENTLY=YES
```

The break-glass target:
- Disables AWS deletion protection first.
- Temporarily flips `prevent_destroy` in `envs/<env>-rds/main.tf`.
- Requires explicit confirmation.

If you want to reuse existing Secrets Manager entries, **do not** force-delete
the secrets after destroy.

## Step 3: Run Persistent Teardown

```bash
make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes
```

This runs the v4 teardown script with `TF_DIR=envs/<env>` and destroys the
persistent Terraform state. If RDS is coupled in that state, **Terraform will
destroy it** regardless of teardown safety flags. The safety flags only affect
extra cleanup steps (Secrets Manager, orphan cleanup), not the core
`terraform destroy`.

To explicitly delete RDS or Secrets, set the flags at runtime:

```bash
DELETE_RDS_INSTANCES=true \
RDS_SKIP_FINAL_SNAPSHOT=false \
DELETE_SECRETS=true \
make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes
```

Note: workflow inputs use `build_id`, but the canonical Makefile variable is `BUILD_ID`.

If you need RDS to survive cluster rebuilds, use the standalone RDS state
(`envs/<env>-rds/`) and set `rds_config.enabled=false` in the cluster tfvars
before teardown.

## Step 4: Verify Deletion

```bash
aws eks list-clusters --region eu-west-2
aws rds describe-db-instances --region eu-west-2
aws secretsmanager list-secrets --region eu-west-2
```

## Troubleshooting

- **State lock error**: See `docs/70-operations/runbooks/RB-0007-tf-state-force-unlock.md`.
- **RDS deletion protection**: Run `make rds-allow-delete ENV=<env> CONFIRM_RDS_DELETE=yes` before destroy.
- **Leftover resources**: Use `RB-0017-orphan-cleanup.md` to remove orphans.

### State Lock Recovery

If teardown fails due to a Terraform state lock, use the lock ID from the error
message and force-unlock the state:

```bash
terraform -chdir=envs/dev force-unlock -force <lock-id>
```

Example:

```bash
terraform -chdir=envs/dev force-unlock -force eeed8a4d-ade1-19cd-1b0d-6fc93a4b18cc
```

## Notes

- Persistent teardown is destructive and should be used sparingly.
- RDS and Secrets deletion require explicit opt-in flags.
- Ephemeral builds must use `make teardown` with `BUILD_ID`.
