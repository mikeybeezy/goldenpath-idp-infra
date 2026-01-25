<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 16_INFRA_Build_ID_Strategy_Decision
title: Build ID Strategy Decision
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
  - 12_GITOPS_AND_CICD
  - 15_TEARDOWN_AND_CLEANUP
  - 17_BUILD_RUN_FLAGS
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ORPHAN_CLEANUP
category: delivery
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:aws_iam
  - module:aws_eks
breaking_change: false
---

# Build ID Strategy Decision

## Decision summary

We will support **ephemeral build IDs** for short‑lived environments to prevent
IAM role collisions and to make teardown deterministic. Persistent environments
(staging/prod) keep **stable names** and do not use a build suffix by default.

## Problem statement

We see collisions and leftovers when clusters are rebuilt:

- IAM role names are global per account, so reusing names causes failures.
- Orphaned resources are hard to find without a consistent tag strategy.
- Teardown becomes “hope and hunt” instead of “filter and delete.”

## Goals

- Make ephemeral builds easy to spin up and tear down.
- Avoid name collisions across repeated runs.
- Enable safe, tag‑based cleanup.
- Keep persistent environments stable and predictable.

## Options considered

### Option A: No suffix, no build ID

Pros:

- Simple names.
- No additional inputs.

Cons:

- Collisions are common.
- Cleanup is manual and error‑prone.
- Hard to automate in CI.

### Option B: Suffix for every cluster (persistent and ephemeral)

Pros:

- All resources are unique.
- Cleanup is easy via tags.

Cons:

- Persistent environments lose stable identities.
- External integrations must re‑point every rebuild.

### Option C: Dual mode (recommended)

Ephemeral runs use a build ID suffix. Persistent runs keep stable names.

Pros:

- Solves collisions for dev/ephemeral.
- Keeps staging/prod stable.
- Works with CI and manual flows.

Cons:

- Requires a clear toggle or lifecycle setting.

## Decision

Adopt **Option C: Dual mode**.

- Ephemeral cluster name: `gp-<env>-<YYYYMMDD>-<n>` or `gp-<env>-<gitsha>`
- Persistent cluster name: `gp-<env>` (stable)
- Tags applied to **all** resources:
  - `Environment`, `Project`, `Owner`, `Lifecycle`, `BuildId`
- IAM role names:
  - Ephemeral: `goldenpath-idp-<role>-<buildId>`
  - Persistent: `goldenpath-idp-<role>`

## Implementation notes (no resources created here)

- Use Terraform `default_tags` so every resource gets build tags.
- Use a single `name_prefix` input and pass it consistently.
- Require `BUILD_ID` (or generated suffix) for `Lifecycle=ephemeral`.
- Reject suffix changes for `Lifecycle=persistent`.
- Owner tagging is configured via `owner_team` and injected into `default_tags`.

  In CI, set it with `TF_VAR_owner_team`.

- For local runs, `build_id` should be set once in `envs/<env>/terraform.tfvars`.

  The Makefile reads from there by default; CI can override with `TF_VAR_build_id`.

## Inputs and examples

Ephemeral build (dev):

```bash

terraform -chdir=envs/dev plan \
  -var='cluster_lifecycle=ephemeral' \
  -var='build_id=20250115-01' \
  -var='owner_team=platform-team'

```text

Persistent build (staging/prod):

```bash

terraform -chdir=envs/staging plan \
  -var='cluster_lifecycle=persistent'

```text

## Recommended defaults

- Dev/manual: use a timestamp Build ID, run `plan` before `apply`.
- CI: use a git SHA (or hybrid) Build ID and run `apply` directly.

## Consequences

- Ephemeral teardown becomes deterministic: “delete by BuildId tag.”
- Persistent environments remain stable and safe.
- CI can safely spin up multiple ephemeral builds in parallel.

## How this prevents collisions and leftovers

- **Unique IAM role names in ephemeral runs**: role names get a `-<build_id>`

  suffix, so new runs never collide with existing roles.

- **Stable names in persistent runs**: staging/prod keep fixed names, so updates

  don’t churn resources.

- **Tags on every resource**: `Lifecycle` + `BuildId` make cleanup a targeted

  “find and delete” instead of a manual hunt.

## Follow‑ups

- Add a short section in teardown docs about tag‑based cleanup.
- Add a bootstrap note about `Lifecycle` and `BuildId` inputs.
