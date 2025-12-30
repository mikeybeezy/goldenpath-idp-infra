# V1 Scope and Timeline (Backstage + Platform Capabilities)

This document defines the scoped V1 deliverables and what is deferred to V1.1.
It is a living guide for planning and execution.

---

## Purpose

- Align on what "usable V1" means.
- Keep scope focused and testable.
- Make deferrals explicit to avoid drift.

---

## V1 scope (lightweight but usable)

### Pipeline observability (OpenTelemetry metrics)

- Capture pipeline duration, success/fail, retries, and environment.
- Scope to plan/apply/teardown only.
- Export to a single backend (Grafana/Prometheus or a minimal OTel collector).

### ADR creation

- Provide an ADR template + helper workflow/script.
- Enforce index updates by convention (PR review).
- Store ADRs in `docs/adrs/`.

### Runbooks and playbooks ("fun books")

- Single format for all operational guidance.
- 5-8 critical runbooks (teardown, state issues, access, plan/apply, drift).
- Link runbooks to workflows and dashboards.

### Service discovery (basic)

- Backstage catalog entries with ownership and docs links.
- Manual registration only (no automation in V1).
- Required annotations for CI and dashboards.

### Golden signals dashboards

- One dashboard per core tool (CI, Argo CD, cluster).
- Standard panels: latency, error rate, throughput, saturation.
- Built from existing metrics where possible.

### Cluster health checks

- Post-apply checks: API reachable, nodes ready, system pods healthy, ingress OK.
- Report status in CI and link to runbooks.

---

## V1.1 deferrals (explicit)

- Automated service discovery from repos/cluster state.
- Full OpenTelemetry traces for per-step pipeline spans.
- Advanced health (SLOs, alerting, automated remediation).
- Expanded dashboards beyond the core toolset.

---

## V1 delivery checklist (usable) with timeframes

### Week 1: Foundations

- [ ] Backstage base deployment (Docker or K8s) is stable.
- [ ] Auth enabled (GitHub/OIDC) with basic RBAC roles.
- [ ] Initial catalog seeded (3-5 services).
- [ ] ADR template and index update instructions published.

### Week 2: Golden-path UX

- [ ] Scaffolder templates for plan/apply/teardown exist.
- [ ] Pipeline triggers wired from Backstage.
- [ ] Backstage entities link to CI runs and docs.
- [ ] Runbook format finalized; 2-3 runbooks published.

### Week 3: Observability + Health

- [ ] Pipeline metrics captured and surfaced in a dashboard.
- [ ] Golden signals dashboards for CI, Argo, and cluster exist.
- [ ] Cluster health checks automated post-apply.
- [ ] Runbooks expanded to 5-8 critical scenarios.

### Week 4: Hardening (time-boxed)

- [ ] Teardown reliability SLO defined (p95 < 20m, p99 < 45m; break-glass <5%).
- [ ] Run 5–10 teardown cycles and capture durations + break-glass usage.
- [ ] If SLO is missed, record a Known limitation and a V1.1 follow-up.
- [ ] RBAC tightened for apply/teardown actions.
- [ ] Catalog quality checks (ownership + annotations enforced).
- [ ] Docs polished and onboarding walkthrough published.
- [ ] V1 checklist reviewed and signed off.

---

## Acceptance criteria

- V1 features are usable without manual glue.
- PR plan path uses repo `tfvars`; manual workflows override via inputs.
- Health checks and dashboards are linked from the catalog.
- Operators can follow runbooks end-to-end without tribal knowledge.
- Teardown SLO is met or recorded as a Known limitation with a V1.1 follow-up.
