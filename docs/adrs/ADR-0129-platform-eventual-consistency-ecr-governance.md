---
id: ADR-0129
title: 'ADR-0129: Eventual Consistency for ECR Registry Governance'
type: adr
status: accepted
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle: active
version: 1.0
relates_to:
  - ADR-0092
  - ADR-0128
supported_until: 2028-01-08
breaking_change: false
---

# ADR-0129: Eventual Consistency for ECR Registry Governance

- **Status:** Accepted
- **Date:** 2026-01-08
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Governance | Architecture
- **Related:** [ECR Product Strategy](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0092-ecr-registry-product-strategy.md)

---

## Context

The Backstage catalog currently faces a "Truth" divergence regarding AWS ECR. While only one physical ECR registry exists, previous automation (Scaffolder runs) created separate `Kind: Resource` YAML files for every repository request. This "Sprawl" model leads to "Ghost Resources"—entities remaining in Backstage after their physical counterparts are deleted.

We needed a model that ensures the Backstage Catalog is a faithful mirror of the platform's governance logic (`ecr-catalog.yaml`) and the physical reality in AWS.

## Decision

We will adopt **Solution A: Mirror Script (Eventually Consistent)**.

> We will replace the distributed file sprawl with a single, script-generated `Kind: Resource` entity that mirrors the centralized governance catalog.

Backstage will no longer accept ad-hoc YAML files for ECR repositories. Instead, the `scripts/sync_ecr_catalog.py` utility will reconcile the state and generate a unified entity.

## Scope

This applies to all **ECR Registry and Repository** discovery within the Backstage Catalog. It does not apply to non-infrastructure entities like Components or APIs.

## Consequences

### Positive

- **Integrity**: Eliminates "Ghost" resources. If it's not in the governance logic, it's not in Backstage.
- **Centralization**: One single source of truth for all ECR assets.
- **Observability**: Direct alignment with `PLATFORM_HEALTH.md`.

### Tradeoffs / Risks

- **Eventual Consistency**: There is a delay (Time to Parity) between a request and its visibility in the catalog.
- **Pipeline Dependency**: Catalog accuracy depends on the successful run of the sync script.

### Operational impact

- **Timings**: Parity is achieved within **~3 minutes** (2-minute script cron + 1-minute Backstage refresh interval).
- **Automation**: The platform sync script must be scheduled (e.g., via GitHub Actions Cron or local Kubernetes CronJob).

## Alternatives considered

- **Option B: Hub-and-Spoke**: Rejected due to high manual maintenance of individual repository YAMLs.
- **Option C: Pruning Script**: Rejected due to the complexity of automated Git-back-pushes for cleanup.

## Follow-ups

- [ ] Update `scripts/sync_ecr_catalog.py` to generate the Backstage YAML.
- [ ] Configure `values-local.yaml` with optimized `refreshInterval` (60s).
- [ ] Schedule the sync script to run every 2 minutes.

---

## Notes

Assumes that a ~3-minute delay is acceptable for developers in exchange for 100% accurate catalog reporting.
