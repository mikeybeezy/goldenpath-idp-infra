---
id: ADR-0049-platform-pragmatic-observability-baseline
title: 'ADR-0049: Pragmatic observability baseline for V1 (RED + Golden Signals)'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 05_OBSERVABILITY_DECISIONS
  - ADR-0049
  - ADR-0069
  - ADR-0069-platform-observability-baseline-golden-signals
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0049: Pragmatic observability baseline for V1 (RED + Golden Signals)

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Observability
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `docs/adrs/ADR-0069-platform-observability-baseline-golden-signals.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

V1 priorities emphasize reliable deployment and teardown with low operational
overhead. Full distributed tracing and deep SLO mechanics are valuable, but
they increase implementation complexity and slow delivery of a stable baseline.
The platform still needs a consistent, testable observability standard that
supports rapid diagnosis and user-visible health.

---

## Decision

We will adopt a **metrics-first baseline** for V1 that combines:

- **RED metrics** at the ingress/gateway layer (rate, errors, duration).
- **Golden Signals dashboards** derived from RED + core infrastructure metrics.
- **Minimal alerting** focused on availability and saturation.

Full distributed tracing and advanced SLO/error-budget automation are deferred
to V1.1.

---

## Scope

Applies to V1 platform environments and platform-owned workloads. This does not
block teams from adding service-specific dashboards or traces, but the platform
baseline only guarantees RED + Golden Signals metrics.

---

## Consequences

### Positive

- Fast, consistent baseline with low operational burden.
- Clear diagnostics for ingress/service health without heavy instrumentation.
- Aligns V1 priorities with deployment reliability and visibility.

### Tradeoffs / Risks

- Less per-request depth until tracing is added in V1.1.
- Some root-cause analysis may require manual, service-specific instrumentation.

### Operational impact

- Publish standard RED dashboards and Golden Signals views.
- Maintain a minimal alerting ruleset for availability and saturation.

---

## Alternatives considered

- **Full tracing + SLO automation in V1:** rejected due to complexity and time.
- **Metrics-only without Golden Signals:** rejected as insufficient for health.
- **Vendor-managed APM baseline:** rejected to avoid lock-in and cost spikes.

---

## Follow-ups

- Define a RED label contract for standard metrics.
- Publish dashboards and minimal alert rules.
- Plan V1.1 trace rollout with clear entry criteria.

---

## Notes

Revisit after V1 validation to confirm whether tracing and SLO automation should
move into V1.1 or later.
