---
id: ADR-0077
title: 'ADR-0077: CI build/teardown log automation'
type: adr
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
  - ADR-0077
---

# ADR-0077: CI build/teardown log automation

Filename: `ADR-0077-platform-ci-build-teardown-log-automation.md`

- **Status:** Proposed
- **Date:** 2026-01-03
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** PR #129, docs/build-run-logs/README.md, docs/40-delivery/41_BUILD_RUN_LOG.md

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Build, bootstrap, and teardown logs provide a durable record of run outcomes,
flags, and timings. Capturing them manually is inconsistent and slows
post-run analysis. We need an automated, low-friction way to generate these
logs from CI runs.

## Decision

We will auto-generate build and teardown log entries from CI workflows using
simple templates and best-effort commits.

- Build logs are generated after bootstrap runs when a build ID is present.
- Teardown logs are generated after teardown runs.
- Log commits are best-effort and must not fail the workflow.

## Scope

Applies to:

- CI bootstrap and teardown workflows.
- Log templates under `docs/build-run-logs/`.

Does not apply to:

- Manual run entries (still allowed when needed).
- Non-CI executions.

## Consequences

### Positive

- Consistent log coverage for runs that matter.
- Faster triage and trend analysis over time.
- Reduced manual overhead.

### Tradeoffs / Risks

- Auto-commit can be blocked by branch protections; best-effort avoids failure.
- Parallel runs can race on sequence numbers; follow-up may be needed.

### Operational impact

- Operators can rely on CI-generated logs, but should still validate correctness
  when outcomes are critical.

## Alternatives considered

- Manual log creation only: rejected due to inconsistency and friction.
- Store logs as CI artifacts only: rejected because docs need durable links.

## Follow-ups

- Review sequence-number collision risks and adjust if they arise.
- Optionally move to a PR-based log commit if branch protections tighten.

## Notes

None.
