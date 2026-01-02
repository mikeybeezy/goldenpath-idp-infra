# Branching Strategy (GoldenPath IDP)

Doc contract:
- Purpose: Define branch roles, promotion flow, and naming.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md

This document defines the branching and promotion flow for the repo.
It keeps main stable and ensures all changes are reviewed.

---

## Goals

- Keep `main` stable and releasable.
- Ensure every change is reviewed and tested before promotion.
- Reduce branching confusion for new contributors.

---

## Branch roles

- `main`: production-ready baseline, protected.
- `development`: primary integration branch, allowed to merge into `main`.
- `dev-feature`: optional integration branch, allowed to merge into `main` when enabled.
- short-lived branches: feature/fix/docs/chore branches off the active gate branch.

---

## PR flow

1) Create a branch from the active gate branch (`development` or `dev-feature`).
2) Open a PR into that gate branch.
3) Merge after checks pass.
4) Promote via a single PR from the gate branch to `main`.

Direct merges from feature branches to `main` are not allowed.
Only `development` or `dev-feature` may target `main`.

---

## Branch naming

- `feature/<short-name>`
- `fix/<short-name>`
- `docs/<short-name>`
- `chore/<short-name>`

---

## Branch protection guidance (GitHub)

Recommended settings for `main`:

- Require pull request reviews (at least 1).
- Require status checks to pass.
- Require branch to be up to date before merging.
- Disallow direct pushes.

Recommended settings for `development`:

- Require status checks to pass (optional but preferred).
- Disallow force pushes.

---

## CI guard (optional enforcement)

We recommend a lightweight CI guard that fails any PR targeting `main`
unless the source branch is `development` or `dev-feature`. This makes the
policy enforceable in repos without enterprise-level branch protections.

---

## Exceptions

None. Hotfixes still flow through the gate branch first.
