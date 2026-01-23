---
id: V1_DETERMINISM_CRITERIA
title: V1 Determinism Criteria - Synthesized Claude + Codex Recommendations
type: documentation
domain: product
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - PRODUCT_THESIS
---

# V1 Determinism Criteria

**Date:** 2026-01-23
**Contributors:** Claude Opus 4.5, Codex
**Purpose:** Synthesized recommendations for achieving repeatable, deterministic V1 success

---

## Synthesized Insights

### From Claude (Architecture Focus)

| Insight | Implication |
| ------- | ----------- |
| Shipping pipeline != production topology | Tiers 0-1 (fast feedback) vs Tiers 2-3 (full stack) |
| Keycloak is prod-only concern | Non-prod uses GitHub OAuth or static admin |
| DNS is global, ephemeral is not | Build-scoped subdomains prevent collisions |
| ClusterIssuers gap exists | TLS will fail until ArgoCD app deploys them |
| AI traversability requires discipline | Documentation patterns, not magic |

### From Codex (Determinism Focus)

| Insight | Implication |
| ------- | ----------- |
| Success must be explicit | Pass/fail criteria per tier, not vibes |
| Tier 2/3 can regress silently | Nightly validation catches DB/auth drift |
| Dependencies drift without contracts | Version and document RDS/IAM prerequisites |
| Convention != enforcement | Policy gates (Kyverno) prevent accidental tier violations |
| Inputs must be pinned | Frozen versions = reproducible outcomes |

### Unified Thesis

**Deterministic V1 = Explicit Criteria + Tiered Validation + Enforced Boundaries**

---

## Foundational vs Disposable Planes

### Core Principle

**Ephemeral cannot exist without Persistent.**

The platform operates on two planes with a strict dependency:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDATIONAL PLANE                           │
│                    (Persistent - must exist first)              │
├─────────────────────────────────────────────────────────────────┤
│  VPC + Subnets        (networking foundation)                   │
│  Route53 Hosted Zone  (DNS parent)                              │
│  RDS PostgreSQL       (database state)                          │
│  Secrets Manager      (credential store)                        │
│  ECR Repositories     (image registry)                          │
│  IAM Roles + Policies (IRSA foundation)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ PROVIDES
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DISPOSABLE PLANE                             │
│                    (Ephemeral - consumes foundational)          │
├─────────────────────────────────────────────────────────────────┤
│  EKS Cluster          (compute - can be destroyed/recreated)    │
│  ArgoCD + Apps        (deployment state - recreatable)          │
│  Kong Ingress         (traffic routing - stateless)             │
│  Pods + Services      (workloads - ephemeral by nature)         │
└─────────────────────────────────────────────────────────────────┘
```

### Dependency Rules

| Rule | Constraint |
| ---- | ---------- |
| **Rule 1** | Foundational plane MUST be deployed before any ephemeral cluster |
| **Rule 2** | Ephemeral clusters CONSUME foundational resources, never CREATE them |
| **Rule 3** | Destroying ephemeral does NOT affect foundational state |
| **Rule 4** | Foundational teardown requires explicit confirmation (destructive) |

### What Each Plane Provides

| Plane | Provides | Lifecycle | Terraform State |
| ----- | -------- | --------- | --------------- |
| Foundational | VPC, RDS, Route53, Secrets, ECR, IAM | Long-lived | `envs/dev-persistent/`, `envs/dev-rds/` |
| Disposable | EKS, ArgoCD, Kong, workloads | Short-lived | `envs/dev/` (ephemeral clusters) |

### Deployment Order

```text
1. Deploy Foundational (once per environment)
   └── VPC exists
   └── RDS exists
   └── Route53 zone exists
   └── Secrets Manager populated
   └── ECR repos created
   └── IAM roles ready

2. Deploy Disposable (many times, on-demand)
   └── EKS cluster created IN existing VPC
   └── IRSA assumes existing IAM roles
   └── ESO pulls FROM existing Secrets Manager
   └── ExternalDNS creates records IN existing Route53
   └── Backstage connects TO existing RDS
