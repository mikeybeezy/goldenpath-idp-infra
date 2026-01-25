---
id: ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
title: 'ADR-0178: Ephemeral vs Persistent DNS Ownership and Bootstrap Contract'
type: adr
status: proposed
domain: platform-core
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 40.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0175-externaldns-wildcard-ownership
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - ADR-0180-argocd-orchestrator-contract
  - 21_CI_ENVIRONMENT_CONTRACT
supersedes: []
superseded_by: []
tags:
  - dns
  - ephemeral
  - persistent
  - bootstrap
  - keycloak
  - v2
inheritance: {}
supported_until: 2028-01-23
version: '1.0'
breaking_change: true
---

# ADR-0178: Ephemeral vs Persistent DNS Ownership and Bootstrap Contract

- **Status:** Proposed (V2 Roadmap)
- **Date:** 2026-01-23
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Operations
- **Related:** ADR-0158 (Standalone RDS), ADR-0175 (ExternalDNS Ownership)
- **Implemented by:** ADR-0179 (Dynamic Hostname Generation)

---

## Context

V1 treats ephemeral and persistent clusters identically during bootstrap. This creates several collision risks:

1. **DNS collisions**: Multiple ephemeral clusters fight over the same hostnames (`backstage.dev.goldenpathidp.io`)
2. **Keycloak duplication**: Each cluster deploys Keycloak, but ephemeral clusters should share the persistent Keycloak
3. **Resource waste**: Ephemeral clusters deploy services they shouldn't own

### The Core Problem

DNS is a global namespace. Ephemeral clusters are non-global by nature. If ephemeral writes to the same DNS zone as persistent, collisions are inevitable, not edge cases.

```
Ephemeral Cluster A creates: backstage.dev.goldenpathidp.io → ALB-A
Ephemeral Cluster B creates: backstage.dev.goldenpathidp.io → ALB-B
                             └── COLLISION: Record flaps or overwrites
```

## Decision

We will establish a **Plane Architecture**, **DNS Ownership Contract**, and **Bootstrap Mode Differentiation**.

### Foundational vs Disposable Planes

**Core constraint: Ephemeral cannot exist without Persistent.**

| Plane | Also Known As | What It Contains | Lifecycle |
| ----- | ------------- | ---------------- | --------- |
| Foundational | Persistent | VPC, RDS, Route53, Secrets Manager, ECR, IAM | Long-lived, rarely destroyed |
| Disposable | Ephemeral | EKS cluster, ArgoCD, Kong, workloads | Short-lived, frequently destroyed |

**Dependency Rules:**

1. Foundational plane MUST be deployed before any ephemeral cluster
2. Ephemeral clusters CONSUME foundational resources, never CREATE them
3. Destroying ephemeral does NOT affect foundational state
4. Foundational teardown requires explicit confirmation (destructive)

```text
Foundational (deploy once)     Disposable (deploy many)
─────────────────────────────  ─────────────────────────────
VPC + Subnets          ──────► EKS cluster uses VPC
Route53 Zone           ──────► ExternalDNS creates child records
RDS PostgreSQL         ──────► Backstage/Keycloak connect
Secrets Manager        ──────► ESO pulls credentials
ECR Repositories       ──────► Pods pull images
IAM Roles              ──────► IRSA assumes roles
```

**Why this matters:** Without this constraint, ephemeral clusters would create competing resources (VPCs, databases), teardown would orphan state, and there would be no shared services for Tier 2/3.

### DNS Ownership Contract

| Cluster Type | Allowed DNS Namespace | Example |
|--------------|----------------------|---------|
| Persistent | `*.{env}.goldenpathidp.io` | `backstage.dev.goldenpathidp.io` |
| Ephemeral | `*.b-{buildid}.{env}.goldenpathidp.io` | `backstage.b-23-01-26-01.dev.goldenpathidp.io` |

**Rule:** Ephemeral clusters may NEVER create records in the base `*.{env}.goldenpathidp.io` namespace.

### Bootstrap Mode Differentiation

```yaml
bootstrap:
  mode: ephemeral | persistent
```

| Component | Persistent Mode | Ephemeral Mode |
|-----------|-----------------|----------------|
| Keycloak | Deploy (owns identity) | Skip (uses persistent Keycloak) |
| Backstage | Deploy | Deploy (with build-scoped DNS) |
| ArgoCD | Deploy | Deploy (with build-scoped DNS) |
| ExternalDNS | Manages `*.{env}.` | Manages `*.b-{buildid}.{env}.` only |
| RDS | Create (if standalone not exists) | Use standalone RDS |

