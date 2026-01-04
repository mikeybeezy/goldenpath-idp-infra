---
id: 13_COLLABORATION_GUIDE
title: Collaboration Guide
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
relates_to:
- 38_BRANCHING_STRATEGY
- SHARED_RESPONSIBILITY
------

# Collaboration Guide

## Branch Strategy

Use short-lived branches and keep `main` deployable.

- `main`: protected, always deployable; only merged PRs.
- `development`: integration branch, only source allowed to merge into `main`.
- `feature/<topic>`: new work.
- `fix/<topic>`: urgent bugfixes.
- `chore/<topic>`: docs, tooling, cleanup.

Flow:

1. Branch from `development`.
2. Open a PR early for visibility into `development`.
3. Merge after checks pass.
4. Promote via a PR from `development` to `main`.
5. Delete the branch after merge.

Examples:

- `feature/ci-bootstrap`
- `fix/teardown-timeout`
- `chore/docs-bootstrap`

Reference: `docs/40-delivery/38_BRANCHING_STRATEGY.md` is the source of truth.

## Roles & Responsibilities (Summary)

- Platform team owns infra lifecycle, CI/CD rails, GitOps controllers, baseline
  security/observability, and governance artifacts (ADRs/changelog rules).
- App teams own application code, runtime behavior, and service-level choices
  within platform contracts (tags, CI inputs, promotion flow).
- AI agents are contributors; humans approve scope, merges, and any high-risk
  actions (apply/destroy/IAM).
- Shared responsibility is tracked in `docs/60-security/SHARED_RESPONSIBILITY.md`
  and must be kept current before production use.
- If onboarding guidance conflicts with governance/contract docs, defer to the
  contract doc and open a fix.

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
