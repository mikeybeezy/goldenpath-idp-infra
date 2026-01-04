---
id: 02_PLATFORM_BOUNDARIES
title: Platform Boundaries & Contract
type: contract
owner: platform-team
status: active
risk_profile:
  production_impact: high
  security_risk: none
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:

- 01_GOVERNANCE
- 21_CI_ENVIRONMENT_CONTRACT
- 29_CD_DEPLOYMENT_CONTRACT
- 35_RESOURCE_TAGGING
- 40_CHANGELOG_GOVERNANCE
- 42_APP_TEMPLATE_LIVING

---

# Platform Boundaries & Contract

Doc contract:

- Purpose: Define platform vs team ownership and the minimum contract between them.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/01_GOVERNANCE.md, docs/20-contracts/42_APP_TEMPLATE_LIVING.md, docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md

This document defines the boundary between what the platform owns and what teams own, and the
contract between them.

## The platform contract

GoldenPath provides a delivery substrate with clear guarantees.

### The platform guarantees

- Deterministic infrastructure lifecycle (build, bootstrap, teardown).
- Standardized delivery mechanics (CI → GitOps → promotion).
- Secure-by-default primitives (identity, secrets, networking).
- Clear source of truth for state and configuration.
- Auditable change history and decision records.

If a team follows the GoldenPath, the platform guarantees these properties.

### Minimal platform contract (V1)

To keep the golden path deterministic and auditable, the platform enforces:

- **Required resource tags**: `BuildId`, `Environment`, `Lifecycle`, `ManagedBy`,
  `Owner`, `Project` (see `docs/10-governance/35_RESOURCE_TAGGING.md`).
- **Required CI inputs**: environment, lifecycle, and build ID inputs for
  ephemeral runs, plus explicit confirmation inputs for apply/bootstrap
  (see `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`).
- **Changelog gate**: when a PR is labeled `changelog-required`, a changelog
  entry is mandatory (see `docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md`).

## Platform responsibilities (control plane)

The platform owns how the system is built and operated.

- Infrastructure provisioning (Terraform, clusters, networking).
- CI/CD for platform-owned workloads.
- GitOps controllers and reconciliation.
- Identity and access primitives (OIDC, IRSA, SSM).
- Registry defaults and scanning posture.
- Baseline security floor.
- ADRs for platform-wide decisions.

Platform changes are deliberate, documented, and backward-aware.

## Team responsibilities (workload plane)

Teams own what they build and run on the platform.

- Application code and business logic.
- Image contents and build process (within platform constraints).
- Runtime behavior and scaling choices.
- Service-level decisions and tradeoffs.
- Adoption or extension of platform defaults.

Teams are not required to reimplement platform mechanics. They consume them.

## Decision ownership

Decisions are classified by scope, not importance.

### Platform decisions

- Affect multiple teams or shared infrastructure.
- Change security posture, delivery mechanics, or boundaries.
- Require an ADR.

### Product decisions

- Affect a single workload or service.
- Are made using the platform’s constraints.
- May use ADRs, but are not required to.

## Deviation model

GoldenPath is not authoritarian.

- Teams may deviate from defaults when necessary.
- Deviations must be explicit and understood.
- The platform documents why the default exists so teams can make informed tradeoffs.

## Stability & deviation

### Stable surfaces

- Core delivery rails (CI → GitOps → promotion).
- Identity and access primitives (OIDC, IRSA, SSM).
- Baseline security floor.

These are the default contract and change slowly.

### Experimental surfaces

- Optional tools and integrations.
- Non-default workflows or scanners.
- Early-stage features.

These can change faster and require explicit adoption.

### Deviation process

Teams may deviate from defaults when necessary, but must:

- state the reason and tradeoffs,
- document the deviation,
- accept support limitations for the non-standard path.

## Stability & exposure

GoldenPath will always evolve, but what we expose as stable is deliberate. We do not have to reveal
experimental features or grant access to capabilities we have not battle-tested ourselves. At this
stage, stability is defined by what the platform uses as its own reference path; everything else
remains internal until proven.
