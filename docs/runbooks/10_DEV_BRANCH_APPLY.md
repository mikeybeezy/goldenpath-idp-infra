---
id: 10_DEV_BRANCH_APPLY
title: 'Runbook: Dev Branch Infra Apply'
type: runbook
category: runbooks
version: 1.0
owner: platform-team
status: active
dependencies:
- module:terraform
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- CI_WORKFLOWS
- ADR-0028
- ADR-0029
---

# Runbook: Dev Branch Infra Apply

Use this runbook to build an environment from the `development` branch.

## Workflow selection

Choose the workflow named `Apply - Infra Terraform Apply (dev branch)`
(defined in `.github/workflows/infra-terraform-apply-dev-branch.yml`).

## Run it like this

- Branch: `development`
- Inputs:
  - `confirm_apply` = `apply`
  - `confirm_dev_apply` = `true`
  - `build_id` = `dd-mm-yy-NN`

## Required plan (same commit)

This workflow requires a successful dev plan on the same commit from one of:

- `Plan - Infra Terraform Plan Pipeline`
  (`.github/workflows/infra-terraform-dev-pipeline.yml`)
- `Plan - Infra Terraform Checks`
  (`.github/workflows/infra-terraform.yml`)
- `Plan - PR Terraform Plan`
  (`.github/workflows/pr-terraform-plan.yml`)

## Notes

If you don’t see `Apply - Infra Terraform Apply (dev branch)` in the Actions
dropdown, that workflow isn’t on the default branch yet. Merge PR #125 first.
