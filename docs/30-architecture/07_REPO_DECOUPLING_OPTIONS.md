---
id: 07_REPO_DECOUPLING_OPTIONS
title: Repo Decoupling Options
type: adr
applies_to:
  - infra
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - 01_GOVERNANCE
  - 09_ARCHITECTURE
  - ADR-0012-platform-repo-decoupling-options
  - ADR-0013-platform-argo-app-management-approach
category: architecture
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:vpc
  - module:aws_eks
  - module:aws_iam
  - chart:argo-cd
breaking_change: false
---

# Repo Decoupling Options

This document captures options for separating infrastructure and platform tooling
into distinct repositories once the platform stabilizes.

## Option A: Monorepo (current)

Keep Terraform, bootstrap, and GitOps app definitions in one repository.

Pros:

- Single PR flow for cross-cutting changes.
- Simple bootstrapping and onboarding.

Cons:

- Mixed ownership and broader blast radius.
- Harder to enforce access boundaries.

## Option B: Two repos (recommended target)

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

## Option C: Three repos (finer-grained)

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

## Option D: Infra repo + per-team app repos

Infra repo owns cluster + Argo CD; each team owns its own app repo.

Pros:

- Team autonomy and least central bottleneck.

Cons:

- Requires strict conventions and guardrails.
- Harder to standardize and audit.

## Recommendation

Move to Option B once dev baseline is stable. Keep Argo CD app-of-apps in the
tooling repo; infra repo only bootstraps the cluster and points Argo CD to the
tooling repo.
