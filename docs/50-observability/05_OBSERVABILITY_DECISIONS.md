# Observability Tooling Decisions

Doc contract:
- Purpose: Record current observability tooling choices and defaults.
- Owner: platform
- Status: reference
- Review cadence: as needed
- Related: docs/50-observability/41_STORAGE_AND_PERSISTENCE.md, docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md, docs/adrs/ADR-0054-platform-observability-exporters-otel-split.md, docs/adrs/ADR-0056-platform-loki-deployment-mode.md, docs/adrs/ADR-0055-platform-tempo-tracing-backend.md

## Fluent Bit for Log Shipping

**Decision**: Use Fluent Bit as the platform-wide log forwarder, configured by the platform team.

**Why**:

- Lightweight DaemonSet that supports multiple outputs (Loki, CloudWatch, Datadog, Splunk, etc.).
- Keeps the "golden path" (Loki) in place while allowing teams to ship logs to managed services without installing their own agents.
- Centralized management ensures consistent filters, metadata labels, and resource limits.

**How It Works**:

- Default backend: Loki (or CloudWatch) managed by the platform.
- Additional outputs can be enabled per namespace/team via Fluent Bit configuration snippets (e.g., Datadog HTTP output).
- Teams request additional destinations through the platform backlog; platform validates security/compliance implications before enabling.

**Trade-offs**:

- Platform team must manage config fan-out carefully to avoid noisy logging or credential sprawl.
- Teams still own downstream log analysis tooling (Datadog dashboards, alerts, etc.).

**Next Steps**:

- Finalize Fluent Bit values in `gitops/helm/fluent-bit/values/<env>.yaml` with modular output sections.
- Document the request process for enabling new outputs (e.g., Datadog API key storage, secret names).

---

## Loki deployment mode (V1 default)

**Decision**: Start Loki in **Single Binary** mode for V1, and move to **Simple Scalable**
only when scale/retention/HA requirements justify it.

Loki is deployed in the `monitoring` namespace.

**Why**:

- Single Binary is simpler to operate and cheaper for early usage.
- Simple Scalable adds HA and better query/write scaling but requires object storage and more ops overhead.

**Triggers to switch**:

- Sustained ingestion/query pressure (slow queries, frequent OOMs).
- Retention beyond local PV limits.
- HA expectations for logs in production.

**Related ADR**: `docs/adrs/ADR-0056-platform-loki-deployment-mode.md`.

---

## Pragmatic V1 observability baseline (RED + Golden Signals)

**Decision**: Use a metrics-first baseline for V1: RED at the ingress/gateway layer and
derived Golden Signals dashboards. Logs remain via Fluent Bit. Distributed traces are deferred
to V1.1.

**Implementation**: Deploy Prometheus, Grafana, and Alertmanager via the
`kube-prometheus-stack` Helm bundle (v45.7.1) in the `monitoring` namespace.
Persistence is enabled by default; storage add-ons, sizing, and tradeoffs are
documented in `docs/50-observability/41_STORAGE_AND_PERSISTENCE.md`.

**Exporter + OpenTelemetry split (decision note)**:

- **Infra metrics** stay on Prometheus exporters: `node-exporter` (node OS) and
  `kube-state-metrics` (Kubernetes object state).
- **cAdvisor metrics** are scraped from the kubelet (`/metrics/cadvisor`); no separate
  cAdvisor deployment is required.
- **App telemetry** uses OpenTelemetry SDKs/Collector for broader signals (metrics, traces,
  logs) and does **not** replace the infra exporters.

**Tracing backend (decision note)**:

- **Tempo** is the default backend when distributed tracing is enabled (V1.1).
- Tempo is deployed separately from `kube-prometheus-stack` via GitOps apps.

**Why**:

- V1 needs fast, reliable delivery and visibility without heavy instrumentation.
- RED gives a clean, low-friction signal for request health.
- Golden Signals provide a user-impact summary without requiring deep tracing.

**How It Works**:

- RED metrics from ingress/gateway (request rate, error rate, latency histograms).
- Minimal label contract: `service`, `env`, `version`, `team`, `build_id`.
- Golden Signals dashboard aggregates RED plus infra saturation (CPU/memory/node).
- CI/CD pipeline metrics remain separate and focus on plan/apply/teardown outcomes.

---

## RED label contract (V1)

These labels are required on RED metrics emitted at the ingress/gateway layer.
They provide consistent grouping for dashboards and alerts while keeping
cardinality controlled.

Required labels:

- `service`: logical service name (matches catalog entity name).
- `env`: environment (dev/test/staging/prod).
- `version`: deploy version (image tag or git SHA).
- `team`: owning team/group.
- `build_id`: CI build identifier for the deployment.

Guidance:

- Use low‑cardinality values; avoid request IDs or user IDs.
- If a value is not available, use `unknown` rather than dropping the label.
- Dashboards and alerts should group by `service` and `env`, and use `version`
  and `build_id` for rollbacks and diff views.

Example:

```
service=payments-api env=dev version=2025.12.31-1 team=platform build_id=31-12-25-02
```

**Trade-offs**:

- Less per-request debugging detail until traces are added in V1.1.
- Service-level instrumentation varies until a standard SDK path is adopted.

---

## Observability provisioning boundary (V1)

**Decision**: In-cluster observability is provisioned via Helm + GitOps.
Terraform is reserved for external/SaaS observability resources.

**Source of truth**:

- **In-cluster:** Helm chart values and ConfigMaps/Secrets (kube-prometheus-stack).
- **External/SaaS:** Terraform providers (Grafana Cloud, Datadog, PagerDuty).

**Why**:

- Avoids drift between Terraform and Helm for the same Grafana instance.
- Keeps upgrades safe and repeatable with chart version pinning.
- Keeps cloud primitives and SaaS integrations in Terraform where state matters.

**Operational rule**:

- Do not manage the same dashboards in both Helm and Terraform.
- If Grafana is in-cluster, use ConfigMaps and Helm values for dashboards/alerts.

**Next Steps**:

- Implement the RED label contract in dashboards and alert rules.
- Add minimal alert rules for error rate, latency, and saturation.
- Keep ADRs aligned: `ADR-0049-platform-pragmatic-observability-baseline.md`,
  `ADR-0055-platform-tempo-tracing-backend.md`, and
  `ADR-0061-platform-observability-provisioning-boundary.md`.
