---
id: 20_CI_ENVIRONMENT_SEPARATION
title: CI Environment Separation (Living Document)
type: contract
risk_profile:
  production_impact: high
  security_risk: none
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0016-platform-ci-environment-separation
  - ADR-0017-platform-policy-as-code
  - ADR-0036-platform-orphan-cleanup-workflow
  - CI_WORKFLOWS
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# CI Environment Separation (Living Document)

Doc contract:

- Purpose: Summarize how CI workflows are separated by environment.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, ci-workflows/CI_WORKFLOWS.md, docs/adrs/ADR-0016-platform-ci-environment-separation.md

This document captures the current CI environment separation implementation. It is a living
reference and should evolve as the platform grows.

## Current approach

- PR workflow: `pr-terraform-plan.yml` posts plan output and runs fmt/validate guards.
- Manual apply workflows: `infra-terraform-apply-<env>.yml` apply with explicit confirmation.
- Optional manual checks: `infra-terraform.yml` runs fmt/validate/plan on demand.
- Environment separation: GitHub Environments named `dev`, `test`, `staging`, `prod`.
- Manual gates: apply steps run only when `confirm_apply=apply` is selected.
- Access model: GitHub Actions uses AWS OIDC and environment-scoped IAM roles.
- PR workflow: `pr-terraform-plan.yml` posts plan output as a PR comment (dev only).

## Current dev implementation

- Plan source: PR plan (dev) or optional `infra-terraform.yml`.
- Manual apply: `infra-terraform-apply-dev.yml` with `confirm_apply=apply`.
- Plan role secret: `secrets.TF_AWS_IAM_ROLE_DEV`.
- Apply role secret: `secrets.TF_AWS_IAM_ROLE_DEV_APPLY`.
- Region: `eu-west-2`.
- Backend:
  - S3 bucket: `goldenpath-idp-dev-bucket`
  - DynamoDB lock table: `goldenpath-idp-dev-db-key`
  - State keys:
    - Persistent: `envs/dev/terraform.tfstate`
    - Ephemeral (per BuildId): `envs/dev/builds/<build_id>/terraform.tfstate`

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
