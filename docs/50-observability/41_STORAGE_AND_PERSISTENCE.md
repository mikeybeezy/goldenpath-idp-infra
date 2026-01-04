---
id: 41_STORAGE_AND_PERSISTENCE
title: Storage and Persistence (Living)
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Storage and Persistence (Living)

Doc contract:
- Purpose: Define storage defaults, persistence requirements, and tradeoffs.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md, docs/adrs/ADR-0053-platform-storage-lifecycle-separation.md

This document captures the ongoing storage implementation for GoldenPath. It
expands on the storage principle in `docs/10-governance/01_GOVERNANCE.md` and the decision in
`docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md`.

## Purpose

- Keep monitoring data persistent across restarts and rollouts.
- Provide clear storage defaults that work out of the box.
- Document tradeoffs for storage class and sizing decisions.

## Defaults (V1)

- Storage add-ons are **enabled by default** (`enable_storage_addons=true`).
- Storage add-ons include **EBS CSI**, **EFS CSI**, and the **snapshot controller**.
- Monitoring data is persisted via PVCs for Prometheus, Alertmanager, and Grafana.
- Storage uses the **cluster default StorageClass** (no hard-coded class name).

## StorageClass choice: default vs gp3

**Decision:** Use the cluster default StorageClass.

Why:
- Aligns with cluster-level policy and avoids hard-coding class names.
- Works across clusters that may not expose `gp3` or use a custom default.
- Centralizes policy control in cluster provisioning rather than chart values.

Tradeoffs:
- If the default is `gp2`, performance scales with size and can be lower for
  small volumes.
- `gp3` offers predictable baseline IOPS and lower cost per GiB, but hard-coding
  `gp3` couples workloads to a class that might not exist everywhere.

If the cluster default is updated to `gp3`, monitoring automatically benefits
without values changes.

## Storage sizing (baseline)

Sizing is tied to retention and scrape volume. Start here and adjust based on
real usage and retention requirements.

| Environment | Prometheus | Alertmanager | Grafana | Retention |
| --- | --- | --- | --- | --- |
| dev | 20Gi | 5Gi | 10Gi | 7d |
| test | 20Gi | 5Gi | 10Gi | 7d |
| staging | 50Gi | 10Gi | 10Gi | 15d |
| prod | 100Gi | 20Gi | 20Gi | 30d |

Tradeoffs:
- Smaller volumes cost less and compact faster, but reduce retention and headroom.
- Larger volumes extend retention and absorb spikes, but cost more and recover slower.

## Failure modes to watch

- **PVC pending:** storage add-ons not Active or StorageClass misconfigured.
- **Slow teardown:** volumes detach slowly; finalizers can delay namespace delete.
- **Retain policies:** orphaned volumes remain after teardown if reclaim policy is `Retain`.

## References

- `docs/10-governance/01_GOVERNANCE.md`
- `docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md`
