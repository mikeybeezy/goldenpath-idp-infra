---
id: CONTRIBUTING
title: Contributing
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

# Contributing

## Branch Strategy

Use short-lived branches and keep `main` deployable.

- `main`: protected, always deployable; only merged PRs.
- `feature/<topic>`: new work.
- `fix/<topic>`: urgent bugfixes.
- `chore/<topic>`: docs, tooling, cleanup.

Flow:

1. Branch from `main`.
2. Open a PR early for visibility.
3. Squash-merge into `main`.
4. Delete the branch after merge.

Examples:

- `feature/ci-bootstrap`
- `fix/teardown-timeout`
- `chore/docs-bootstrap`

## Branch Protection Checklist (GitHub)

Recommended settings for `main`:

- Require pull requests before merging.
- Require approvals: at least 1.
- Require status checks to pass.
- Require branches to be up to date before merging.
- Restrict who can push to `main`.
- Require linear history (no merge commits).
- Dismiss stale approvals when new commits are pushed.
- Enforce code owner reviews (if `CODEOWNERS` exists).

## Terraform lockfile policy

CI must not upgrade Terraform providers or modules. Use `terraform init` locally for upgrades and
commit the resulting `.terraform.lock.hcl` changes. If CI reports lockfile drift, update the
lockfile in a dedicated change and rerun the checks.
