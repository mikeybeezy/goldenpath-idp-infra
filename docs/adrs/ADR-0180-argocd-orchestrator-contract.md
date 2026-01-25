<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0180-argocd-orchestrator-contract
title: 'ADR-0180: ArgoCD Orchestrator Contract'
type: adr
status: proposed
domain: platform-core
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 60.0
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
  - ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - V1_DETERMINISM_CRITERIA
supersedes: []
superseded_by: []
tags:
  - argocd
  - orchestration
  - bootstrap
  - tiers
  - v2
inheritance: {}
supported_until: 2028-01-23
version: '1.0'
breaking_change: false
---

# ADR-0180: ArgoCD Orchestrator Contract

- **Status:** Proposed (V2 Roadmap)
- **Date:** 2026-01-23
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Operations
- **Related:** ADR-0178 (DNS/Bootstrap Contract), ADR-0179 (Dynamic Hostnames)

---

## Context

V1 bootstrap uses shell scripts with conditional logic to deploy platform components. This approach has several problems:

1. **Complexity accumulates**: Each new condition adds shell logic
2. **No single orchestrator**: Multiple scripts coordinate via environment variables
3. **Tier boundaries are convention**: Nothing enforces which apps deploy at which tier
4. **Drift is invisible**: No reconciliation loop to detect/fix configuration drift

ADR-0178 introduced the Tier Architecture (0, 1, 1.5, 2, 3) and the concept of ArgoCD as Tier Controller. This ADR formalizes the contract ArgoCD must follow when orchestrating tier-based deployments.

---

## Decision

ArgoCD will be the **single orchestrator** for all platform components beyond the EKS cluster itself. Terraform's responsibility ends at deploying EKS + ArgoCD bootstrap. ArgoCD handles everything else.

### Scope

ArgoCD orchestrates **Tiers 1-3** only:

| Tier | Components | ArgoCD Responsibility |
| ---- | ---------- | --------------------- |
| 0 | EKS, nodes, CNI, CoreDNS | NOT ArgoCD (Terraform + EKS managed) |
| 1 | ArgoCD, Kong, ExternalDNS, ESO, Cluster Autoscaler | ArgoCD self-manages after bootstrap |
| 1.5 | Prometheus, Grafana (SQLite), Alertmanager | ArgoCD deploys (no RDS required) |
| 2 | Backstage, Loki, Grafana (PostgreSQL) | ArgoCD deploys IF `rdsAvailable: true` |
| 3 | Keycloak, OIDC federation | ArgoCD deploys IF `mode: persistent` AND `env: prod` |

### Bootstrap Values Contract

Terraform passes these values to ArgoCD at bootstrap:

```yaml
# ConfigMap: argocd-bootstrap-config
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-bootstrap-config
  namespace: argocd
data:
  bootstrap.yaml: |
    bootstrap:
      mode: ephemeral | persistent
      maxTier: "1.5"           # Highest tier to deploy
      env: dev | staging | prod
      buildId: "26-01-23-01"   # Only for ephemeral

    platform:
      rdsAvailable: false       # Can Tier 2+ apps connect to RDS?
      storageClassReady: false  # Is EBS CSI driver provisioning?
      irsaConfigured: false     # Are IRSA roles ready?

    dns:
      baseDomain: goldenpathidp.io
      hostSuffix: ""            # Computed: b-{buildId}.{env} or {env}
```

### Hostname Generation (ADR-0179 Integration)

The bootstrap values feed into ADR-0179's hostname generation chain:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│  ADR-0180 Bootstrap Config          ADR-0179 Propagation Chain          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  bootstrap.mode ─────────────────────► global.lifecycle                 │
│  bootstrap.buildId ──────────────────► global.buildId                   │
│  bootstrap.env ──────────────────────► env variable                     │
│                                                                         │
│  dns.hostSuffix ◄──── COMPUTED ──────┬ ephemeral: b-{buildId}.{env}.   │
│                                      └ persistent: {env}.               │
│                                                                         │
│  dns.hostSuffix ─────────────────────► global.hostSuffix (to charts)   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Variable Mapping:**

