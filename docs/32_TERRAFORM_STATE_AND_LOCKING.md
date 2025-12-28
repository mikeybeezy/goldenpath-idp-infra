# Terraform State and Locking (Living)

This document explains where Terraform state lives, how locking works, and how
CI roles connect to the backend.

## Why this exists

Terraform uses a remote backend to:
- keep state durable and shared between runs
- prevent two applies from writing at the same time (state locking)

## Dev backend (current)

- **S3 bucket:** `goldenpath-idp-dev-bucket`
- **State key:** `envs/dev/terraform.tfstate`
- **Lock table:** `goldenpath-idp-dev-db-key`

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

## First-run behavior

If the state key does not exist, a first apply must run to create it.
Plans will fail to lock until the state object exists.

## References

- `docs/21_CI_ENVIRONMENT_CONTRACT.md`
- `.github/workflows/infra-terraform.yml`
