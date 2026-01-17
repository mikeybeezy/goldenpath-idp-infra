---
id: ADR-0013-platform-argo-app-management-approach
title: 'ADR-0013: Argo CD app management approach for current scale'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 07_REPO_DECOUPLING_OPTIONS
  - ADR-0013-platform-argo-app-management-approach
  - BOOTSTRAP_10_BOOTSTRAP_README
  - RB-0012-argocd-app-readiness
  - audit-20260103
  - goldenpath-idp-bootstrap
  - one_stage_vs_multistage_bootstrap
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---
# ADR-0013: Argo CD app management approach for current scale

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** platform team
- **Domain:** Application
- **Decision type:** Operations
- **Related:** `docs/30-architecture/07_REPO_DECOUPLING_OPTIONS.md`

---

## Context

We need to decide how to manage Argo CD applications in production. The two options are:

- App-of-apps (a root Application that points at a folder of child Applications).
- ApplicationSet (a controller that generates Applications from a template and generator).

The current platform is a small, stable setup with a single repo and a limited number of
environments. We want to minimize operational overhead while keeping a path to scale.

---

## Decision

> We will use app-of-apps for the current platform scale and defer ApplicationSet until scaling
> requirements justify it.

---

## Scope

Applies to how Argo CD applications are organized in the current platform repositories and
environments. This does not prevent future adoption of ApplicationSet when the platform grows.

---

## Consequences

### Positive

- Simple setup with fewer moving parts in production.
- Clear, explicit application manifests that are easy to audit.

### Tradeoffs / Risks

- Manual scaling for additional clusters/environments.
- Potential manifest duplication as the platform grows.

### Operational impact

- Platform team maintains app-of-apps structure in the tooling repo.
- Revisit this decision when cluster/env count increases materially.

---

## Alternatives considered

### ApplicationSet now

Pros:

- Scales cleanly across clusters and environments.
- Reduces YAML duplication through templating.

Cons:

- Adds another controller to operate and upgrade.
- Generated applications can be harder to debug.

---

## Follow-ups

- Document app-of-apps structure in the tooling repo.
- Reassess if multi-cluster or per-team app growth accelerates.

---

## Notes

ApplicationSet remains the preferred path for future scale, but is not required today.
