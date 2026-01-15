---
id: ADR-0135
title: 'ADR-0135: Secrets Manager + External Secrets Operator foundation'
type: adr
status: proposed
domain: platform-core
owner: platform-team
lifecycle: proposed
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0006
  - ADR-0015
  - ADR-0031
  - 85-how-it-works/secrets-flow/SECRET_REQUEST_FLOW.md
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-09
version: 1.0
breaking_change: false
---

# ADR-0135: Secrets Manager + External Secrets Operator foundation

- **Status:** Proposed
- **Date:** 2026-01-09
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Security | Operations
- **Related:** ADR-0006, ADR-0015, ADR-0031

---

## Context

We need a deterministic, auditable secrets flow for the IDP golden path. Today,
secrets handling is ad hoc, and does not provide a governed path for app teams.
We want a consistent source of truth and a safe, repeatable sync into Kubernetes,
aligned with GitOps and existing IAM/IRSA contracts.

## Decision

We will use **AWS Secrets Manager** as the source of truth and **External
Secrets Operator (ESO)** as the sync mechanism into Kubernetes. The foundation
will be implemented as a platform layer and exposed to golden path templates.

## Scope

**Applies to:**
- Platform baseline for secrets in `dev` (V1).
- Secrets used by golden path app templates.
- IRSA/OIDC roles and SecretStore/ClusterSecretStore contracts.

**Does not apply to:**
- SSM Parameter Store (deferred).
- Runbooks and operational playbooks (deferred).
- Non-Kubernetes workloads (out of scope for V1).

## Consequences

### Positive

- Single source of truth for secrets.
- Deterministic sync into clusters (GitOps-compatible).
- Standardized contract for teams and templates.
- Scales across environments without per-cluster re-encryption.

### Tradeoffs / Risks

- Adds a controller and CRDs to manage.
- Requires careful IAM/IRSA scoping and naming discipline.
- Rotation and incident response runbooks remain deferred.

### Operational impact

- Platform team must manage ESO install and IAM/IRSA.
- App templates must reference SecretStore + ExternalSecret.

## Alternatives considered

### HashiCorp Vault

**Pros**
- Multi-cloud, vendor-neutral.
- Dynamic secrets (short-lived DB/IAM creds) with strong policy model.
- Rich audit and leasing/renewal.

**Cons**
- Requires operating the control plane (HA, storage, upgrades, unseal).
- Higher operational burden and on-call maturity.
- More moving parts for V1 adoption.

### Sealed Secrets Operator

**Pros**
- GitOps-native (encrypted secrets stored in Git).
- Simple operational model; no external store required.

**Cons**
- Secrets are cluster-tied (re-encrypt per cluster).
- No external source of truth or centralized rotation.
- Less scalable across multi-env fleets.

### AWS Secrets Manager + ESO (chosen)

**Pros**
- Managed source of truth; strong audit trail.
- Clean integration with IRSA/OIDC and ESO.
- Scales across environments without per-cluster re-encryption.

**Cons**
- AWS-only (vendor lock-in).
- Custom rotation requires extra work.
- More moving parts than sealed secrets.

### Raw K8s Secrets

- No external source of truth; high drift and audit risk.

### SSM Parameter Store only

- Cheaper, but fewer features and weaker rotation model.

## Follow-ups

- Add ESO Helm release via GitOps.
- Define SecretStore/ClusterSecretStore contracts.
- Update templates to emit ExternalSecret definitions.
- Defer runbook creation until first rollout proves stable.

## Notes

- Future: support SSM as optional store once Secrets Manager is stable.
- This decision does not mandate immediate rollout to all services.
