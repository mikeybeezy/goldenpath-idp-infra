---
id: ADR-0174-pipeline-decoupling-from-cluster-bootstrap
title: 'ADR-0174: Pipeline enablement intentionally decoupled from cluster bootstrap'
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
  - ADR-0007-platform-environment-model
  - ADR-0026-platform-cd-deployment-contract
  - ADR-0170
  - GOV-0012-build-pipeline-standards
  - RB-0036
  - RB-0037
  - ROADMAP
  - session-2026-01-19-build-pipeline-architecture
supersedes: []
superseded_by: []
tags:
  - pipeline
  - bootstrap
  - decoupling
  - gitops
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 0.0
supported_until: 2027-01-19
version: '1.0'
breaking_change: false
---
# ADR-0174: Pipeline enablement intentionally decoupled from cluster bootstrap

Filename: `ADR-0174-pipeline-decoupling-from-cluster-bootstrap.md`

- **Status:** Active
- **Date:** 2026-01-19
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform Core
- **Decision type:** Architecture
- **Related:** ADR-0170, ADR-0007, GOV-0012, RB-0036, RB-0037

---

## Context

GoldenPath IDP clusters are bootstrapped through a multi-stage process that
provisions EKS, ArgoCD, monitoring, and foundational workloads. A separate
concern is enabling the CI/CD pipeline that allows ArgoCD Image Updater to
write back image tag changes to Git repositories.

Pipeline enablement requires:
1. GitHub App creation (organization-level)
2. Secrets Manager entries for credentials
3. Kubernetes secrets in target cluster
4. ArgoCD Application annotations for write-back

This creates an ordering challenge: the cluster must exist before K8s secrets
can be created, but the secrets must exist before Image Updater can function.

## Decision

**Pipeline enablement is intentionally decoupled from cluster bootstrap.**

This means:
1. **Cluster bootstrap completes without pipeline secrets** - The cluster is
   fully functional for GitOps deployments using digest-based image references.
2. **Pipeline enablement is a separate operational event** - Performed after
   cluster bootstrap, documented in RB-0037.
3. **Image Updater gracefully degrades** - Uses `optional: true` for secrets
   in dev environments, allowing the cluster to come up without pipeline creds.

### Rationale

| Concern | Coupled Approach | Decoupled Approach |
|---------|------------------|-------------------|
| Bootstrap failure | Fails if GitHub App not ready | Succeeds independently |
| GitHub App lifecycle | Must pre-exist | Can be created post-bootstrap |
| Secret rotation | Requires cluster redeploy | Independent secret update |
| Multi-cluster | Complex ordering | Enable per-cluster as needed |
| Local/dev testing | Blocked on secrets | Works immediately |

### Implementation Pattern

```
Bootstrap Phase (Cluster Creation):
┌─────────────────────────────────────────────────────┐
│ Terraform → EKS → ArgoCD → Apps (digest-based)     │
│                                                     │
│ Image Updater deployed with optional: true          │
│ Cluster functional without pipeline secrets        │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
Pipeline Enablement Phase (Separate Event):
┌─────────────────────────────────────────────────────┐
│ 1. Create GitHub App (if not exists)                │
│ 2. Store creds in Secrets Manager                   │
│ 3. Create K8s secret (manual or ExternalSecret)     │
│ 4. Verify write-back functionality                  │
│                                                     │
│ Image Updater now writes to Git                    │
└─────────────────────────────────────────────────────┘
```

### Environment-Specific Behavior

| Environment | Secret Optionality | Behavior Without Secret |
|-------------|-------------------|------------------------|
| local | N/A | Uses digest strategy, no write-back |
| dev | `optional: true` | Graceful degradation, logs warning |
| test | `optional: false` | Deployment fails without secret |
| staging | `optional: false` | Deployment fails without secret |
| prod | `optional: false` | Deployment fails without secret |

## Scope

Applies to:
- All GoldenPath IDP cluster deployments
- ArgoCD Image Updater configuration
- Pipeline authentication setup

Does not apply to:
- Application-level CI (GitHub Actions workflows)
- ECR push authentication (handled by OIDC)

## Consequences

### Positive

- **Cluster bootstrap is self-contained** - No external GitHub dependencies.
- **Separation of concerns** - Cluster ops vs. pipeline ops are distinct.
- **Flexible timing** - Enable pipeline when ready, not during bootstrap.
- **Local development works** - No need for GitHub App for local testing.
- **Clear failure modes** - Bootstrap failures unrelated to pipeline setup.

### Tradeoffs / Risks

- **Additional operational step** - Pipeline must be explicitly enabled.
- **Potential for drift** - Test/staging/prod require secrets; forgetting
  causes deployment failures (mitigated by `optional: false`).
- **Documentation overhead** - Must document the enablement process clearly.

### Operational Impact

- Operators must follow RB-0037 after cluster bootstrap to enable pipeline.
- For non-dev environments, Image Updater deployment will fail if secrets
  are missing, providing a clear signal.
- Secret rotation is independent of cluster lifecycle.

## Alternatives Considered

### Option A: Pipeline as Part of Bootstrap

Bootstrap script creates GitHub App, stores secrets, and provisions K8s
secrets as part of the cluster creation process.

**Rejected because:**
- Creates complex dependencies between GitHub org and cluster
- Bootstrap becomes fragile (GitHub API failures block cluster creation)
- Local/ephemeral clusters unnecessarily require GitHub App

### Option B: Sync Wave Approach

Use ArgoCD sync waves to create secrets after other resources.

**Rejected because:**
- Secrets Manager credentials still need to exist
- Adds complexity to sync ordering
- Doesn't solve the GitHub App creation timing

### Option C: Terraform-Managed K8s Secrets

Use Terraform to create K8s secrets directly.

**Rejected because:**
- Mixes infrastructure and cluster configuration
- Requires Terraform to have K8s API access during apply
- State management becomes complex

## Follow-ups

- Maintain RB-0037 as the canonical pipeline enablement runbook.
- Consider ExternalSecret CRD for automated secret sync from Secrets Manager.
- Add CI check to verify pipeline secrets exist for non-dev environments.

## Notes

This decision aligns with the "explicit over implicit" philosophy: enabling
the pipeline is a deliberate operational choice, not an automatic side effect
of cluster creation. This makes the system more predictable and debuggable.