```

### Why This Matters

Without this constraint:

- Ephemeral clusters would try to create VPCs (collision, drift)
- Each cluster would deploy its own RDS (waste, inconsistency)
- Teardown would orphan DNS records or leave dangling resources
- No shared state = no Tier 2/3 services possible

With this constraint:

- Ephemeral is truly disposable (delete cluster, foundational untouched)
- Shared RDS means Backstage/Keycloak work across clusters
- DNS parent zone managed centrally, children scoped per-build
- Clear separation of "what persists" vs "what gets torn down"

---

## V1 Success Criteria

### Tier 0: Cluster Viability

| Check | Command | Pass | Fail |
| ----- | ------- | ---- | ---- |
| EKS API responsive | `kubectl cluster-info` | Returns API server URL | Timeout or connection refused |
| Nodes ready | `kubectl get nodes` | All nodes STATUS=Ready | Any NotReady or missing |
| CoreDNS resolving | `kubectl run test --rm -i --image=busybox -- nslookup kubernetes` | Returns IP | NXDOMAIN or timeout |
| CNI functional | Pod-to-pod ping test | Packets received | Network unreachable |

### Tier 1: Delivery Plane

| Check | Command | Pass | Fail |
| ----- | ------- | ---- | ---- |
| ArgoCD healthy | `kubectl get app -n argocd root-app -o jsonpath='{.status.health.status}'` | Healthy | Degraded/Missing/Unknown |
| Kong accepting traffic | `curl -s -o /dev/null -w "%{http_code}" http://<kong-proxy>/healthz` | 200 | 502/503/timeout |
| ExternalDNS running | `kubectl get pods -n external-dns -l app.kubernetes.io/name=external-dns` | 1/1 Running | CrashLoopBackOff |
| ESO syncing | `kubectl get externalsecret -A -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'` | All True | Any False |

### Tier 2: Platform Experience

| Check | Command | Pass | Fail |
| ----- | ------- | ---- | ---- |
| Backstage UI | `curl -s -o /dev/null -w "%{http_code}" https://backstage.<env>.goldenpathidp.io` | 200 | 500/502/connection refused |
| Backstage DB connected | Backstage logs show "Database connection established" | Present | "Connection refused" in logs |
| Grafana dashboards | `curl -s https://grafana.<env>.goldenpathidp.io/api/health` | `{"database":"ok"}` | Database not ok |

### Tier 3: Production Identity

| Check | Command | Pass | Fail |
| ----- | ------- | ---- | ---- |
| Keycloak realm | `curl -s https://keycloak.<env>.goldenpathidp.io/realms/goldenpath` | Returns realm JSON | 404 or connection refused |
| OIDC token | Request token via client credentials | Returns access_token | 401/403 |
| RBAC enforced | Attempt unauthorized action | 403 Forbidden | Action succeeds |

---

## Implementation Phases

### Phase 1: V1 Baseline (Immediate)

**Goal:** Tier 0-1 passes reliably on every ephemeral deploy

| Step | Action | Owner | Artifact |
| ---- | ------ | ----- | -------- |
| 1.1 | Add Tier 0-1 smoke test to CI | Platform | `.github/workflows/tier-validation.yml` |
| 1.2 | Pin all Helm chart versions | Platform | `gitops/helm/*/values/*.yaml` |
| 1.3 | Pin EKS add-on versions | Platform | `envs/dev/terraform.tfvars` |
| 1.4 | Document current pinned versions | Platform | `docs/VERSION_MANIFEST.md` |

**Acceptance:** 3 consecutive ephemeral deploys pass Tier 0-1 checks

### Phase 2: RDS Foundation (Next)

**Goal:** Tier 2 prerequisites in place

| Step | Action | Owner | Artifact |
| ---- | ------ | ----- | -------- |
| 2.1 | Deploy standalone RDS | Platform | `gh workflow run rds-database-apply.yml -f environment=dev` |
| 2.2 | Verify secrets created | Platform | Check Secrets Manager for `goldenpath/dev/backstage/postgres` |
| 2.3 | Document RDS connectivity contract | Platform | `docs/RDS_CONNECTIVITY_CONTRACT.md` |
| 2.4 | Add RDS health to Tier 2 validation | Platform | Extend `tier-validation.yml` |

**Acceptance:** Backstage pod connects to RDS, UI returns 200

### Phase 3: TLS Foundation (V1.1)

