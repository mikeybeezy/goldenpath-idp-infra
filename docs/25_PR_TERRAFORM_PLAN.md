# PR Terraform Plan (Living Document)

This document describes the PR plan workflow and how it behaves.

## Current behavior

- Trigger: pull requests that touch Terraform files.
- Scope: `envs/dev` only.
- Backend: remote S3 + DynamoDB (read-only OIDC role).
- State key: resolved from `envs/dev/terraform.tfvars`:
  - `cluster_lifecycle=persistent` → `envs/dev/terraform.tfstate`
  - `cluster_lifecycle=ephemeral` → `envs/dev/builds/<build_id>/terraform.tfstate`
- Output: posted as a PR comment.

## Why this exists

- Provide fast, visible infrastructure feedback without Atlantis.
- Keep apply manual and controlled.

## Limitations

- Plan output is truncated if too large.
- Plan uses `-refresh=false` so it reflects state, not live AWS drift.

## Note

If you want a fresh-slate plan, update `build_id` in `envs/dev/terraform.tfvars`
and keep `cluster_lifecycle=ephemeral`. The plan will then use a new state key
and show a full create from scratch.

If you want the PR plan to reflect incremental changes against a long-lived
environment, keep `cluster_lifecycle=persistent` so the plan uses the stable
state key.

## Two ways to start a new build

1) **Ad-hoc CI only (no PR)**: run the workflow and pass a new `build_id` input.
2) **PR-driven**: update `build_id` in `envs/dev/terraform.tfvars` so the PR plan
   uses the new state key.

## Change process

- Update the ADR if the workflow changes materially.
- Keep this doc aligned with the workflow file.
