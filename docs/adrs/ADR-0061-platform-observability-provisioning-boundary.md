---
id: ADR-0061
title: 'ADR-0061: Observability provisioning boundary (Helm in-cluster, Terraform
  external)'
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
  - 01_GOVERNANCE
  - 05_OBSERVABILITY_DECISIONS
  - ADR-0052
  - ADR-0052-platform-kube-prometheus-stack-bundle
  - ADR-0061
---

# ADR-0061: Observability provisioning boundary (Helm in-cluster, Terraform external)

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Observability | Governance
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `docs/10-governance/01_GOVERNANCE.md`, `docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

We need a consistent rule for how observability is provisioned to avoid drift
between GitOps (Helm/Argo) and Terraform provider configurations. Today the
platform uses Helm for in-cluster observability, but some documentation still
implies dashboards and Grafana config are managed by Terraform. That creates
confusion and increases the risk of double-management.

---

## Decision

We will apply the following boundary:

- **Inside Kubernetes:** use Helm + GitOps (kube-prometheus-stack and ConfigMaps)
  for observability components and default dashboards/alerts.
- **Outside Kubernetes or SaaS:** use Terraform to manage cloud or external
  observability resources (Grafana Cloud, Datadog, PagerDuty, managed Prometheus).
- **Terraform remains the backbone** for cloud and cluster-adjacent
  infrastructure (VPC, EKS, IAM, DNS, KMS, state backends).

RED and Golden Signals define *what* we measure; Helm defines *how* we ship
in-cluster observability defaults.

---

## Scope

Applies to all platform-managed clusters and the V1 observability baseline.

Does not apply to:

- External/SaaS observability stacks.
- Cloud primitives managed by Terraform.

---

## Consequences

### Positive

- Single source of truth for in-cluster observability (Helm + GitOps).
- Reduced drift risk between Terraform and Helm provisioning paths.
- Cleaner upgrades via chart version pinning.

### Tradeoffs / Risks

- API-managed Grafana resources are not used by default.
- Teams must follow the ConfigMap/values workflow for dashboard changes.

### Operational impact

- Observability changes are made through Helm values and ConfigMaps.
- Terraform is reserved for external observability and infra primitives.

---

## Alternatives considered

- **Terraform for Grafana dashboards in-cluster:** rejected due to drift and
  dual management alongside Helm provisioning.
- **Mixed management per team:** rejected; increases inconsistency and support
  burden.

---

## Follow-ups

- Update observability docs to reflect this boundary.
- Keep chart versions pinned and tracked.

---

## Notes

If the platform shifts to managed observability, revisit this boundary and
introduce a new ADR for the change.