**Goal:** ClusterIssuers deployed, TLS functional

| Step | Action | Owner | Artifact |
| ---- | ------ | ----- | -------- |
| 3.1 | Create ArgoCD app for ClusterIssuers | Platform | `gitops/argocd/apps/dev/cert-manager-issuers.yaml` |
| 3.2 | Validate certificate issuance | Platform | `kubectl get certificate -A` shows Ready |
| 3.3 | Add TLS check to Tier 1 validation | Platform | Extend `tier-validation.yml` |

**Acceptance:** Ingresses have valid TLS certificates

### Phase 4: Policy Enforcement (V1.1)

**Goal:** Tier boundaries enforced by policy, not convention

| Step | Action | Owner | Artifact |
| ---- | ------ | ----- | -------- |
| 4.1 | Configure Kyverno policies | Platform | `gitops/kustomize/bases/kyverno/policies/` |
| 4.2 | Block Tier 2/3 workloads in ephemeral | Platform | Policy: deny if `lifecycle=ephemeral` AND `tier in [2,3]` |
| 4.3 | Add policy validation to CI | Platform | `kyverno test` in pre-commit |

**Acceptance:** Attempt to deploy Keycloak in ephemeral fails with policy violation

### Phase 5: Nightly Validation (V1.1)

**Goal:** Tier 2/3 regressions caught before they matter

| Step | Action | Owner | Artifact |
| ---- | ------ | ----- | -------- |
| 5.1 | Create nightly validation workflow | Platform | `.github/workflows/nightly-tier-validation.yml` |
| 5.2 | Run against persistent dev cluster | Platform | Cron: `0 2 * * *` |
| 5.3 | Alert on Tier 2/3 failures | Platform | Slack/email notification |

**Acceptance:** Nightly run completes, alerts on failure

---

## Dependency Contracts

### RDS Connectivity Contract

```yaml
# Contract version: 1.0.0
prerequisites:
  networking:
    - VPC peering or same VPC as EKS
    - Security group allows 5432 from EKS node SG
    - Subnet routing allows EKS-to-RDS traffic
  iam:
    - ESO service account has secretsmanager:GetSecretValue
    - Secret ARN matches ExternalSecret spec
  secrets:
    - Secret exists: goldenpath/{env}/{app}/postgres
    - Secret contains: username, password, host, port, dbname
```

### DNS Ownership Contract

```yaml
# Contract version: 1.0.0
persistent_cluster:
  allowed_namespace: "*.{env}.goldenpathidp.io"
  externaldns_owner_id: "{env}-persistent"
ephemeral_cluster:
  allowed_namespace: "*.b-{buildId}.{env}.goldenpathidp.io"
  externaldns_owner_id: "b-{buildId}"
  prohibited: "*.{env}.goldenpathidp.io"  # MUST NOT create
```

---

## Version Manifest (V1 Frozen)

| Component | Version | Source |
| --------- | ------- | ------ |
| EKS | 1.29 | `envs/dev/terraform.tfvars` |
| cert-manager | v1.14.4 | `gitops/helm/cert-manager/values/dev.yaml` |
| ArgoCD | 2.10.x | `gitops/helm/argocd/values/dev.yaml` |
| Kong | 3.6.x | `gitops/helm/kong/values/dev.yaml` |
| ExternalDNS | 0.14.x | `gitops/helm/external-dns/values/dev.yaml` |
| Backstage | 1.26.x | `backstage-helm/charts/backstage/values.yaml` |

**Rule:** No version changes during V1 stabilization without ADR.

---

## Summary

| Phase | Scope | Blocker | Target |
| ----- | ----- | ------- | ------ |
| 1 | Tier 0-1 CI validation | None | Immediate |
| 2 | RDS + Tier 2 | IAM permissions | After Phase 1 |
| 3 | TLS + ClusterIssuers | None | V1.1 |
| 4 | Policy enforcement | Kyverno risk | V1.1 |
| 5 | Nightly Tier 2/3 | RDS working | V1.1 |

**V1 Complete When:** Phases 1-2 pass consistently.
**V1.1 Complete When:** Phases 3-5 operational.

---

Signed: Claude Opus 4.5 + Codex Synthesis (2026-01-23)
