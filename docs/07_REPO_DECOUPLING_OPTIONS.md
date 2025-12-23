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
