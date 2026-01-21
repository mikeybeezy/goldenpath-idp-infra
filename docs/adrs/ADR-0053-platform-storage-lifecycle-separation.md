---
id: ADR-0053-platform-storage-lifecycle-separation
title: 'ADR-0053: Separate storage lifecycle from bootstrap and teardown'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 15_TEARDOWN_AND_CLEANUP
  - 41_STORAGE_AND_PERSISTENCE
  - ADR-0053-platform-storage-lifecycle-separation
  - ADR-0157-platform-multi-tenant-rds-architecture
  - ADR-0158-platform-standalone-rds-bounded-context
  - CL-0018-kube-prometheus-stack-defaults
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0053: Separate storage lifecycle from bootstrap and teardown

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Operations | Governance
- **Related:** `docs/50-observability/41_STORAGE_AND_PERSISTENCE.md`, `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`, `bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh`, `.github/workflows/ci-bootstrap.yml`, `.github/workflows/ci-teardown.yml`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Monitoring components require PVCs to persist data. If storage add-ons are not
ready at bootstrap, kube-prometheus-stack pods stay Pending and monitoring is
not available. Teardown can be delayed by PV/PVC finalizers and cloud volume
detach time. We need a deterministic workflow that preserves monitoring
persistence without making teardown fragile.

---

## Decision

We will **enable storage add-ons during bootstrap** and treat **storage cleanup
as a separate, explicit workflow** from teardown.

Bootstrap must validate storage add-ons when persistence is required. Teardown
does not implicitly delete or detach volumes beyond normal Kubernetes cleanup.
Operators run a storage cleanup workflow when required (for retain policies or
explicit cleanup audits).

---

## Scope

Applies to platform monitoring storage (Prometheus, Alertmanager, Grafana) and
cluster storage add-ons in all environments.

Does not alter application-level PVC behavior outside the platform baseline.

---

## Consequences

### Positive

- Monitoring pods can bind PVCs immediately during bootstrap.
- Storage readiness is validated early and fails fast when missing.
- Teardown avoids hidden destructive storage behavior.

### Tradeoffs / Risks

- Storage cleanup becomes an explicit step and requires operator action.
- Persistent volumes may outlive cluster teardown when reclaim policies retain.
- Storage add-ons increase bootstrap dependencies.

### Operational impact

- Bootstrap requires storage add-ons to be Active.
- Add a storage cleanup workflow/runbook for PVC/PV and cloud volume cleanup.
- Document reclaim policy expectations for monitoring PVCs.

---

## Alternatives considered

- Provision storage after bootstrap: rejected because monitoring PVCs would not bind.
- Auto-delete storage during teardown: rejected due to risk of accidental data loss.

---

## Follow-ups

- Create a storage cleanup workflow and runbook.
- Document storage reclaim policy and cleanup checklist.

---

## Notes

If storage persistence requirements change, supersede this ADR with updated
cleanup guarantees.
