---
id: 32_TERRAFORM_STATE_AND_LOCKING
title: Terraform State and Locking (Living)
type: policy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 07_TF_STATE_FORCE_UNLOCK
  - 21_CI_ENVIRONMENT_CONTRACT
  - 33_IAM_ROLES_AND_POLICIES
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - 36_STATE_KEY_STRATEGY
  - 70_OPERATIONS_README
  - ADR-0040-platform-lifecycle-aware-state-keys
category: compliance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Terraform State and Locking (Living)

Doc contract:

- Purpose: Explain Terraform state storage, locking, and CI backend access.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/70-operations/36_STATE_KEY_STRATEGY.md, docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/70-operations/runbooks/07_TF_STATE_FORCE_UNLOCK.md

This document explains where Terraform state lives, how locking works, and how
CI roles connect to the backend.

## Why this exists

Terraform uses a remote backend to:

- keep state durable and shared between runs
- prevent two applies from writing at the same time (state locking)

## Dev backend (current)

- **S3 bucket:** `goldenpath-idp-dev-bucket`
- **Lock table:** `goldenpath-idp-dev-db-key`
- **State keys:**
  - **Persistent:** `envs/dev/terraform.tfstate`
  - **Ephemeral (per BuildId):** `envs/dev/builds/<build_id>/terraform.tfstate`

## How it connects

```
PR / Plan (read-only role)
  -> S3 (read state)
  -> DynamoDB (acquire lock)

Apply (write role)
  -> S3 (read/write state)
  -> DynamoDB (acquire/release lock)

Bootstrap
  -> Uses cluster name from state
  -> Does not write Terraform state
```

## Plan role permissions (dev)

Plan needs read-only access to the state object plus lock access to the table.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformStateRead",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::goldenpath-idp-dev-bucket",
        "arn:aws:s3:::goldenpath-idp-dev-bucket/envs/dev/terraform.tfstate"
      ]
    },
    {
      "Sid": "TerraformStateLock",
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:eu-west-2:593517239005:table/goldenpath-idp-dev-db-key"
    }
  ]
}
```

## Ephemeral state access (apply roles)

Ephemeral CI runs store state per BuildId. Apply roles must allow access to
the `envs/dev/builds/*` prefix in the state bucket.

## First-run behavior

For **persistent** runs, the state key must exist; a first apply creates it.
For **ephemeral** runs, the state key is created on the first apply for that
BuildId, so a missing key is expected on a fresh build.

## References

- `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`
- `docs/60-security/33_IAM_ROLES_AND_POLICIES.md`
- `.github/workflows/infra-terraform.yml`
