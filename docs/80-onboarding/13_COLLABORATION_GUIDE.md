# Collaboration Guide

## Branch Strategy

Use short-lived branches and keep `main` deployable.

- `main`: protected, always deployable; only PRs from a gate branch.
- `development` / `dev-feature`: optional gate branches allowed to merge into `main`.
- `feature/<topic>`: new work.
- `fix/<topic>`: urgent bugfixes.
- `chore/<topic>`: docs, tooling, cleanup.

Flow:

1. Branch from the active gate branch (`development` or `dev-feature`).
2. Open a PR early for visibility into that gate branch.
3. Squash-merge into the gate branch after checks pass.
4. Promote via PR from the gate branch to `main`.
5. Delete the branch after merge.

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
