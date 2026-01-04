---
id: ADR-0006
title: 'ADR-0006: Use AWS Secrets Manager/SSM as system of record for secrets and
  External Secrets to hydrate Kubernetes'
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

- ADR-0003
- ADR-0006
- ADR-0007

---

# ADR-0006: Use AWS Secrets Manager/SSM as system of record for secrets and External Secrets to hydrate Kubernetes

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security / Operations / Governance
- **Related docs:** docs/08_SOURCE_OF_TRUTH.md, docs/06_REBUILD_SEQUENCE.md, ADR-0003-iam-irsa-ssm.md

## Context

The platform is frequently rebuilt and clusters are disposable. Any secret stored only inside the cluster risks loss and encourages manual fixes.

We want a secure, auditable, and repeatable secrets workflow:

- no long-lived credentials committed to Git
- minimal manual steps during rebuild
- least-privilege access for workloads

## Decision

- **System of record:** AWS **Secrets Manager** and/or **SSM Parameter Store** hold secret material.
- **In-cluster hydration:** Kubernetes Secrets are created/updated via **External Secrets Operator** (ExternalSecrets resources tracked in Git).
- **No secrets in Git:** secret values must never be committed to the repo. Git stores references only.
- **Access control:** External Secrets Operator uses **IRSA** with least-privilege policies per environment.

## Scope

- Applies to: platform tooling secrets (Argo, Backstage, Keycloak, Kong) and app secrets deployed via GitOps.
- Out of scope (V1): complex secret templating beyond ESO patterns; multi-cloud secret abstraction.

## Consequences

### Positive

- Secrets survive cluster teardown; rebuilds remain deterministic.
- Eliminates static key sprawl in Git/Kubernetes.
- Clear ownership boundary: AWS is truth, cluster is cache.

### Negative / Tradeoffs

- Requires IRSA wiring and network reachability to AWS APIs.
- Adds dependency on External Secrets Operator availability and correct configuration.
- Requires disciplined secret naming and rotation approach.

### Operational implications

- Define naming conventions:

- `/goldenpath/<env>/<component>/<secret>`

- Define rotation approach (manual/automatic) per secret type.
- Add runbooks:

- creating/updating secrets in AWS

- verifying ESO sync

- incident response if secrets fail to hydrate

- CI/GitOps checks:

- block accidental secret commits (secret scanning)

- validate ExternalSecret manifests exist for required components

## Alternatives considered

- Kubernetes Secrets as system of record (rejected due to teardown + drift risk)
- Sealed Secrets / SOPS in Git (viable, but still places encrypted secrets in repo; chosen to keep AWS as source of truth)
- Hardcoded values in Helm (rejected)

## Follow-ups / Actions

- Deploy External Secrets Operator as a core platform addon (GitOps).
- Create IRSA role/policy for ESO per environment.
- Add a “bootstrap seed” procedure for first-time secrets creation in AWS.
- Add repo secret scanning and a “no secrets in Git” enforcement gate.

If you want one more “glue” piece, I can draft:

- docs/adrs/ADR-0007-platform-environment-model.md (1 cluster vs 2 clusters vs 4 clusters) with the cost/time/credibility tradeoffs you’ve already reasoned through.
