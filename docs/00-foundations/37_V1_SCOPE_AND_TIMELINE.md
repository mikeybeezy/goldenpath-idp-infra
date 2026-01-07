---
id: 37_V1_SCOPE_AND_TIMELINE
title: V1 Scope and Timeline (Backstage + Platform Capabilities)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - ROADMAP
  - IDP_PRODUCT_FEATURES
  - 00_DESIGN_PHILOSOPHY
  - READINESS_CHECKLIST
  - V1_04_CAPABILITY_MATRIX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# V1 Scope and Timeline (Backstage + Platform Capabilities)

Doc contract:

- Purpose: Define V1 scope, timeline, and explicit deferrals.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/production-readiness-gates/ROADMAP.md, docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md

This document defines the scoped V1 deliverables and what is deferred to V1.1.
It is a living guide for planning and execution.

---

## Purpose

- Align on what "usable V1" means.
- Keep scope focused and testable.
- Make deferrals explicit to avoid drift.

## V1 Scope & VQ Alignment

This V1 scope is aligned with **Phase 1 (Stabilize the Core)** of our [**VQ Strategy**](../production-readiness-gates/ROADMAP.md). Our primary success metric for V1 is: *"I can step away and nothing degrades."*

Every V1 feature is classified as **🔴 HV / HQ** (High Value / High Quality). We move slowly here to ensure trust, safety, and determinism.

---

## V1 scope (The Boring Core)

### CI/CD observability (metrics only)

- Capture pipeline duration, success/fail, retries, and environment.
- Scope to plan/apply/teardown only.
- Export to a single backend (Grafana/Prometheus or a minimal OTel collector).

### Observability baseline (RED + Golden Signals)

- RED metrics at ingress/gateway: request rate, error rate, latency histograms.
- Minimal label contract: service, env, version, team, build_id.
- Golden Signals dashboards derived from RED + infra saturation.
- Minimal alerts: error rate, latency, saturation.

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

### App scaffolding + repo creation (Golden Path)

- Backstage scaffolder creates a new app repo from a golden-path template.
- Repo includes CI, GitOps, and docs scaffolding by default.
- Catalog registration remains manual in V1.

### Cluster health checks

- Post-apply checks: API reachable, nodes ready, system pods healthy, ingress OK.
- Report status in CI and link to runbooks.

---

## V1.1 deferrals (explicit)

- Automated service discovery from repos/cluster state.
- Full OpenTelemetry traces (pipeline + service spans).
- Advanced health (SLOs, error budgets, automated remediation).
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
- [ ] Scaffolder can create a new app repo from a golden-path template.
- [ ] Pipeline triggers wired from Backstage.
- [ ] Backstage entities link to CI runs and docs.
- [ ] Runbook format finalized; 2-3 runbooks published.

### Week 3: Observability + Health

- [ ] Pipeline metrics captured and surfaced in a dashboard.
- [ ] RED + Golden Signals dashboards published with minimal alerts.
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
