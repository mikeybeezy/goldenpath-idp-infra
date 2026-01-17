---
id: 33_IAM_ROLES_AND_POLICIES
title: IAM Roles and Policies Index (Living)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 01_GOVERNANCE
  - 21_CI_ENVIRONMENT_CONTRACT
  - 31_EKS_ACCESS_MODEL
  - 32_TERRAFORM_STATE_AND_LOCKING
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - RB-0003-iam-audit
category: security
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# IAM Roles and Policies Index (Living)

This is the single index of IAM roles and policies used by GoldenPath.
Use this to understand **who assumes what**, **where it is used**, and **why**.

## CI roles (GitHub Actions)

### `terraform_plan_read_only`

- **Purpose:** read-only Terraform plan against remote state.
- **Assumed by:** GitHub Actions (OIDC).
- **Used in:** `infra-terraform.yml`, `pr-terraform-plan.yml`.
- **Scope:** S3 state read + DynamoDB lock.

### `github-actions-terraform` (apply)

- **Purpose:** apply infrastructure changes.
- **Assumed by:** GitHub Actions (OIDC).
- **Used in:** `infra-terraform-apply-dev.yml`, `ci-teardown.yml`.
- **Scope:** S3/DynamoDB state + AWS infra create/update.
- **Teardown/orphan cleanup policy:** `docs/10-governance/policies/ci-teardown-orphan-cleanup.json`
  (delete actions require `BuildId` + `Environment` tags; read actions are unscoped).
- **Instance profile read policy:** `docs/10-governance/policies/ci-apply-iam-instance-profile-read.json`
  (required for Terraform to list IAM instance profiles when deleting roles).
- **Note:** IAM policies are excluded from orphan cleanup by design.

## Cluster roles (IRSA)

These roles are assumed by Kubernetes service accounts via IRSA.

### Cluster Autoscaler role

- **Purpose:** autoscaling node groups.
- **Assumed by:** service account `kube-system/cluster-autoscaler`.
- **Used in:** bootstrap (IRSA stage).
- **Policy ARN:** `arn:aws:iam::##########:policy/golden-path-cluster-autoscaler-policy`.

### AWS Load Balancer Controller role

- **Purpose:** provision/load balance AWS ELB resources.
- **Assumed by:** service account `kube-system/aws-load-balancer-controller`.
- **Used in:** bootstrap (IRSA stage).
- **Policy ARN:** `arn:aws:iam::##########:policy/goldenpath-load-balancer-controller-policy`.

## State and locking (dev)

- **S3 bucket:** `goldenpath-idp-dev-bucket`
- **DynamoDB lock table:** `goldenpath-idp-dev-db-key`
- **State keys:**
  - **Persistent:** `envs/dev/terraform.tfstate`
  - **Ephemeral (per BuildId):** `envs/dev/builds/<build_id>/terraform.tfstate`
- **Apply role access:** allow `envs/dev/builds/*` for ephemeral runs.

## Where roles are configured

- **GitHub Secrets:** role ARNs referenced in workflows.
- **Terraform variables:** IRSA policy ARNs set in `envs/dev/terraform.tfvars`.
- **Bootstrap:** IRSA service accounts created during bootstrap stage.

## V2: multi-account environment boundaries (planned)

GoldenPath V2 will require a **bounded context per environment**, especially for
teams operating in different AWS accounts. This means:

- Each environment (dev/test/staging/prod) can map to a distinct AWS account.
- CI roles are scoped per account and per environment (no shared wide role).
- Cross-account access is explicit (assume role into the target account).
- The IAM index will track roles by **environment + account** rather than a
  single global list.

## Related docs

- `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`
- `docs/60-security/31_EKS_ACCESS_MODEL.md`
- `docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md`
