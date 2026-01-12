---
id: ADR-0001-platform-argocd-as-gitops-operator
title: 'ADR-0001: Adopt Argo CD as GitOps controller for platform deployments'
type: adr
status: active
domain: platform-core
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0001
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0001: Adopt Argo CD as GitOps controller for platform deployments

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture / Operations
- **Related docs:** docs/06_REBUILD_SEQUENCE.md, docs/08_SOURCE_OF_TRUTH.md, docs/30-architecture/04_REPO_STRUCTURE.md

## Context

We need a deterministic, auditable mechanism to deploy and reconcile platform components (Kong, cert-manager, autoscaler, etc.) on EKS.

We want a single, clear source of truth for in-cluster resources and to remove ambiguity caused by multiple reconciliation systems.

## Decision

Use **Argo CD** as the GitOps controller and single source of truth for Kubernetes application deployment state.

Platform apps are expressed as Argo CD Applications (app-of-apps pattern) and reconciled continuously from the Git repository.

## Scope

- Applies to: all platform apps deployed to EKS via GitOps (core + tooling).
- Out of scope: Terraform-managed AWS infrastructure (VPC/EKS/IAM) and external API configuration managed via Terraform providers.

## Consequences

### Positive

- Clear reconciliation model; cluster state converges toward Git.
- Improved auditability: change history is visible via PRs + Argo sync history.
- Enables promotion workflows by changing Git and letting Argo apply.

### Negative / Tradeoffs

- Need to manage Argo “status noise” (OutOfSync/Unknown for dynamic fields).
- Requires disciplined repo structure and Argo RBAC/projects to avoid accidental changes.

### Operational implications

- Bootstrap must install Argo and create the root Application deterministically.
- Add `ignoreDifferences` for known dynamic fields to reduce false drift.
- Define “hands-off vs prompted” steps in rebuild sequence.

## Alternatives considered

- **Flux CD**: not chosen due to standardization on Argo and desire to remove Flux CRD references.
- **Manual kubectl/Helm**: not acceptable for determinism/auditability.
- **Hybrid multiple controllers**: increases ambiguity and support burden.

## Follow-ups / Actions

- Implement app-of-apps layout under `gitops/argocd/apps/<env>/`.
- Add Argo drift management (`ignoreDifferences`) for known dynamic resources.
- Define Argo Projects/RBAC boundaries for environments and platform namespaces.

## Notes

If multi-cluster is introduced (dev/test vs stage/prod), Argo remains the deployment mechanism; only destinations change.
