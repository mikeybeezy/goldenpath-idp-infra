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