| ADR-0180 (Bootstrap) | ADR-0179 (Helm) | Used By |
| -------------------- | --------------- | ------- |
| `bootstrap.mode` | `global.lifecycle` | Tier gating, Keycloak skip |
| `bootstrap.buildId` | `global.buildId` | ExternalDNS owner-id |
| `dns.hostSuffix` | `global.hostSuffix` | All Ingress hostnames |
| (computed) | `global.dnsOwnerId` | ExternalDNS txt-owner-id |

**Hostname Computation Logic (in Terraform or ArgoCD):**

```yaml
{{- if eq .Values.bootstrap.mode "ephemeral" }}
dns:
  hostSuffix: "b-{{ .Values.bootstrap.buildId }}.{{ .Values.bootstrap.env }}.goldenpathidp.io"
  dnsOwnerId: "ephemeral-{{ .Values.bootstrap.buildId }}"
{{- else }}
dns:
  hostSuffix: "{{ .Values.bootstrap.env }}.goldenpathidp.io"
  dnsOwnerId: "persistent-{{ .Values.bootstrap.env }}"
{{- end }}
```

**Why This Matters:**

All ingress hostnames in ephemeral clusters will be scoped to the build:

```text
Ephemeral (buildId: 26-01-23-01):
  argocd.b-26-01-23-01.dev.goldenpathidp.io
  grafana.b-26-01-23-01.dev.goldenpathidp.io
  backstage.b-26-01-23-01.dev.goldenpathidp.io  (if Tier 2 enabled)

Persistent:
  argocd.dev.goldenpathidp.io
  grafana.dev.goldenpathidp.io
  backstage.dev.goldenpathidp.io
```

### Tier Deployment Rules

ArgoCD App-of-Apps uses these rules to determine which apps to deploy:

```yaml
# App-of-Apps tier selection logic
{{- range .Values.apps }}
{{- $tierFloat := float64 .tier }}
{{- $maxTierFloat := float64 $.Values.bootstrap.maxTier }}

{{- /* Rule 1: Tier must be <= maxTier */}}
{{- if le $tierFloat $maxTierFloat }}

{{- /* Rule 2: Tier 2+ requires RDS */}}
{{- if and (ge $tierFloat 2.0) (not $.Values.platform.rdsAvailable) }}
  {{- /* Skip: RDS not available */}}
{{- else if and (eq .name "keycloak") (ne $.Values.bootstrap.mode "persistent") }}
  {{- /* Skip: Keycloak only in persistent mode */}}
{{- else }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {{ .name }}
  labels:
    goldenpath.idp/tier: "{{ .tier }}"
    goldenpath.idp/mode: "{{ $.Values.bootstrap.mode }}"
spec:
  # ... app spec
{{- end }}
{{- end }}
{{- end }}
```

### Preflight Checks

Before ArgoCD advances to each tier, these conditions must be verified.

**Foundational Plane Checks (must pass before ANY tier):**

| Check | Validation Method | Failure Mode |
| ----- | ----------------- | ------------ |
| Foundational plane exists | PreSync Job: verify VPC, Route53 zone, Secrets Manager reachable | Block all deployments |
| ExternalDNS scoped correctly | PreSync Job: verify `--domain-filter` excludes base `*.{env}` for ephemeral | Block Tier 1 |
| IRSA roles configured | PreSync Job: verify IAM roles exist for ESO, ExternalDNS, ArgoCD | Block Tier 1 |

**Tier-Specific Checks:**

| Tier | Preflight Check | How ArgoCD Validates |
| ---- | --------------- | -------------------- |
| 1 | EKS API responding | ArgoCD itself is running (implicit) |
| 1 | Nodes Ready | Sync wave 0 deploys node-readiness Job |
| 1.5 | StorageClass exists | Prometheus app has PreSync hook: `kubectl get sc gp3` |
| 1.5 | PV can be provisioned | Alertmanager app waits for PVC bound |
| 2 | RDS endpoint reachable | Backstage app has PreSync hook: `nc -z $RDS_HOST 5432` |
| 2 | Secrets exist in Secrets Manager | ESO SecretStore status is Ready |
| 2 | S3/object storage available | Loki app has PreSync hook if long-term storage enabled |
| 3 | Keycloak realm accessible | OIDC app has PreSync hook: `curl keycloak/realms/goldenpath` |
| All | ClusterIssuers ready (if TLS required) | Certificate apps have PreSync hook: `kubectl get clusterissuer -o jsonpath='{.status.conditions}'` |

