# ADR-0007: Adopt an environment model that balances cost, iteration speed, and credible separation

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Operations | Cost
- **Related:** docs/01_GOVERNANCE.md, docs/02_GOVERNANCE_MODEL.md

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
