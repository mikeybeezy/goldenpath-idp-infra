---
id: ADR-0069-platform-observability-baseline-golden-signals
title: 'ADR-0069: Observability baseline for golden signals in production'
type: adr
status: superseded
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
supported_until: 2028-01-04
version: '1.0'
superseded_by: ADR-0049
relates_to:
  - 05_OBSERVABILITY_DECISIONS
  - ADR-0049
  - ADR-0049-platform-pragmatic-observability-baseline
  - ADR-0069
breaking_change: false
---

# ADR-0069: Observability baseline for golden signals in production

- **Status:** Superseded (by ADR-0049-platform-pragmatic-observability-baseline.md)
- **Date:** 2025-12-23
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `docs/adrs/ADR-0049-platform-pragmatic-observability-baseline.md`

---

## Context

Production needs consistent visibility into the golden signals: latency, traffic, errors, and
saturation. The platform should provide an opinionated baseline that is production-grade but not
overkill, while still allowing teams to extend or integrate with managed services when needed.

---

## Decision

> We will adopt a minimal, opinionated observability baseline for production that captures the
> golden signals with low operational overhead.

Baseline components:

- Metrics: Prometheus + Grafana, with `kube-state-metrics` and `node_exporter`.
- Logs: Fluent Bit for collection, default backend Loki.
- Traces: OpenTelemetry SDKs in apps, collected via OTel Collector and stored in Tempo.
- Alerts: Prometheus Alertmanager with a small SLO-aligned ruleset.

---

## Scope

Applies to production environments and the platform-provided observability stack. Teams may add
service-specific dashboards, alerts, or exporters, but should not replace the baseline without a
documented exception.

---

## Consequences

### Positive

- Consistent golden-signal coverage with a small, predictable toolset.
- Lower operational overhead compared to full ELK or bespoke stacks.

### Tradeoffs / Risks

- Some advanced log analytics may require external tooling.
- Teams wanting managed observability must integrate with the baseline instead of replacing it.

### Operational impact

- Platform team maintains the baseline stack and default dashboards.
- Teams use the standard logging and tracing pipelines unless exceptions are approved.

---

## Alternatives considered

- Full ELK stack (rejected: higher operational overhead).
- Vendor-only managed observability (rejected: cost and lock-in).
- Metrics-only baseline (rejected: insufficient for golden signals).

---

## Follow-ups

- Align `docs/50-observability/05_OBSERVABILITY_DECISIONS.md` with this baseline.
- Publish a short golden-signal dashboard pack and alert rules.

---

## Notes

If the baseline proves too heavy or too light, revisit with usage and cost data.
