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

## Consequences

- Ephemeral teardown becomes deterministic: “delete by BuildId tag.”
- Persistent environments remain stable and safe.
- CI can safely spin up multiple ephemeral builds in parallel.

## Follow‑ups

- Add a short section in teardown docs about tag‑based cleanup.
- Add a bootstrap note about `Lifecycle` and `BuildId` inputs.