**Codex Attribution:** These preflight checks were synthesized from Codex review feedback (session capture 2026-01-23).

### External Secrets Ownership Note

`ClusterSecretStore` is managed by ArgoCD via `gitops/kustomize/bases/external-secrets/cluster-secret-store.yaml`.
Terraform should not apply it directly, because the CRD may not exist during apply and can fail nondeterministically.

### Sync Wave Order

ArgoCD deploys apps in sync wave order within each tier:

```yaml
# Tier 1 (Delivery Plane)
- name: external-secrets
  tier: "1"
  syncWave: "10"
- name: external-dns
  tier: "1"
  syncWave: "20"
- name: kong
  tier: "1"
  syncWave: "30"
- name: cluster-autoscaler
  tier: "1"
  syncWave: "40"

# Tier 1.5 (Core Observability)
- name: prometheus
  tier: "1.5"
  syncWave: "50"
- name: alertmanager
  tier: "1.5"
  syncWave: "51"
- name: grafana-sqlite
  tier: "1.5"
  syncWave: "52"

# Tier 2 (Platform Experience)
- name: backstage
  tier: "2"
  syncWave: "100"
- name: loki
  tier: "2"
  syncWave: "101"
- name: grafana-postgresql
  tier: "2"
  syncWave: "102"

# Tier 3 (Production Identity)
- name: keycloak
  tier: "3"
  syncWave: "200"
- name: oidc-config
  tier: "3"
  syncWave: "201"
```

### Mode vs MaxTier Precedence

When `bootstrap.mode` and `bootstrap.maxTier` conflict, these rules apply:

| Scenario | Mode | MaxTier | Result |
| -------- | ---- | ------- | ------ |
| Ephemeral CI | ephemeral | 1.5 | Deploy Tier 0-1.5 only |
| Ephemeral with Platform | ephemeral | 2 | Deploy Tier 0-2, skip Keycloak |
| Persistent Dev | persistent | 2 | Deploy Tier 0-2, skip Keycloak |
| Persistent Prod | persistent | 3 | Deploy Tier 0-3 (full stack) |

**Rule:** `maxTier` is the ceiling. `mode` further restricts within that ceiling (e.g., ephemeral never deploys Keycloak regardless of maxTier).

#### V1 Implementation: Derived MaxTier (No Independent Override)

In V1, `maxTier` is **computed from `lifecycle`** and cannot be independently overridden:

```hcl
# envs/dev/main.tf - V1 Implementation
max_tier = local.cluster_lifecycle == "ephemeral" ? "1.5" : "3"
```

**V1 Behavior:**

- `lifecycle=ephemeral` → `maxTier=1.5` (always, no override)
- `lifecycle=persistent` → `maxTier=3` (always, no override)

**Why This Matters:**

- No conflict is possible in V1 (mode and maxTier cannot disagree)
- Simplifies implementation (single source of truth: `lifecycle`)
- Explicit override support deferred to V2 if needed

**V2 Consideration:**

If independent `maxTier` override is needed (e.g., persistent dev with `maxTier=2` to skip Keycloak), add a `max_tier_override` variable with explicit precedence:

```hcl
# V2: Allow explicit override
max_tier = var.max_tier_override != "" ? var.max_tier_override : (
  local.cluster_lifecycle == "ephemeral" ? "1.5" : "3"
)
```

---

## Implementation

### Phase 1: App-of-Apps Refactor

1. Add `tier` label to all ArgoCD Application manifests
2. Add `syncWave` annotations for ordering
3. Update app-of-apps template with tier selection logic

### Phase 2: Preflight Hooks

1. Create PreSync hook Jobs for each tier transition
2. Hook Jobs check prerequisites (node readiness, RDS, secrets)
3. Hook failure blocks tier deployment

