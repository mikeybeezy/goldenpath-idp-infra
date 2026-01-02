# ADR-0066: Platform Dashboards as Code

Filename: `ADR-0066-platform-dashboards-as-code.md`

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Observability
- **Related:** `docs/50-observability/09_PLATFORM_DASHBOARD_CATALOG.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Observability dashboards are critical operational artifacts. However, managing them via the Grafana UI ("ClickOps") leads to:
1.  **Drift:** Dashboards customized in production are overwritten by deployments or lost if the pod restarts (without persistence).
2.  **Toil:** Re-creating standard dashboards for every new environment or cluster.
3.  **Lack of History:** No git history of who changed a threshold or query.

We need a way to treat dashboards as versioned artifacts that are automatically provisioned alongside the platform.

---

## Decision

We will manage all Platform and Default Application dashboards as **Kubernetes ConfigMaps**, deployed via Helm (`kube-prometheus-stack`).

> We will use the Grafana Sidecar pattern to automatically load dashboards from ConfigMaps labeled with `grafana_dashboard=1`.

This applies to:
*   **Cluster Overview:** Platform-level capacity and health.
*   **Platform Health:** GitOps and Addon status.
*   **Default App Dashboards:** The "Golden Signals" dashboard provided by the App Template.

It does **not** apply to:
*   Temporary ad-hoc exploration dashboards (users can still create these in the UI, but they are not guaranteed to persist across cluster rebuilds).

---

## Scope

*   **Applies to:** All dashboards managed by the Platform team (`goldenpath-idp-infra`) and the Golden Path templates.
*   **Does not apply to:** SaaS dashboards (e.g., Datadog, CloudWatch) which are managed via Terraform.

---

## Consequences

### Positive

- **Version Control:** Dashboards are reviewing in PRs, just like code.
- **GitOps:** ArgoCD ensures the "known good" dashboards are always present in every cluster.
- **Standardization:** Developers get a high-quality "Golden Signals" dashboard by default, enforcing consistent metrics across the org.

### Tradeoffs / Risks

- **Feedback Loop:** Editing JSON/YAML dashboards is slower than dragging panels in the UI. (Mitigation: Design in UI, export JSON, commit to git).
- **Complexity:** Reviewing massive JSON files in PRs is difficult.

### Operational impact

- **Operators:** Must export Dashboard JSON from Grafana and wrap it in a ConfigMap to "save" changes permanently.

---

## Alternatives considered

*   **Terraform Provider for Grafana:** feasible, but introduces a dependency on the Grafana API being up during Terraform runs. The ConfigMap/Sidecar approach is native to the cluster/Helm workflow.
*   **Grafana Persistent Volume:** Persists everything, but doesn't solve the "Standardization" or "Version Control" problem (it's still a mutable black box).

---

## Follow-ups

- Document the catalog of managed dashboards.
- Update the App Template to include the standard JSON model.

---

## Notes

None.
