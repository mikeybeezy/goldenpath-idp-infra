---
id: ADR-0074-platform-ops-workflow-branch-guard
title: 'ADR-0074: Ops workflow branch guard'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0074-platform-ops-workflow-branch-guard
  - CL-0029-ops-workflow-branch-guard
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0074: Ops workflow branch guard

- **Status:** Accepted
- **Date:** 2026-01-03
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** PR #126, docs/changelog/entries/CL-0029-ops-workflow-branch-guard.md

---

## Context

Ops workflows (bootstrap, teardown, orphan cleanup, managed LB cleanup) can be
invoked from any branch via workflow dispatch. That increases risk of running
operational jobs from stale or experimental branches.

## Decision

We will restrict ops workflows to run only from `main` and `development`.

## Scope

Applies to:

- `.github/workflows/ci-bootstrap.yml`
- `.github/workflows/ci-teardown.yml`
- `.github/workflows/ci-orphan-cleanup.yml`
- `.github/workflows/ci-managed-lb-cleanup.yml`

Does not apply to:

- Feature branch testing workflows (plan-only, linting, or documentation checks).

## Consequences

### Positive

- Reduces drift risk from running ops tasks on unreviewed branches.
- Keeps operational behavior tied to controlled branch history.

### Tradeoffs / Risks

- Adds a small gate for contributors running ops tasks from feature branches.

### Operational impact

- Operators must dispatch ops workflows from `main` or `development`.

## Alternatives considered

- Allow any branch: rejected due to drift and safety risks.
- Restrict to `main` only: rejected because `development` supports test builds.

## Follow-ups

- Document the branch guard in the PR gates runbook.

## Notes

None.
