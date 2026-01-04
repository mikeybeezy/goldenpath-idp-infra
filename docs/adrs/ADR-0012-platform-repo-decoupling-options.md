---
id: ADR-0012
title: 'ADR-0012: Repo decoupling options for infra and platform tooling'
type: adr
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
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
- 07_REPO_DECOUPLING_OPTIONS
- ADR-0012
---

# ADR-0012: Repo decoupling options for infra and platform tooling

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md`

---

## Context

We need to plan how to separate infrastructure and platform tooling repositories once the platform
stabilizes. Today everything lives in one monorepo, which is simple but mixes ownership and expands
blast radius.

---

## Decision

> We will keep a monorepo for now and move to a two-repo split once the dev baseline is stable.

The recommended target state is two repos:

- `platform-infra`: Terraform, cluster bootstrap, IAM, networking.
- `platform-tooling`: GitOps apps (Argo CD Applications) and Helm values.

Argo CD app-of-apps will live in the tooling repo; the infra repo will only bootstrap the cluster
and point Argo CD to the tooling repo.

---

## Scope

Applies to repository structure for infrastructure, GitOps app definitions, and platform tooling
configuration. Does not change any current repo layout immediately.

---

## Consequences

### Positive

- Clear ownership and separation of concerns in the target state.
- Independent release cadence for infra vs tooling.
- Easier access control and permissions.

### Tradeoffs / Risks

- Coordination needed for cross-repo changes.
- Bootstrap must reference the tooling repo.
- More operational overhead compared to a single repo.

### Operational impact

- Plan and execute a controlled repo split when the dev baseline is stable.
- Update bootstrap flows to point to the tooling repo.

---

## Alternatives considered

### Option A: Monorepo (current)

Keep Terraform, bootstrap, and GitOps app definitions in one repository.

Pros:

- Single PR flow for cross-cutting changes.
- Simple bootstrapping and onboarding.

Cons:

- Mixed ownership and broader blast radius.
- Harder to enforce access boundaries.

### Option B: Two repos (recommended target)

Split into:

- `platform-infra`: Terraform, cluster bootstrap, IAM, networking.
- `platform-tooling`: GitOps apps (Argo CD Applications) and Helm values.

Pros:

- Clear ownership and separation of concerns.
- Independent release cadence for infra vs tooling.
- Easier access control.

Cons:

- Coordination needed for cross-repo changes.
- Bootstrap needs to reference tooling repo.

### Option C: Three repos (finer-grained)

Split into:

- `platform-infra`: Terraform, IAM, VPC, EKS.
- `platform-gitops`: Argo CD Applications, base GitOps structure.
- `platform-tooling-config`: dashboards, Keycloak realms, app config.

Pros:

- Strong access isolation and release control.
- Fits larger orgs with multiple platform teams.

Cons:

- More operational overhead.
- More cross-repo orchestration.

### Option D: Infra repo + per-team app repos

Infra repo owns cluster + Argo CD; each team owns its own app repo.

Pros:

- Team autonomy and least central bottleneck.

Cons:

- Requires strict conventions and guardrails.
- Harder to standardize and audit.

---

## Follow-ups

- When dev baseline is stable, execute Option B split.
- Move Argo CD app-of-apps and GitOps definitions into the tooling repo.

---

## Notes

This ADR captures the recommended target and does not require immediate changes.
