---
id: ADR-0055
title: ADR-0055: Tempo as the standard tracing backend (V1.1)
type: adr
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
  supported_until: 2027-01-03
  breaking_change: false
relates_to: []
---

# ADR-0055: Tempo as the standard tracing backend (V1.1)

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Observability
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `docs/adrs/ADR-0049-platform-pragmatic-observability-baseline.md`, `docs/adrs/ADR-0054-platform-observability-exporters-otel-split.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

V1 focuses on metrics-first observability, with distributed tracing deferred to
V1.1. When tracing is enabled, we need a default backend that aligns with the
Grafana/Prometheus/Loki stack and integrates cleanly with OpenTelemetry.

---

## Decision

When distributed tracing is enabled (V1.1), **Tempo** will be the standard
tracing backend for OpenTelemetry traces.

Tempo will be deployed as a **separate GitOps application** (not part of
`kube-prometheus-stack`), following the same per-environment Argo CD app pattern
used for other observability components.

---

## Scope

Applies to platform-managed clusters when tracing is enabled. This does not
introduce tracing into V1; it defines the backend to use when V1.1 tracing
rollout begins.

---

## Consequences

### Positive

- Consistent, Grafana-aligned tracing backend.
- Simple integration with OpenTelemetry SDKs and collector pipelines.
- Clear separation from the metrics/logs baseline.

### Tradeoffs / Risks

- Additional deployment and storage footprint when tracing is enabled.
- Less advanced query/analytics than some commercial APMs.

### Operational impact

- Add a Tempo GitOps app and values per environment during V1.1 rollout.
- Define trace retention and storage targets aligned with platform defaults.
- Ensure Grafana is configured with the Tempo datasource.

---

## Alternatives considered

- **Jaeger:** rejected due to weaker long-term scale and tighter coupling to its
  own storage requirements.
- **Vendor-managed APM:** rejected to avoid lock-in and cost spikes during V1.

---

## Follow-ups

- Add the Tempo app to the GitOps app-of-apps when V1.1 tracing starts.
- Document OTel collector pipelines and sampling defaults.

---

## Notes

If tracing scope expands beyond platform-owned workloads, revisit multi-tenant
boundaries and retention tiers.
