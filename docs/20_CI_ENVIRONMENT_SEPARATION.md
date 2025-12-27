# CI Environment Separation (Living Document)

This document captures the current CI environment separation implementation. It is a living
reference and should evolve as the platform grows.

## Current approach

- Single workflow: `infra-terraform.yml` handles plan/apply via `workflow_dispatch`.
- Environment separation: GitHub Environments named `dev`, `test`, `staging`, `prod`.
- Manual gates: apply steps run only when `apply=true` is set at workflow dispatch.
- Access model: GitHub Actions uses AWS OIDC and environment-scoped IAM roles.
- PR workflow: `pr-terraform-plan.yml` posts plan output as a PR comment (dev only).

## Current dev implementation

- Workflow input: `env=dev`.
- Manual apply toggle: `apply=true` at workflow dispatch.
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
- Consider GitHub Environments as a future manual-approval gate if licensing allows.

## Change process

For material changes:

1. Create or update an ADR.
2. Update governance guidance.
3. Refresh this living document to reflect current implementation.
