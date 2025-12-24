# GitOps and CI/CD

This document explains how the platform delivers changes using GitOps and
CI/CD. It keeps Argo CD details in one place.

## Goals

- Single source of truth in Git.
- Clear ownership of platform vs application delivery.
- Predictable promotion across environments.

## Current model (V1)

- **GitOps engine**: Argo CD.
- **CI**: GitHub Actions (pipeline details evolve by repo).
- **Source of truth**: this repo for platform tooling and shared services.

## Repository layout

- `gitops/argocd/apps/<env>`: Argo CD Application manifests per environment.
- `gitops/helm/<app>/values/<env>.yaml`: Helm values overrides per environment.

## Bootstrap flow (high level)

1) Terraform provisions infra and EKS add-ons.
2) Bootstrap runner installs Argo CD.
3) Argo CD Applications are applied from `gitops/argocd/apps/<env>`.
4) Argo CD reconciles apps to match Git.

## Sync policy

- Default is manual sync during bootstrap and early iterations.
- Auto-sync can be enabled later when drift and promotion rules are stable.

## Access and RBAC (bootstrap phase)

- Admin access is allowed temporarily for bootstrap.
- Use port-forward for Argo CD if there is no external Service.
- Tighten RBAC after bootstrap and route access through SSO.

## Drift handling

Some apps generate runtime state (e.g., webhook certificates). These should be
ignored via `ignoreDifferences` rules to prevent persistent OutOfSync noise.

## CI/CD integration (future)

- Pipeline creates or updates Argo CD Application manifests.
- Sync gates include preflight checks and environment approvals.
- Promotion is a Git change, not a manual kubectl step.
