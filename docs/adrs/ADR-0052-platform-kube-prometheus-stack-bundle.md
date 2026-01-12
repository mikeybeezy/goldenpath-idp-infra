---
id: ADR-0052-platform-kube-prometheus-stack-bundle
title: 'ADR-0052: Use kube-prometheus-stack as the V1 monitoring bundle'
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
  - 05_OBSERVABILITY_DECISIONS
  - 06_IDENTITY_AND_ACCESS
  - 41_STORAGE_AND_PERSISTENCE
  - ADR-0052
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

# ADR-0052: Use kube-prometheus-stack as the V1 monitoring bundle

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Observability
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `gitops/helm/kube-prometheus-stack`, `docs/60-security/06_IDENTITY_AND_ACCESS.md`, `docs/50-observability/41_STORAGE_AND_PERSISTENCE.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

V1 needs a deterministic, productized monitoring baseline. Today Prometheus,
Grafana, and Alertmanager are installed as separate Helm charts, which increases
config drift, operational overhead, and coordination effort across environments.

We also require persistent monitoring data for platform visibility; ephemeral
storage is not acceptable for Prometheus retention.

---

## Decision

Adopt the `kube-prometheus-stack` Helm bundle (v45.7.1) as the single
deployment unit for Prometheus, Grafana, and Alertmanager.

Persist monitoring data by default using PVCs backed by EBS/EFS storage
add-ons. Storage add-ons are required for the monitoring baseline.

---

## Scope

Applies to platform monitoring in all environments. This does not change
Fluent Bit or Loki deployments.

---

## Consequences

### Positive

- Single bundle reduces drift across Prometheus/Grafana/Alertmanager.
- Environment-specific values are centralized and easier to audit.
- Persistence is explicit and aligned with the platform’s monitoring contract.

### Tradeoffs / Risks

- Upgrades are coupled across components.
- Bundle values are more complex than standalone charts.
- PVC requirements increase reliance on storage add-ons.

### Operational impact

- Argo CD apps change from three components to one bundle.
- Storage add-ons must be active before monitoring can reconcile.
- Grafana access remains the same, but namespace defaults to `monitoring`.

---

## Alternatives considered

- Keep separate charts: rejected due to drift and operator overhead.
- Managed monitoring backend: deferred for V1 due to cost and setup time.

---

## Follow-ups

- Add Argo CD applications for kube-prometheus-stack.
- Remove standalone Prometheus/Grafana/Alertmanager apps.
- Update monitoring docs and bootstrap checks.

---

## Notes

If persistence requirements change or a managed backend becomes the default,
this ADR should be superseded.