### Deployment Tiers

**Key insight:** The shipping pipeline (CI/CD) and production topology (full-stack services) are different concerns. Not every environment needs every service.

| Tier | Name | Components | RDS Required | Environment |
| ---- | ---- | ---------- | ------------ | ----------- |
| 0 | Cluster Viability | EKS control plane, nodes, CNI, CoreDNS | No | All |
| 1 | Delivery Plane | ArgoCD, Kong, ExternalDNS, ESO, Cluster Autoscaler | No | All |
| 1.5 | Core Observability | Prometheus, Grafana (SQLite), Alertmanager | No | All |
| 2 | Platform Experience | Backstage, Loki (long-term), Grafana (PostgreSQL) | Yes | Dev+, optional ephemeral |
| 3 | Production Identity | Keycloak, OIDC federation, RBAC policies | Yes | Prod only |

**Tier Rationale:**

- **Tier 0-1**: Required for the cluster to function and deploy workloads. The "shipping pipeline".
- **Tier 1.5**: Core observability for debugging. No RDS required (Grafana uses SQLite, Prometheus uses local PV).
- **Tier 2**: Developer experience services. Backstage needs RDS, observability gets long-term storage.
- **Tier 3**: Production authentication. Keycloak is complex and adds friction to ephemeral testing.

**Tier Acceptance Criteria (Pass/Fail):**

| Tier | Pass Criteria | Fail Indicators |
| ---- | ------------- | --------------- |
| 0 | EKS API responds, nodes Ready, CoreDNS resolving | Node NotReady, CNI failures, API timeout |
| 1 | ArgoCD healthy, Kong accepting traffic, ESO syncing secrets | App-of-apps degraded, ingress 502/503, secrets missing |
| 1.5 | Prometheus scraping, Grafana UI loads, Alertmanager running | Metrics missing, dashboards 500, no alerts |
| 2 | Backstage UI loads, Grafana dashboards render, DB connections established | Pod CrashLoopBackOff, DB connection refused, UI 500 errors |
| 3 | Keycloak login works, OIDC tokens issued, RBAC policies enforced | Auth redirect loop, token validation failure, 403 on valid user |

**CI Validation by Tier:**

- **Ephemeral (Tier 0-1.5):** `kubectl get nodes` Ready, ArgoCD Healthy, Prometheus targets up
- **Nightly/On-demand (Tier 2-3):** Backstage health 200, Keycloak realm accessible

**V1 Rule:** Non-prod environments (dev, staging, ephemeral) can use simplified auth:

- **GitHub OAuth**: For Backstage developer login (already supported)
- **Static admin credentials**: For ArgoCD/Grafana in dev/test
- **No Keycloak**: Removes a heavy dependency from the fast feedback loop

**Why this matters:**

```text
Without tiers:
  Ephemeral cluster → needs RDS → needs Keycloak → takes 20 minutes → defeats purpose

With tiers:
  Ephemeral cluster → Tier 0-1.5 → deploys in 8 minutes → validates code + has observability
  Production cluster → Tier 0-3 → full identity federation
```

### ArgoCD as Tier Controller

**Simplified bootstrap:** Terraform only deploys EKS + ArgoCD. ArgoCD handles everything else.

```text
┌─────────────────────────────────────────────────────────────────┐
│  TERRAFORM (minimal)                                            │
│    1. Create EKS cluster                                        │
│    2. Deploy ArgoCD bootstrap app                               │
│    3. Pass context: { env, mode, maxTier, rdsAvailable }        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ARGOCD APP-OF-APPS (tier controller)                           │
│    Reads bootstrap values and deploys apps up to maxTier        │
│    Each app has label: goldenpath.idp/tier: "1.5"               │
│    Apps with tier > maxTier are skipped                         │
└─────────────────────────────────────────────────────────────────┘
```

**Bootstrap values passed to ArgoCD:**

```yaml
bootstrap:
  mode: ephemeral        # or persistent
  maxTier: "1.5"         # highest tier to deploy
  env: dev
  buildId: "26-01-23-01"

platform:
  rdsAvailable: false    # can Tier 2+ apps connect to RDS?
```

**App-of-apps tier selection logic:**