### Phase 3: Bootstrap ConfigMap

0. Terraform ensures the `argocd` namespace exists before ArgoCD Helm install (dependency ordering to avoid namespace races).
1. Terraform generates `argocd-bootstrap-config` ConfigMap
2. ArgoCD ApplicationSet or app-of-apps reads ConfigMap
3. Values control tier ceiling and feature flags

### Phase 4: Validation

1. Deploy ephemeral with `maxTier: 1.5`, verify no Tier 2 apps
2. Deploy persistent with `maxTier: 2`, verify Backstage + no Keycloak
3. Deploy prod with `maxTier: 3`, verify full stack

---

## Consequences

### Positive

- Single orchestrator (ArgoCD) instead of shell script coordination
- Tier boundaries enforced by ArgoCD logic, not convention
- GitOps-native: desired state in Git, ArgoCD reconciles
- Drift detection built-in (ArgoCD shows OutOfSync)
- Simplified Terraform: only EKS + ArgoCD bootstrap

### Tradeoffs

- ArgoCD becomes critical path (if ArgoCD fails, nothing deploys)
- PreSync hooks add deployment latency
- More complex app-of-apps template
- Debugging requires ArgoCD knowledge

### Risks

- **ArgoCD self-upgrade failure**: Mitigated by keeping ArgoCD in Tier 1 with careful sync waves
- **Circular dependency**: ArgoCD needs ESO for secrets, ESO is an ArgoCD app. Mitigated by bootstrap secrets in Terraform.

---

## Alternatives Considered

1. **Keep shell scripts with tiers**: Convention-based, no enforcement, complexity grows
2. **Helm umbrella chart**: Single chart deploys everything, but no GitOps reconciliation
3. **Flux CD**: Alternative GitOps tool, but ArgoCD already deployed and understood
4. **Terraform-only**: No GitOps, no drift detection, no reconciliation

---

## Validation Criteria

| Test | Expected Outcome |
| ---- | ---------------- |
| Ephemeral deploy with `maxTier: 1.5` | Tier 0-1.5 apps Healthy, no Tier 2+ apps exist |
| Ephemeral deploy with `maxTier: 2` | Backstage deployed, Keycloak NOT deployed |
| Persistent deploy with `maxTier: 3` | Full stack deployed, all apps Healthy |
| Delete RDS, redeploy | Tier 2 PreSync hook fails, Backstage not deployed |
| Node NotReady | Tier 1 PreSync hook fails, delivery plane blocked |

---

## Open Questions (from Codex Review)

These questions were raised during Codex review and require decisions:

| Question | Context | Proposed Resolution |
| -------- | ------- | ------------------- |
| IAM-level DNS restrictions? | ExternalDNS could still write to base zones if misconfigured | V2: Add IAM policy scoping to `*.b-{buildId}.{env}.*` for ephemeral roles |
| Single source of truth for gating? | `bootstrap.mode` vs `bootstrap.maxTier` can conflict | `maxTier` is ceiling, `mode` sets restrictions within ceiling (documented above) |
| Tier 2 S3 dependency? | Loki needs S3 for long-term storage | Add `platform.s3Available` flag, make Loki optional in Tier 2 |
| Tier 1.5 storage class guarantee? | Local PV needs EBS CSI driver | Add `platform.storageClassReady` flag to bootstrap config |
| `hostSuffix` vs `bootstrap.mode` mapping? | Different variable names for same concept | Standardize: `lifecycle` in Terraform → `mode` in bootstrap → `hostSuffix` computed |

---

## References

- ADR-0178: Ephemeral vs Persistent DNS Ownership and Bootstrap Contract
- ADR-0179: Dynamic Hostname Generation for Ephemeral Clusters
- V1_DETERMINISM_CRITERIA: Synthesized Claude + Codex Recommendations
- Session Capture 2026-01-23: Codex review feedback (lines 551-626)
- ArgoCD Sync Waves: <https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/>
- ArgoCD Resource Hooks: <https://argo-cd.readthedocs.io/en/stable/user-guide/resource_hooks/>
