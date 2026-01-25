---
id: ADR-0007-platform-environment-model
title: 'ADR-0007: Adopt an environment model that balances cost, iteration speed,
  and credible separation'
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
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_LIFECYCLE_POLICY
  - 01_adr_index
  - ADR-0006-platform-secrets-strategy
  - ADR-0007-platform-environment-model
  - ADR-0018-platform-container-registry-standard
  - ADR-0139
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0157-platform-multi-tenant-rds-architecture
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0007: Adopt an environment model that balances cost, iteration speed, and credible separation

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Operations | Cost
- **Related:** docs/10-governance/01_GOVERNANCE.md

## Context

We want a V1 platform that demonstrates:

- promotion through dev → test → stage → prod
- governance and separation (at least logically, ideally physically)
- deterministic rebuild and teardown

Constraints:

- clusters are ephemeral (created/destroyed during iteration)
- cost and time must be minimized until income is generated
- multi-cluster multiplies teardown/build time and operational overhead

## Decision

Adopt a phased environment strategy:

### V1 default (initial)

Use **one EKS cluster** with **four namespaces** representing dev/test/stage/prod
and strict GitOps boundaries (Argo Projects/RBAC, quotas, and environment
overlays).

### V1+ (when cost/time allows)

Optionally graduate to **two clusters**:

- Cluster A: dev + test
- Cluster B: stage + prod

Four clusters (dev/test/stage/prod) is deferred until there is stable income and
the platform loop is CI-ready.

## Scope

- Applies to: V1 platform delivery and demo/proof path.
- Out of scope: enterprise-grade multi-account, multi-region topology for V1.

## Consequences

### Positive

- Minimizes spend and build time while still demonstrating promotion flow.
- Keeps platform complexity low early, increasing likelihood of reaching V1-ready.
- Leaves a clear upgrade path to stronger isolation (2 clusters, then 4).

### Tradeoffs / Risks

- One cluster provides logical separation, not full physical separation.
- Blast radius is larger in single-cluster model (cluster outage affects all envs).
- Requires discipline: strong Argo/RBAC boundaries and clear “source of truth”

  to avoid cross-env drift.

### Operational impact

- Enforce per-environment boundaries:
  - namespaces per env
  - Argo Projects per env
  - resource quotas and limit ranges
  - env-specific values/overlays
- Define promotion as PR-based GitOps changes between env overlays.
- Update documentation to reflect current mode and upgrade path.

## Alternatives considered

- **Four clusters immediately**: rejected for V1 due to cost/time multiplication

  and increased failure surface.

- **Two clusters immediately**: viable, but deferred until the single-cluster

  loop is stable and CI-ready.

- **Single env only**: rejected; we need a credible promotion story.

## Follow-ups

- Implement Argo Projects + RBAC boundaries for dev/test/stage/prod namespaces.
- Add quotas/limits to prevent one env starving another.
- Document how to migrate from 1-cluster → 2-cluster model without repo redesign.
