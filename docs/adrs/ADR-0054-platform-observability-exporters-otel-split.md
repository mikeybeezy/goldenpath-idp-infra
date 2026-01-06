---
id: ADR-0054
title: 'ADR-0054: Exporter vs OpenTelemetry split for platform observability'
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
  - 05_OBSERVABILITY_DECISIONS
  - ADR-0049
  - ADR-0049-platform-pragmatic-observability-baseline
  - ADR-0052
  - ADR-0052-platform-kube-prometheus-stack-bundle
  - ADR-0054
---

# ADR-0054: Exporter vs OpenTelemetry split for platform observability

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Observability
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `docs/adrs/ADR-0049-platform-pragmatic-observability-baseline.md`, `docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

We need a clear and minimal observability baseline that separates infrastructure
metrics from application telemetry. There has been ambiguity about whether
OpenTelemetry replaces Prometheus exporters. The platform needs a consistent
default that is easy to operate while still enabling richer app signals.

---

## Decision

We will keep Prometheus exporters as the baseline for infrastructure metrics and
use OpenTelemetry for application telemetry breadth.

Specifically:

- **Infra metrics**: `node-exporter` (node OS) and `kube-state-metrics` (Kubernetes
  object state) remain required.
- **Container metrics**: cAdvisor is scraped via the kubelet (`/metrics/cadvisor`);
  no separate cAdvisor deployment is installed.
- **App telemetry**: OpenTelemetry SDKs/Collector are the standard for app
  metrics, traces, and logs. This complements, not replaces, infra exporters.

---

## Scope

Applies to all platform-managed clusters and the platform-provided observability
stack for V1. This does not block teams from adding service-specific exporters,
but they must not remove the baseline exporters without an approved exception.

---

## Consequences

### Positive

- Clear separation between infra baseline and app instrumentation.
- Stable infra dashboards independent of app telemetry maturity.
- Reduced risk of losing node/kube visibility if app instrumentation lags.

### Tradeoffs / Risks

- Two telemetry paths increase conceptual and operational complexity.
- Some metric duplication may occur between exporters and OTel SDKs.

### Operational impact

- Ensure kubelet scrape config for `/metrics/cadvisor` stays enabled.
- Maintain ServiceMonitors for `node-exporter` and `kube-state-metrics`.
- Define a minimal OTel collector deployment when app telemetry is enabled.

---

## Alternatives considered

- **All-in OpenTelemetry (no exporters):** rejected; OTel does not replace
  kube-state-metrics or node-exporter for infra baseline.
- **Metrics-only baseline:** rejected; it blocks trace/log adoption and limits
  app-level visibility.

---

## Follow-ups

- Keep `docs/50-observability/05_OBSERVABILITY_DECISIONS.md` aligned with this split.
- Document the OTel rollout path (collector, exporters, destinations).

---

## Notes

If V1.1 expands tracing, revisit the OTel collector footprint and retention
policy.
