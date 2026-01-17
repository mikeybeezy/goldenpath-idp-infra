---
id: 36_STATE_KEY_STRATEGY
title: State Key Strategy (Living)
type: policy
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
  - 25_PR_TERRAFORM_PLAN
  - 32_TERRAFORM_STATE_AND_LOCKING
  - 70_OPERATIONS_README
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ADR-0046-platform-pr-plan-validation-ownership
category: compliance
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# State Key Strategy (Living)

Doc contract:

- Purpose: Define lifecycle-aware Terraform state key usage.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md, docs/adrs/ADR-0040-platform-lifecycle-aware-state-keys.md

This document explains how Terraform state keys are chosen for persistent and
ephemeral builds, and how to use them in CI.

## Why this exists

We run two kinds of infrastructure lifecycles:

- **Persistent:** long-lived platform environments.
- **Ephemeral:** short-lived builds for rapid iteration.

Using a single state key for both causes stale state reuse and drift. We now
isolate ephemeral runs by BuildId so a new BuildId always starts clean.

## State key rules

- **Persistent:** `envs/<env>/terraform.tfstate`
- **Ephemeral:** `envs/<env>/builds/<build_id>/terraform.tfstate`

`build_id` is required when `cluster_lifecycle=ephemeral`.

## CI flow by intent

### 1) Fresh ephemeral build (new BuildId, clean slate)

Use when you want a new cluster and empty state.

1. Set `cluster_lifecycle=ephemeral` and a new `build_id`.
2. Ensure a plan exists (PR Terraform Plan or `infra-terraform.yml` with `lifecycle=ephemeral`).
3. Run `infra-terraform-apply-dev.yml` with `lifecycle=ephemeral` and the same `build_id`.
4. Run `ci-bootstrap.yml` with the same `build_id` if you need platform bootstrap.

Result: Terraform uses `envs/dev/builds/<build_id>/terraform.tfstate`.

### 2) Update an existing ephemeral build

Use when you want to modify the current ephemeral cluster (for example, add a
Route 53 record or a new AZ).

1. Keep the **same** `build_id` used for the existing cluster.
2. Run plan/apply with the same lifecycle/build_id.

Result: Terraform reads the existing ephemeral state and applies changes in place.

### 3) Update persistent platform infra

Use when you need to change long-lived infrastructure.

1. Set `cluster_lifecycle=persistent` (BuildId optional).
2. Ensure a plan exists (PR Terraform Plan or `infra-terraform.yml` with `lifecycle=persistent`).
3. Run `infra-terraform-apply-dev.yml` with `lifecycle=persistent`.

Result: Terraform uses `envs/dev/terraform.tfstate`.

## CI workflow mapping

| Workflow | Lifecycle-aware state key |
| --- | --- |
| `infra-terraform.yml` | Yes |
| `infra-terraform-apply-dev.yml` | Yes (dev only) |
| `infra-terraform-apply-test.yml` | Yes (test only) |
| `infra-terraform-apply-staging.yml` | Yes (staging only) |
| `infra-terraform-apply-prod.yml` | Yes (prod only) |
| `infra-terraform-dev-pipeline.yml` | Yes (plan-only, all envs) |
| `ci-bootstrap.yml` | Yes |
| `ci-teardown.yml` | Yes |
| `pr-terraform-plan.yml` | Yes (reads `envs/dev/terraform.tfvars`) |

## Operational notes

- **New BuildId = new backend key.** If you want to update an existing ephemeral
  cluster, reuse the same BuildId.
- Apply roles must allow access to the `envs/<env>/builds/*` prefix in S3.
- Consider lifecycle rules to expire old state objects to avoid bucket sprawl.

## References

- `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`
- `docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md`
- `docs/40-delivery/25_PR_TERRAFORM_PLAN.md`
- `docs/adrs/ADR-0040-platform-lifecycle-aware-state-keys.md`
