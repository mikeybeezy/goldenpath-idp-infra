---
id: 38_BRANCHING_STRATEGY
title: Branching Strategy (GoldenPath IDP)
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

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
- `development`: integration branch, only source allowed to merge into `main`.
- short-lived branches: feature/fix/docs/chore branches off `development`.

---

## PR flow

1) Create a branch from `development`.
2) Open a PR into `development`.
3) Merge after checks pass.
4) Promote via a single PR from `development` to `main`.

Direct merges from feature branches to `main` are not allowed.

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
unless the source branch is `development`. This makes the policy enforceable
in repos without enterprise-level branch protections.

---

## Exceptions

None. Hotfixes still flow through `development` first.
