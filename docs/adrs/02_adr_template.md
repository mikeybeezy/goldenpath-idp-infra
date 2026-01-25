---
id: 02_adr_template
title: 'ADR-XXXX: Template for Architecture Decision Records'
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
  - 01_GOVERNANCE
  - ADR-0084-platform-enhanced-metadata-schema
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: 1.0
breaking_change: false
---

# ADR-XXXX: Concise decision title

Filename: `ADR-XXXX-(platform|app)-short-title.md`

- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Date:** YYYY-MM-DD
- **Owners:** `team / role`
- **Domain:** Platform | Application
- **Decision type:** Architecture | Security | Operations | Governance | Observability
- **Related:** `links to docs, PRs, tickets`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

What problem are we solving?

What constraints matter (cost, time, risk, org, platform limits)?

Why does this decision exist *now*?

Keep this factual and brief.

---

## Decision

State the decision clearly and unambiguously.

> We will …

Avoid hedging language.

---

## Scope

What this decision **applies to**, and what it explicitly **does not** apply to.

---

## Consequences

### Positive

- What improves because of this decision?

### Tradeoffs / Risks

- What do we give up?
- What new complexity or constraints are introduced?

### Operational impact

- What operators/teams must do differently?
- Any runbooks, monitoring, or access changes required?

---

## Alternatives considered

Briefly list realistic alternatives and why they were not chosen.

---

## Follow-ups

Concrete actions needed to fully implement or enforce this decision.

---

## Notes

Assumptions, future reconsideration triggers, or known unknowns.