```yaml
{{- range .Values.apps }}
{{- if le (float64 .tier) (float64 $.Values.bootstrap.maxTier) }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {{ .name }}
  labels:
    goldenpath.idp/tier: "{{ .tier }}"
# ... app spec
{{- end }}
{{- end }}
```

**Why this simplifies everything:**

- No tier-specific bootstrap scripts
- No shell logic for conditional deployment
- ArgoCD is the single orchestrator
- Tier changes = just update Helm values
- GitOps-native: desired state in Git, ArgoCD reconciles

### Shared Services Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                    FOUNDATIONAL PLANE                           │
│                    (Persistent - long-lived)                    │
├─────────────────────────────────────────────────────────────────┤
│  RDS PostgreSQL (goldenpath-dev-platform-db) [Tier 2+]         │
│  Route53 Zone (dev.goldenpathidp.io) [Tier 1]                  │
│  Keycloak (keycloak.prod.goldenpathidp.io) [Tier 3 - Prod]     │
└─────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │ Database           │ DNS parent         │ Auth (prod)
    ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
    │Persistent│          │Ephemeral│          │Ephemeral│
    │ Cluster  │          │Cluster A│          │Cluster B│
    │(Tier 0-3)│          │(Tier 0-1.5)│       │(Tier 0-1.5)│
    │          │          │+ Observ. │         │+ Observ. │
    └──────────┘          └──────────┘         └──────────┘
    backstage.dev.        grafana.b-01.        grafana.b-02.
    goldenpathidp.io      dev.goldenpathidp.io dev.goldenpathidp.io
```

## Implementation

### Phase 1: DNS Contract Enforcement

1. Add `hostSuffix` to Helm values generation:
   ```yaml
   # Computed based on lifecycle
   hostSuffix: "{{ if eq .lifecycle 'ephemeral' }}b-{{ .buildId }}.{{ end }}{{ .env }}.goldenpathidp.io"
   ```

2. Update all charts to use:
   ```yaml
   ingress:
     hostname: "backstage.{{ .Values.hostSuffix }}"
   ```

3. Add CI gate to block ephemeral manifests requesting base DNS

### Phase 2: Bootstrap Mode

1. Add `bootstrap.mode` to cluster configuration
2. Conditional app deployment in app-of-apps:
   ```yaml
   {{- if eq .Values.bootstrap.mode "persistent" }}
   - name: keycloak
   {{- end }}
   ```

3. Configure ephemeral Backstage to use persistent Keycloak:
   ```yaml
   keycloak:
     baseUrl: "https://keycloak.{{ .env }}.goldenpathidp.io"  # Always persistent
   ```

### Phase 3: ExternalDNS Scoping

1. Configure `--txt-owner-id={{ buildId }}` for ephemeral clusters
2. Configure `--domain-filter` to restrict ephemeral to build-scoped subdomains

## TLS Considerations

| Cluster Type | Certificate Scope |
|--------------|-------------------|
| Persistent | `*.dev.goldenpathidp.io` (wildcard) |
| Ephemeral | Per-build cert via cert-manager |

Alternative: Use `*.builds.dev.goldenpathidp.io` zone so ephemeral can use a single wildcard.

## Consequences

### Positive

- Zero DNS collisions between clusters
- Clear ownership boundaries
- Keycloak remains single source of truth for identity
- Ephemeral clusters are truly disposable
- Cleanup is straightforward (delete build-scoped records)

### Tradeoffs

- More complex Helm values generation
- Ephemeral clusters cannot test Keycloak changes (acceptable tradeoff)
- Requires Keycloak wildcard redirect URIs

### Migration

- V1 clusters continue as-is (single cluster per environment)
- V2 introduces the contract when multi-cluster ephemeral is needed

## Alternatives Considered

1. **Separate hosted zones per cluster type**: Cleaner but adds zone management complexity
2. **ExternalDNS txt-owner-id only**: Prevents overwrites but doesn't solve naming collisions
3. **Disable DNS for ephemeral**: Simpler but reduces usability

## Roadmap

- **V1.1**: Document contract, add CI gate for hostname validation
- **V2.0**: Implement bootstrap mode differentiation
- **V2.1**: Full ExternalDNS scoping with txt-owner-id

## References

- ADR-0158: Standalone RDS as Bounded Context
- ADR-0175: ExternalDNS Wildcard Ownership
- ADR-0179: Dynamic Hostname Generation (implements this contract)
- DNS Ownership Contract discussion (2026-01-23)
