# Observability Tooling Decisions

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

## Pragmatic V1 observability baseline (RED + Golden Signals)

**Decision**: Use a metrics-first baseline for V1: RED at the ingress/gateway layer and
derived Golden Signals dashboards. Logs remain via Fluent Bit. Distributed traces are deferred
to V1.1.

**Implementation**: Deploy Prometheus, Grafana, and Alertmanager via the
`kube-prometheus-stack` Helm bundle (v45.7.1) in the `monitoring` namespace.
Persistence is enabled through PVCs backed by EBS/EFS storage add-ons.
Storage defaults and tradeoffs are documented in `docs/41_STORAGE_AND_PERSISTENCE.md`.

**Why**:

- V1 needs fast, reliable delivery and visibility without heavy instrumentation.
- RED gives a clean, low-friction signal for request health.
- Golden Signals provide a user-impact summary without requiring deep tracing.

**How It Works**:

- RED metrics from ingress/gateway (request rate, error rate, latency histograms).
- Minimal label contract: `service`, `env`, `version`, `team`, `build_id`.
- Golden Signals dashboard aggregates RED plus infra saturation (CPU/memory/node).
- CI/CD pipeline metrics remain separate and focus on plan/apply/teardown outcomes.

**Trade-offs**:

- Less per-request debugging detail until traces are added in V1.1.
- Service-level instrumentation varies until a standard SDK path is adopted.

**Next Steps**:

- Publish the RED label contract and dashboard pack.
- Add minimal alert rules for error rate, latency, and saturation.
- Create an ADR that records the V1 baseline and V1.1 deferrals.
