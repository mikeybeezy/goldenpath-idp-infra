# CI Environment Separation (Living Document)

This document captures the current CI environment separation implementation. It is a living
reference and should evolve as the platform grows.

## Current approach

- Single workflow: `infra-terraform.yml` handles plan/apply via `workflow_dispatch`.
- Environment separation: GitHub Environments named `dev`, `test`, `staging`, `prod`.
- Manual gates: apply steps are protected by Environment approvals.
- Access model: GitHub Actions uses AWS OIDC and environment-scoped IAM roles.

## Current dev implementation

- Workflow input: `env=dev`.
- GitHub Environment: `dev` (used for manual approval of apply).
- Role secret: `secrets.TF_AWS_IAM_ROLE_DEV`.
- Region: `eu-west-2`.
- Backend:
  - S3 bucket: `goldenpath-idp-dev-bucket`
  - DynamoDB lock table: `goldenpath-idp-dev-db-key`
  - State key: `envs/dev/terraform.tfstate`

## Planned extensions

- Add `test`, `staging`, `prod` roles, buckets, and lock tables.
- Map workflow inputs to the correct environment-specific secrets and backends.
- Optionally split workflows per environment for teams needing stricter boundaries.

## Change process

For material changes:
1. Create or update an ADR.
2. Update governance guidance.
3. Refresh this living document to reflect current implementation.
