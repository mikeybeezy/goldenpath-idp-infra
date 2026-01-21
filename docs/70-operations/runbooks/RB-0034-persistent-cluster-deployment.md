---
id: RB-0034-persistent-cluster-deployment
title: Persistent Cluster Deployment
type: runbook
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: terraform-destroy
  observability_tier: silver
  maturity: 1
relates_to:
  - 30_PLATFORM_RDS_ARCHITECTURE
  - 32_TERRAFORM_STATE_AND_LOCKING
  - 36_STATE_KEY_STRATEGY
  - ADR-0040-platform-lifecycle-aware-state-keys
  - DOCS_RUNBOOKS_README
  - RB-0031-idp-stack-deployment
  - RB-0032
  - RB-0033-persistent-cluster-teardown
category: runbooks
supported_until: 2028-01-17
version: '1.0'
breaking_change: false
---
# Persistent Cluster Deployment Runbook

This runbook covers deployment for **persistent** EKS clusters that use the root
state key (`envs/<env>/terraform.tfstate`). Platform RDS is managed in a
standalone state (`envs/<env>-rds/`) to prevent accidental deletion.

## When to Use

- Deploying a new cluster with `cluster_lifecycle=persistent`
- Deploying the platform RDS in standalone state (`envs/<env>-rds/`)
- Re-deploying a persistent cluster after teardown

## Persistent vs Ephemeral Mode

| Aspect | Ephemeral | Persistent |
|--------|-----------|------------|
| State key | `envs/dev/builds/{build_id}/terraform.tfstate` | `envs/dev/terraform.tfstate` |
| BUILD_ID | Required | Not used |
| Platform RDS | Not created | Standalone (`envs/<env>-rds/`) |
| Teardown | By BuildId tag | By ClusterName tag |

## Preconditions

1. AWS credentials with EKS/RDS create permissions
2. Terraform state bucket and lock table exist
3. VPC with private subnets tagged appropriately
4. Standalone RDS tfvars configured in `envs/<env>-rds/terraform.tfvars`

## Inputs

- `ENV` (e.g., `dev`)
- `REGION` (e.g., `eu-west-2`)

## Quick Start

```bash
# Full deployment (apply + rds-deploy + bootstrap)
make deploy-persistent ENV=dev REGION=eu-west-2
```

## Step-by-Step Deployment

### Step 1: Verify Prerequisites

```bash
# Check VPC exists with correct tags
aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=goldenpath-idp" "Name=tag:Environment,Values=dev" \
  --region eu-west-2 \
  --query 'Vpcs[0].VpcId'

# Check state bucket exists
aws s3 ls s3://goldenpath-idp-dev-bucket/envs/dev/ 2>/dev/null || echo "Bucket ready"
```

### Step 2: Verify tfvars Configuration

Ensure `envs/dev/terraform.tfvars` has:

```hcl
cluster_lifecycle = "persistent"  # Required for persistent clusters
rds_config = {
  enabled = false  # Standalone RDS is managed in envs/<env>-rds/
}
```

RDS settings live in `envs/dev-rds/terraform.tfvars`.

### Step 3: Initialize Terraform

```bash
# Makefile handles backend config automatically
make init ENV=dev
```

Or manually with explicit backend:

```bash
terraform -chdir=envs/dev init \
  -backend-config="bucket=goldenpath-idp-dev-bucket" \
  -backend-config="key=envs/dev/terraform.tfstate" \
  -backend-config="region=eu-west-2" \
  -backend-config="dynamodb_table=goldenpath-idp-dev-locks"
```

### Step 4: Plan (Optional)

```bash
make plan ENV=dev
```

Review the plan to confirm:
- EKS cluster will be created
- No unexpected deletions

### Step 5: Apply Infrastructure

```bash
make apply-persistent ENV=dev REGION=eu-west-2
```

This runs:
```bash
terraform apply \
  -var="cluster_lifecycle=persistent" \
  -var="enable_k8s_resources=true" \
  -var="apply_kubernetes_addons=false"
```

Expected duration: 15-25 minutes

### Step 6: Deploy Standalone RDS + Provision Users

```bash
make rds-deploy ENV=dev
```

This initializes, applies, and provisions the standalone RDS state from
`envs/dev-rds/terraform.tfvars`.

By default, `rds-deploy` restores any scheduled-for-deletion secrets and adopts
existing secrets into state before apply. To skip this preflight:

```bash
make rds-deploy ENV=dev RESTORE_SECRETS=false
```

### Step 7: Bootstrap Platform

```bash
make bootstrap-persistent ENV=dev REGION=eu-west-2
```

This installs:
- ArgoCD
- External Secrets Operator
- cert-manager
- Kong Ingress Controller

### Step 8: Verify Deployment

```bash
# Check nodes
kubectl get nodes

# Check ArgoCD applications
kubectl get applications -n argocd

# Check core pods
kubectl get pods -n argocd
kubectl get pods -n external-secrets
kubectl get pods -n kong-system
```

## One-Command Deployment

For convenience, use the combined target:

```bash
make deploy-persistent ENV=dev REGION=eu-west-2
```

This runs steps 5-8 in sequence:
1. `apply-persistent` - Terraform apply
2. `rds-deploy` - Standalone RDS apply + provisioning
3. `bootstrap-persistent` - Platform bootstrap
4. `_phase3-verify` - Verification

To skip RDS creation:

```bash
make deploy-persistent ENV=dev REGION=eu-west-2 CREATE_RDS=false
```

## Troubleshooting

### Terraform Init Fails

```
Error: Failed to get existing workspaces
```

Check S3 bucket permissions and ensure the bucket exists.

### RDS Blocked in Ephemeral Mode

```
ERROR: Coupled RDS is not allowed in ephemeral EKS builds.
```

Set `cluster_lifecycle = "persistent"` in terraform.tfvars or use standalone RDS.

### Bootstrap Fails - Cluster Not Found

```
error: couldn't get resource list for external-secrets.io/v1beta1
```

Wait for EKS to be fully ready:
```bash
aws eks wait cluster-active --name goldenpath-dev-eks --region eu-west-2
aws eks update-kubeconfig --name goldenpath-dev-eks --region eu-west-2
```

### RDS Connection Timeout

Check security group allows traffic from EKS nodes:
```bash
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*rds*" \
  --region eu-west-2 \
  --query 'SecurityGroups[*].[GroupId,GroupName]'
```

## Rollback

To destroy a persistent deployment:

```bash
make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes
```

See [RB-0033-persistent-cluster-teardown](RB-0033-persistent-cluster-teardown.md) for details.

## Related Documentation

- [RB-0031-idp-stack-deployment](RB-0031-idp-stack-deployment.md) - IDP application deployment (Keycloak, Backstage)
- [RB-0032-rds-user-provision](RB-0032-rds-user-provision.md) - RDS user provisioning details
- [RB-0033-persistent-cluster-teardown](RB-0033-persistent-cluster-teardown.md) - Teardown procedure
- [30_PLATFORM_RDS_ARCHITECTURE](../30_PLATFORM_RDS_ARCHITECTURE.md) - RDS architecture overview

## Command Reference

| Command | Description |
|---------|-------------|
| `make deploy-persistent ENV=dev REGION=eu-west-2` | Full deployment |
| `make apply-persistent ENV=dev REGION=eu-west-2` | Infrastructure only |
| `make bootstrap-persistent ENV=dev REGION=eu-west-2` | Bootstrap only |
| `make teardown-persistent ENV=dev REGION=eu-west-2 CONFIRM_DESTROY=yes` | Destroy |
