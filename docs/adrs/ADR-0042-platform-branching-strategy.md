---
id: ADR-0042-platform-branching-strategy
title: 'ADR-0042: Branching strategy (development → main)'
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
  - 23_NEW_JOINERS
  - 38_BRANCHING_STRATEGY
  - ADR-0042
---

# ADR-0042: Branching strategy (development → main)

Filename: `ADR-0042-platform-branching-strategy.md`

- **Status:** Proposed
- **Date:** 2025-12-29
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `docs/40-delivery/38_BRANCHING_STRATEGY.md`, `docs/80-onboarding/23_NEW_JOINERS.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

We need a simple, enforced branching model that keeps `main` stable and
prevents direct merges from ad hoc branches. Recent work involved multiple
short-lived branches, so we need a clear, documented path to avoid confusion.

---

## Decision

Adopt a two-branch promotion model:

- All work branches from `development`.
- All changes merge into `development` first.
- Only `development` can merge into `main`.

We will document the flow and add an optional CI guard to fail PRs that target
`main` from any branch other than `development`.

---

## Consequences

### Positive

- Predictable promotions into `main`.
- Clear expectations for contributors.
- Reduced risk of bypassing review or tests.

### Tradeoffs / Risks

- Hotfixes require an extra step through `development`.
- Teams must keep `development` healthy to avoid blocking promotion.

---

## Alternatives considered

- **Direct feature → main merges:** rejected due to stability and audit risk.
- **GitFlow with release branches:** rejected as too heavy for current scale.
