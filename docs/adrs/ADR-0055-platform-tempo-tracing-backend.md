---
id: ADR-0055-platform-tempo-tracing-backend
title: 'ADR-0055: Tempo as the standard tracing backend (V1.1)'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 05_OBSERVABILITY_DECISIONS
  - 20_TOOLING_APPS_MATRIX
  - ADR-0049-platform-pragmatic-observability-baseline
  - ADR-0054-platform-observability-exporters-otel-split
  - ADR-0055-platform-tempo-tracing-backend
  - CL-0148
  - HELM_TEMPO
  - V1_04_CAPABILITY_MATRIX
  - audit-20260103
  - session-capture-2026-01-18-local-dev-hello-app
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---
# ADR-0055: Tempo as the standard tracing backend (V1.1)

- **Status:** Implementing
- **Date:** 2025-12-31
- **Updated:** 2026-01-18
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

- [x] Add Tempo Helm chart structure (`gitops/helm/tempo/`)
- [x] Create per-environment values files (dev/test/staging/prod)
- [ ] Add Argo CD Application manifests for each environment
- [ ] Configure Grafana datasource for Tempo
- [ ] Document OTel collector pipelines and sampling defaults
- [ ] Add otel-cli to CI workflow for build tracing

---

## Implementation Details (2026-01-18)

### Helm Chart Structure

```text
gitops/helm/tempo/
├── README.md
├── metadata.yaml
└── values/
    ├── dev.yaml      # SingleBinary, local storage, 3d retention
    ├── test.yaml     # SingleBinary, local storage, 7d retention
    ├── staging.yaml  # SingleBinary, S3 storage, 14d retention
    └── prod.yaml     # Distributed, S3 storage, 30d retention
```

### Deployment Modes

| Environment | Mode         | Storage | Retention | HA  |
| ----------- | ------------ | ------- | --------- | --- |
| dev         | SingleBinary | local   | 3 days    | No  |
| test        | SingleBinary | local   | 7 days    | No  |
| staging     | SingleBinary | S3      | 14 days   | No  |
| prod        | Distributed  | S3      | 30 days   | Yes |

### CI Tracing with otel-cli

Chosen over GitHub Actions native OpenTelemetry because:

| Aspect      | otel-cli            | GitHub Actions Native |
| ----------- | ------------------- | --------------------- |
| Portability | Works anywhere      | GitHub only           |
| Control     | Explicit spans      | Automatic             |
| Debugging   | Clear what's traced | Black box             |
| Maintenance | You manage          | GitHub manages        |

Example usage in CI:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://tempo.goldenpath.dev"
./otel-cli exec --name "docker-build" -- docker build -t myapp .
```

### Ingestion Endpoints

| Protocol  | Port  | Use Case                   |
| --------- | ----- | -------------------------- |
| OTLP gRPC | 4317  | High-volume apps, otel-cli |
| OTLP HTTP | 4318  | Simple HTTP push           |
| Jaeger    | 14268 | Legacy Jaeger clients      |
| Zipkin    | 9411  | Legacy Zipkin clients      |

---

## Notes

If tracing scope expands beyond platform-owned workloads, revisit multi-tenant
boundaries and retention tiers.
