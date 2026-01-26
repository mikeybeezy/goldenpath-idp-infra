---
id: 2026-01-23-v1-milestone-ephemeral-deploy-success
title: V1 Milestone - Ephemeral Deploy, DNS Architecture, and Governance Registry Fix
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0177-ci-iam-comprehensive-permissions
  - ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract
  - ADR-0179-dynamic-hostname-generation-ephemeral-clusters
  - RDS_USER_DB_PROVISIONING
  - 2026-01-23-ci-iam-permissions-fix
---
# Session Capture: V1 Milestone - Ephemeral Deploy Success

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-23
**Timestamp:** 2026-01-23T07:00:00Z
**Branch:** development (goldenpath-idp-infra)

## Scope

- Validate ephemeral cluster deployment as V1 milestone success
- Clarify RDS architecture and dependency chain
- Document standalone RDS deployment workflow
- Merge conflict resolution for PR #275

## Work Summary

### PR #275 Completed

- Resolved merge conflict in `session_summary/agent_session_summary.md`
- Added changelog entry CL-0166 for CI IAM permissions fix
- All 22 CI checks passed
- PR ready for human merge

### V1 Milestone Assessment

Confirmed ephemeral cluster deployment as **success** because:

| Component | Status | Notes |
|-----------|--------|-------|
| CI Pipeline | Working | Commit → Deploy functional |
| VPC/Subnets | Working | Persistent VPC exists |
| EKS cluster | Working | Control plane + nodes up |
| IRSA roles | Working | ESO, ExternalDNS, Autoscaler, ALB |
| ArgoCD | Working | App-of-apps deployed |
| Secrets | Working | Adopt-or-create pattern |
| Keycloak | Pending | Needs standalone RDS |
| Backstage | Pending | Needs standalone RDS |

### RDS Architecture Clarified

**Key insight:** Keycloak/Backstage not working is **expected** - they need standalone RDS deployed first.

**Dependency chain:**
```
1. Persistent VPC (exists)
2. Standalone RDS (envs/dev-rds/) - NEEDS DEPLOYMENT
3. Ephemeral clusters connect to existing RDS
```

**Two RDS workflows explained:**

| Workflow | Purpose | When to use |
|----------|---------|-------------|
| `rds-database-apply.yml` | Deploy RDS instance + pre-configured DBs | First-time setup |
| `create-rds-database.yml` | Add new database to existing RDS | Self-service for new apps |

### Secrets Flow Validated

```
RDS creates: goldenpath/dev/backstage/postgres
  └── { username, password, host, port, dbname }
          ↓
ExternalSecret pulls from Secrets Manager
          ↓
Backstage pod uses credentials
```

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Count as V1 success | Yes | Non-DB apps working, DB apps just need RDS |
| RDS deployment approach | Standalone first | ADR-0158 pattern - separate lifecycle |
| Documentation needed | No | Existing docs in RDS_USER_DB_PROVISIONING.md sufficient |

## Artifacts Touched

### Modified

- `session_summary/agent_session_summary.md` - Merged conflict, added sessions
- `docs/changelog/entries/CL-0166-ci-iam-comprehensive-permissions.md` - Created

### Validated

- `gitops/helm/backstage/values/dev.yaml` - ExternalSecret config correct
- `envs/dev-rds/terraform.tfvars` - Pre-configured with keycloak/backstage users
- `envs/dev-rds/main.tf` - Creates secrets with correct structure

## Current State / Follow-ups

**Immediate next step:**
```bash
gh workflow run rds-database-apply.yml -f environment=dev
```

This will:
1. Create RDS PostgreSQL instance
2. Create keycloak + backstage databases
3. Create secrets in Secrets Manager
4. Enable Keycloak/Backstage to connect

**After RDS deployed:**
- Keycloak and Backstage pods will auto-recover
- Full platform stack operational

**PR #275 status:** Ready for human merge

- URL: [PR #275](https://github.com/mikeybeezy/goldenpath-idp-infra/pull/275)

---

## Session Part 2: DNS Architecture and Governance Registry Fix

**Timestamp:** 2026-01-23T10:00:00Z

### ADR-0178 and ADR-0179 Created

Documented the DNS ownership contract for ephemeral vs persistent clusters:

| ADR      | Purpose                                                           | Status   |
|----------|-------------------------------------------------------------------|----------|
| ADR-0178 | Policy - DNS ownership contract and bootstrap mode differentiation | Proposed |
| ADR-0179 | Implementation - BuildId propagation chain for dynamic hostnames   | Proposed |

**Key architecture decision:**

- Persistent clusters own `*.{env}.goldenpathidp.io`
- Ephemeral clusters own `*.b-{buildId}.{env}.goldenpathidp.io`

**BuildId propagation chain (ADR-0179):**
```
CI workflow input → Terraform variable → Helm values → Ingress annotation → ExternalDNS
```

Roadmap items 094-097 added to track implementation.

### PR #276 Gate Fixes

Fixed CI gate failures on hotfix/rds-workflow-backend-config merge to main:

| Issue                                    | Fix                                             |
|------------------------------------------|-------------------------------------------------|
| markdownlint MD034 (bare URL)            | Wrapped URL in markdown link                    |
| emoji-enforcer (non-compliant checkmark) | Replaced checkmark with "DONE" text             |
| require-session-logs                     | Added session entry to agent_session_summary.md |

All 15 checks passed after fixes.

### Governance Registry Bug Investigation and Fix

**Problem:** User reported today's teardowns not appearing in governance-registry logs.

**Investigation findings:**

| Check | Result |
|-------|--------|
| GitHub Actions teardown runs | 4 runs today, 2 successful |
| Teardown logging step | Executed successfully, committed and pushed |
| governance-registry CSV | Only has data up to 2026-01-01 |

**Root cause identified:**

The `governance-registry-writer.yml` workflow was overwriting teardown timing records:

1. Teardown workflow appends row to `environments/development/latest/build_timings.csv`
2. Push to main/development triggers governance-registry-writer
3. Writer copies stale `docs/build-timings.csv` from source branch
4. Fresh teardown data overwritten with stale December 2025 data

**Fix applied (commit d0fcfc11):**

```yaml
# New step added before "Write latest + history"
- name: Preserve existing build_timings.csv
  run: |
    if [ -f "$LATEST_DIR/build_timings.csv" ]; then
      cp "$LATEST_DIR/build_timings.csv" /tmp/preserved_build_timings.csv
    fi

# After copying artifacts, restore preserved file
if [ -f /tmp/preserved_build_timings.csv ]; then
  cp /tmp/preserved_build_timings.csv "$LATEST_DIR/build_timings.csv"
  cp /tmp/preserved_build_timings.csv "$HIST_DIR/build_timings.csv"
fi
```

Also removed the stale copy from source branch that was causing the overwrite.

### Kyverno vs Datree Assessment

Evaluated policy enforcement options:

| Tool | Current State | Recommendation |
|------|---------------|----------------|
| Datree | Deployed as admission webhook but unconfigured (empty values) | Keep for now |
| Kyverno | Not deployed | V1.1/V2 candidate |

**Decision:** Defer Kyverno adoption to V1.1. Admission webhooks can brick clusters if misconfigured - not worth the risk for V1 stability.

## Artifacts Modified (Part 2)

| File | Change |
|------|--------|
| `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md` | Created |
| `docs/adrs/ADR-0179-dynamic-hostname-generation-ephemeral-clusters.md` | Created |
| `docs/adrs/01_adr_index.md` | Added ADR-0178, ADR-0179 |
| `docs/production-readiness-gates/ROADMAP.md` | Added items 094-097 |
| `.github/workflows/governance-registry-writer.yml` | Fixed CSV preservation bug |
| `session_summary/agent_session_summary.md` | Added session entry |

## Current State

| Item | Status |
|------|--------|
| PR #275 | Ready for human merge |
| PR #276 | Ready for human merge |
| Governance registry fix | Pushed to development |
| Next teardown | Will properly log to CSV |

---

## Session Part 3: Deployment Tiers and Product Thesis

**Timestamp:** 2026-01-23T14:00:00Z

### Product Thesis Discussion

Created `docs/00-foundations/product/PRODUCT_THESIS.md` as an honest assessment of the platform's current state and product potential.

**Key observations documented:**

| Claim | Reality |
| ----- | ------- |
| "AI traversability" | True - but works because of documentation discipline, not magic |
| "One person = team" | Partially true - amplifies output but can't replace senior judgment |
| "Vibe coding defense" | True for some classes - PR gates block obvious breaks |
| "Production ready" | Not yet - RDS not deployed, no TLS, Datree unconfigured |

**Honest differentiation:** The only potentially unique aspects are AI-first governance, ADRs as first-class citizens, and session memory patterns. But these are patterns, not products.

### Deployment Tiers Architecture

User insight: We're conflating the shipping pipeline (CI/CD validation) with production topology (full identity stack). This creates unnecessary friction for ephemeral clusters.

**Tiers added to ADR-0178:**

| Tier | Name | Components | RDS Required | Environments |
| ---- | ---- | ---------- | ------------ | ------------ |
| 0 | Cluster Viability | EKS, nodes, CNI, CoreDNS | No | All |
| 1 | Delivery Plane | ArgoCD, Kong, ExternalDNS, ESO | No | All |
| 2 | Platform Experience | Backstage, Grafana, Prometheus | Yes | Dev+, optional ephemeral |
| 3 | Production Identity | Keycloak, OIDC, RBAC | Yes | Prod only |

**V1 Rule:** Non-prod can use simplified auth (GitHub OAuth, static admin). Keycloak is a production concern, not a dev/test prerequisite.

**Impact:**

```text
Without tiers: Ephemeral → RDS → Keycloak → 20 minutes → defeats purpose
With tiers:    Ephemeral → Tier 0+1 → 8 minutes → validates code works
```

### TLS/cert-manager Assessment

Investigated TLS infrastructure:

| Component | Status | Gap |
| --------- | ------ | --- |
| cert-manager Helm chart | Deployed via ArgoCD | None |
| ClusterIssuers (selfsigned, letsencrypt-staging, letsencrypt-prod) | Defined in kustomize | NOT deployed - no ArgoCD app |
| TLS on ingresses | Annotations present | Will fail without ClusterIssuers |

**Next step:** Create ArgoCD app to deploy ClusterIssuers, or add to kustomize base deployment.

## Artifacts Modified (Part 3)

| File | Change |
| ---- | ------ |
| `docs/00-foundations/product/PRODUCT_THESIS.md` | Created - honest product assessment |
| `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md` | Added deployment tiers section |

## Part 3 Status

| Item | Status |
| ---- | ------ |
| ADR-0178 | Updated with deployment tiers |
| Product thesis | Documented honestly |
| ClusterIssuers gap | Identified, not fixed (V1.1) |
| Ready for Codex review | Yes |

---

## Codex Review Brief

### V1 Status Summary

**V1 Milestone:** Ephemeral cluster deployment working (Tier 0-1). DB-dependent apps (Tier 2-3) blocked on RDS deployment.

### Key Architecture Decisions Made Today

| ADR | Decision | Status |
| --- | -------- | ------ |
| ADR-0178 | DNS Ownership Contract - ephemeral clusters get `*.b-{buildId}.{env}.` namespace | Proposed |
| ADR-0178 | Deployment Tiers (0-3) - separate shipping pipeline from production topology | Proposed |
| ADR-0179 | BuildId propagation chain - CI to Terraform to Helm to Ingress to ExternalDNS | Proposed |

### Tiers Overview

- **Tier 0-1:** Cluster viability + delivery plane (no RDS, all environments)
- **Tier 2:** Platform experience - Backstage, Grafana (RDS required, dev+)
- **Tier 3:** Production identity - Keycloak (prod only, not a dev prerequisite)

### Identified Gaps

| Gap | Impact | Priority |
| --- | ------ | -------- |
| ClusterIssuers not deployed | TLS will fail | V1.1 |
| RDS not deployed | Keycloak/Backstage blocked | Immediate |
| Datree unconfigured | No runtime policy enforcement | V1.1 |
| CI IAM permissions gap | `iam:CreatePolicy` needed for ESO/ExternalDNS | Plan exists |

### Open Questions for Review

1. **Is the tiered deployment model the right abstraction?** Or is there a simpler way to express "ephemeral doesn't need Keycloak"?

2. **Should ClusterIssuers be in Helm or Kustomize?** Currently in kustomize but no ArgoCD app deploys them.

3. **Is GitHub OAuth sufficient for non-prod Backstage auth?** Or should we still use Keycloak for dev to catch integration issues early?

4. **Bootstrap mode in app-of-apps:** Best way to conditionally exclude Tier 3 apps based on `bootstrap.mode`?

5. **TLS strategy for ephemeral:** Per-build certs vs wildcard on `*.builds.{env}.` subdomain?

## Codex Feedback: V1 Determinism Recommendations

### Goal
Create a stable, coherent, deterministic platform where "success" is repeatable.

### Recommendations

| Area | Recommendation | Why it matters |
|------|----------------|----------------|
| Tier definitions | Add explicit pass/fail criteria for Tier 0/1 and a minimal Tier 2/3 validation path | Removes ambiguity in "V1 success" and makes outcomes repeatable |
| Validation coverage | Keep ephemeral runs fast, but add nightly or on-demand Tier 2/3 checks | Prevents DB/auth regressions from hiding behind Tier 0/1 green runs |
| Dependency contracts | Document RDS networking + IAM prerequisites as a versioned contract | Avoids drift and broken dependencies |
| Version pinning | Freeze EKS add-on versions, Helm charts, and image tags for V1 | Deterministic inputs lead to deterministic outcomes |
| Environment gating | Enforce tier usage by policy (not convention) | Prevents accidental Tier 2/3 workloads in ephemeral runs |
| Readiness gates | Tie TLS/ClusterIssuer and auth requirements to tier gates | Clarifies what "ready" means for each tier |

### Suggested next steps

1. Define Tier 0/1 acceptance criteria in ADR-0178 and CI checks.
2. Add a lightweight Tier 2/3 validation workflow (nightly or manual).
3. Publish an RDS connectivity checklist (SGs, subnets, IAM, secrets).

---

## Response to Codex Feedback

**Timestamp:** 2026-01-23T15:00:00Z

### Actions Taken

| Recommendation | Status | Action |
| -------------- | ------ | ------ |
| Tier pass/fail criteria | DONE | Added to ADR-0178 with explicit pass/fail table |
| CI validation by tier | DONE | Added ephemeral (Tier 0-1) and nightly (Tier 2-3) checks to ADR |
| Nightly Tier 2/3 validation | TODO | Add to roadmap as V1.1 item |
| RDS dependency contract | PARTIAL | Exists in ADR-0158, needs versioned checklist |
| Version pinning | IN PLACE | Already doing, needs enforcement policy |
| Environment gating by policy | TODO | Requires Kyverno/OPA - V1.1 scope |
| Readiness gates tied to tiers | DONE | Captured in acceptance criteria table |

### ADR-0178 Updates

Added two new sections:

1. **Tier Acceptance Criteria (Pass/Fail)** - Explicit success/failure indicators for each tier
2. **CI Validation by Tier** - What to check in ephemeral vs nightly runs

### Remaining Gaps (V1.1 scope)

| Gap | Why deferred |
| --- | ------------ |
| Policy-based tier enforcement | Needs Kyverno - too risky for V1 |
| Nightly Tier 2/3 workflow | RDS not deployed yet - no point validating |
| RDS connectivity checklist | Document after first successful RDS deploy |

### Assessment

Codex feedback is valid and actionable. The key insight - "determinism requires explicit criteria" - is now addressed in ADR-0178. The remaining items are correctly scoped to V1.1 (after RDS is working).

---

## Synthesized Implementation Plan

**Timestamp:** 2026-01-23T15:30:00Z

Created `docs/00-foundations/product/V1_DETERMINISM_CRITERIA.md` - unified Claude + Codex recommendations.

### Unified Thesis

Deterministic V1 = Explicit Criteria + Tiered Validation + Enforced Boundaries

### Foundational vs Disposable Planes

**Core constraint: Ephemeral cannot exist without Persistent.**

| Plane | Contains | Lifecycle |
| ----- | -------- | --------- |
| Foundational (Persistent) | VPC, RDS, Route53, Secrets Manager, ECR, IAM | Long-lived |
| Disposable (Ephemeral) | EKS cluster, ArgoCD, Kong, workloads | Short-lived |

**Dependency chain:** Foundational MUST deploy first. Disposable CONSUMES foundational, never creates it.

Updated in both ADR-0178 and V1_DETERMINISM_CRITERIA.md.

### Implementation Phases

| Phase | Scope | Target | Blocker |
| ----- | ----- | ------ | ------- |
| 1 | Tier 0-1 CI validation + version pinning | Immediate | None |
| 2 | RDS deployment + Tier 2 connectivity | After Phase 1 | IAM permissions |
| 3 | TLS + ClusterIssuers | V1.1 | None |
| 4 | Kyverno policy enforcement | V1.1 | Risk assessment |
| 5 | Nightly Tier 2/3 validation | V1.1 | RDS working |

### Key Artifacts to Create

| Artifact | Purpose |
| -------- | ------- |
| `.github/workflows/tier-validation.yml` | CI smoke tests for Tier 0-1 |
| `docs/VERSION_MANIFEST.md` | Frozen versions for V1 |
| `docs/RDS_CONNECTIVITY_CONTRACT.md` | Versioned dependency contract |
| `gitops/argocd/apps/dev/cert-manager-issuers.yaml` | Deploy ClusterIssuers |

### V1 Complete Criteria

- 3 consecutive ephemeral deploys pass Tier 0-1 checks
- Backstage pod connects to RDS, UI returns 200
- All versions pinned and documented

---

## Session Part 4: Observability Tier and Simplified Bootstrap

**Timestamp:** 2026-01-23T16:00:00Z

### Observability Concern Identified

User identified a gap: How do you debug Tier 0-1 failures if observability (Grafana, Prometheus) is in Tier 2 which requires RDS?

**Resolution:** Split observability into two modes:

| Tier | Observability Mode | Storage | Use Case |
| ---- | ------------------ | ------- | -------- |
| 1.5 | Core Observability | Prometheus local PV, Grafana SQLite | Debug current cluster, no history |
| 2 | Full Observability | Grafana PostgreSQL, Loki S3 | Long-term retention, cross-cluster |

**Updated tier table:**

| Tier | Name | Components | RDS Required |
| ---- | ---- | ---------- | ------------ |
| 0 | Cluster Viability | EKS, nodes, CNI, CoreDNS | No |
| 1 | Delivery Plane | ArgoCD, Kong, ExternalDNS, ESO | No |
| 1.5 | Core Observability | Prometheus, Grafana (SQLite), Alertmanager | No |
| 2 | Platform Experience | Backstage, Loki, Grafana (PostgreSQL) | Yes |
| 3 | Production Identity | Keycloak, OIDC, RBAC | Yes |

### Simplified Bootstrap Model

User insight: Bootstrap can be simplified to just deploy ArgoCD. ArgoCD handles everything else based on context.

**New model:**

```text
TERRAFORM = Deploy EKS + ArgoCD (minimal)
ARGOCD = Deploy everything else based on tier selection
```

**ArgoCD as tier controller:**

- Each app gets a tier label: `goldenpath.idp/tier: "1.5"`
- App-of-apps reads `bootstrap.maxTier` from values
- Apps with tier > maxTier are skipped
- No tier-specific scripts needed

**Bootstrap values:**

```yaml
bootstrap:
  mode: ephemeral
  maxTier: "1.5"
  env: dev
  buildId: "26-01-23-01"
platform:
  rdsAvailable: false
```

### Why This Matters

- Ephemeral clusters now get observability (Tier 1.5) without needing RDS
- Bootstrap is GitOps-native (ArgoCD controls tiers, not shell scripts)
- Tier changes = just update Helm values

## Artifacts Modified (Part 4)

| File | Change |
| ---- | ------ |
| `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md` | Added Tier 1.5, ArgoCD as tier controller section |

## Part 4 Status

| Item | Status |
| ---- | ------ |
| Tier 1.5 observability | Added to ADR-0178 |
| ArgoCD tier controller | Documented in ADR-0178 |
| Simplified bootstrap model | Captured |

Signed: Claude Opus 4.5 (2026-01-23T16:00:00Z)

---

## Addendum: ArgoCD Orchestrator Contract Draft

### Screenoutput 1 (Exact)

**Findings**
- High: DNS ownership is declared but enforcement relies on CI and ExternalDNS config; there’s no IAM/zone-level guardrail, so a misconfigured ephemeral cluster could still write to base `*.{env}` records. `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:103` `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:275` `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:293`
- Medium: The “foundational must exist first” rule isn’t enforced in the simplified bootstrap model, so ephemeral runs can proceed without the required foundational plane and fail nondeterministically. `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:85` `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:180` `session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success.md:499`
- Medium: Two gating mechanisms (`bootstrap.mode` and `bootstrap.maxTier`) are used without precedence, which can produce inconsistent app selection (e.g., Keycloak gated by mode while tier gating says otherwise). `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:112` `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:199` `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:277` `session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success.md:517`
- Medium: Tier 2 is labeled “RDS required,” but includes Loki long‑term storage (S3) and Grafana PostgreSQL; missing explicit object‑storage dependency makes readiness checks incomplete. `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:131` `session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success.md:489`
- Medium: Tier 1.5 observability depends on local PV + Grafana SQLite, but storage class/PV prerequisites aren’t called out, which can break determinism on fresh clusters. `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:135` `session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success.md:482`
- Low: `hostSuffix` uses `.lifecycle` while bootstrap config uses `bootstrap.mode`; without a defined mapping, DNS scopes can drift. `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:114` `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md:263`

Open questions / assumptions
- Do you want IAM-level restrictions for ExternalDNS to hard‑block writes to base zones?
- Should `bootstrap.mode` or `bootstrap.maxTier` be the single source of truth, or do you want explicit precedence?
- Should Tier 2 list S3/object‑storage as a first‑class dependency, and be gated on its availability?
- What storage class guarantee should Tier 1.5 assume for local PVs?

Change summary: No changes made.

### Screenoutput 2 (Exact)

ArgoCD as the single orchestrator is strong for determinism and coherence, but only if you enforce a few guardrails.

What’s good:
- One reconciliation engine, one desired‑state source → fewer hidden side effects.
- Tier gating becomes declarative and testable (values → apps rendered).
- Easier rollback and drift detection.

Risks to watch:
- Bootstrap dependency on ArgoCD means if it’s unhealthy, everything stalls.
- Cross‑cutting prerequisites (RDS, DNS, IAM) still sit outside ArgoCD and need explicit contracts.
- Gating logic can get messy if you mix `bootstrap.mode` + `maxTier` without precedence.

Recommendation:
- Keep ArgoCD as the single orchestrator for app deploys, but formalize the “foundational plane” prerequisites and enforce them before ArgoCD runs.
- Make `bootstrap.maxTier` the single source of truth; use `bootstrap.mode` only to set defaults.
- Add a minimal “preflight” check that validates RDS/DNS/IAM readiness before ArgoCD advances tiers.

If you want, I can draft a short “ArgoCD Orchestrator Contract” section and propose the preflight checks.

### Questions

- Do you want IAM-level restrictions for ExternalDNS to hard-block writes to base zones?
- Should `bootstrap.mode` or `bootstrap.maxTier` be the single source of truth, or do you want explicit precedence?
- Should Tier 2 list S3/object-storage as a first-class dependency, and be gated on its availability?
- What storage class guarantee should Tier 1.5 assume for local PVs?

### Recommendations

- Keep ArgoCD as the single orchestrator for app deploys, but formalize the foundational plane prerequisites and enforce them before ArgoCD runs.
- Make `bootstrap.maxTier` the single source of truth; use `bootstrap.mode` only to set defaults.
- Add a minimal preflight check that validates RDS/DNS/IAM readiness before ArgoCD advances tiers.

### ArgoCD Orchestrator Contract

**Scope:** Terraform boots EKS + ArgoCD only. ArgoCD is the single orchestrator for app deployments and tier gating.

**Inputs (required):**
- `bootstrap.mode` (ephemeral|persistent)
- `bootstrap.maxTier` (float-like string)
- `bootstrap.env`, `bootstrap.buildId`
- `platform.rdsAvailable`

**Rules:**
- Tier selection is driven by `bootstrap.maxTier`. `bootstrap.mode` sets defaults only.
- Apps must declare `goldenpath.idp/tier`; apps with tier > `maxTier` are skipped.
- Ephemeral DNS scope is build-scoped only; base `*.{env}` is forbidden.

**Preflight checks (must pass before ArgoCD advances tiers):**
1. Foundational plane exists (VPC, Route53 zone, Secrets Manager) and is reachable from the cluster.
2. ExternalDNS is scoped to build-specific subdomains and cannot write to base `*.{env}` records.
3. Required IRSA roles and IAM policies exist for ESO/ExternalDNS/ArgoCD.
4. If `maxTier` >= 1.5, a default storage class exists for local PVs.
5. If `maxTier` >= 2, RDS endpoint is reachable and secrets are present.
6. If TLS is required for the selected tier, ClusterIssuers are installed and ready.

---

## Part 5: ADR-0180 ArgoCD Orchestrator Contract

**Time:** 2026-01-23 (continued session)

### Decision

Created [ADR-0180-argocd-orchestrator-contract.md](../docs/adrs/ADR-0180-argocd-orchestrator-contract.md) to formalize the ArgoCD Orchestrator Contract as a standalone ADR.

### Key Content

**Scope:** ArgoCD orchestrates Tiers 1-3. Terraform only deploys EKS + ArgoCD bootstrap.

**Bootstrap Values Contract:**

```yaml
bootstrap:
  mode: ephemeral | persistent
  maxTier: "1.5"
  env: dev | staging | prod
  buildId: "26-01-23-01"

platform:
  rdsAvailable: false
  storageClassReady: false
  irsaConfigured: false
```

**Tier Deployment Rules:**

- Tier must be <= maxTier
- Tier 2+ requires RDS
- Keycloak only in persistent mode

**Preflight Checks:**

| Tier | Preflight Check | How ArgoCD Validates |
| ---- | --------------- | -------------------- |
| 1 | EKS API responding | ArgoCD itself is running (implicit) |
| 1 | Nodes Ready | Sync wave 0 deploys node-readiness Job |
| 1.5 | StorageClass exists | Prometheus app has PreSync hook |
| 2 | RDS endpoint reachable | Backstage app has PreSync hook |
| 3 | Keycloak realm accessible | OIDC app has PreSync hook |

**Sync Wave Order:**

- Tier 1: external-secrets (10), external-dns (20), kong (30), cluster-autoscaler (40)
- Tier 1.5: prometheus (50), alertmanager (51), grafana-sqlite (52)
- Tier 2: backstage (100), loki (101), grafana-postgresql (102)
- Tier 3: keycloak (200), oidc-config (201)

**Mode vs MaxTier Precedence:**

- `maxTier` is the ceiling
- `mode` further restricts within that ceiling (ephemeral never deploys Keycloak)

### Files Created/Updated

| File | Action |
| ---- | ------ |
| `docs/adrs/ADR-0180-argocd-orchestrator-contract.md` | Created |
| `docs/adrs/01_adr_index.md` | Updated (added ADR-0180) |
| `docs/adrs/ADR-0178-ephemeral-persistent-dns-and-bootstrap-contract.md` | Updated (relates_to) |

### Part 5 Status

ADR-0180 formalizes the "breakthrough" architecture where:

1. Terraform responsibility ends at EKS + ArgoCD
2. ArgoCD is the single orchestrator for everything else
3. Tier boundaries are enforced by ArgoCD logic, not convention
4. Preflight checks validate prerequisites before tier advancement

This completes the V2 architecture documentation for tiered, GitOps-native deployments.

### Codex Feedback Incorporation

After review, ADR-0180 was updated to fully incorporate Codex's contract draft (lines 605-626 above):

**Added Foundational Plane Checks:**

- Foundational plane exists (VPC, Route53, Secrets Manager)
- ExternalDNS scoped to build-specific subdomains
- IRSA roles configured

**Added Missing Tier Checks:**

- S3/object storage for Loki (Tier 2)
- ClusterIssuers ready for TLS (all tiers)

**Added Open Questions Section:**

| Question | Proposed Resolution |
| -------- | ------------------- |
| IAM-level DNS restrictions | V2: IAM policy scoping for ephemeral roles |
| Single source of truth | `maxTier` is ceiling, `mode` sets restrictions |
| Tier 2 S3 dependency | Add `platform.s3Available` flag |
| Tier 1.5 storage class | Add `platform.storageClassReady` flag |
| `hostSuffix` vs `mode` mapping | Standardize variable naming |

**Attribution:** Added explicit Codex attribution in ADR-0180 preflight checks section.

### ADR-0179 Integration

Added explicit connection between ADR-0180 bootstrap values and ADR-0179 hostname generation:

**Variable Mapping:**

| ADR-0180 (Bootstrap) | ADR-0179 (Helm) | Used By |
| -------------------- | --------------- | ------- |
| `bootstrap.mode` | `global.lifecycle` | Tier gating |
| `bootstrap.buildId` | `global.buildId` | ExternalDNS owner-id |
| `dns.hostSuffix` | `global.hostSuffix` | All Ingress hostnames |

**Flow:**

```text
bootstrap.mode=ephemeral + bootstrap.buildId=26-01-23-01
    ↓
dns.hostSuffix = b-26-01-23-01.dev.goldenpathidp.io
    ↓
All ingresses: argocd.b-26-01-23-01.dev.goldenpathidp.io
```

This ensures the ArgoCD orchestrator contract (ADR-0180) explicitly references how buildId propagates to hostnames (ADR-0179).

---

## Feedback: IMPL-0001 Tiered Bootstrap and Hostname Generation

**Summary:** Solid phase breakdown, but a few gates conflict with tier intent and some checks are too brittle for determinism.

**Key issues**
- Phase 0 prerequisites require RDS/Secrets/ClusterIssuers, which blocks Tier 0-1.5 runs; needs tier-scoped gating. `docs/00-foundations/product/IMPL-0001-tiered-bootstrap-and-hostname-generation.md:21`
- Tier selection mixes `bootstrap.maxTier` and `bootstrap.mode` without precedence, risking inconsistent app inclusion (e.g., Keycloak). `docs/00-foundations/product/IMPL-0001-tiered-bootstrap-and-hostname-generation.md:85`
- ExternalDNS scoping is hardcoded to `b-{buildId}.{env}` while hostname generation is `global.hostSuffix`; potential drift if hostname strategy changes. `docs/00-foundations/product/IMPL-0001-tiered-bootstrap-and-hostname-generation.md:100`
- Phase 1 "no hardcoded hostnames" uses a simple `grep goldenpathidp.io`, which will be noisy and miss non-matching hardcodes. `docs/00-foundations/product/IMPL-0001-tiered-bootstrap-and-hostname-generation.md:39`
- Preflight checks are deferred to V2.1, leaving V1 with late failures and nondeterministic outcomes. `docs/00-foundations/product/IMPL-0001-tiered-bootstrap-and-hostname-generation.md:111`

**Questions**
- Should Phase 0 be split by tier so Tier 0-1.5 does not require RDS/ClusterIssuers?
- Is `bootstrap.maxTier` intended as the single gating input, with `bootstrap.mode` only setting defaults?
- Should ExternalDNS domain filters derive from `global.hostSuffix` to avoid drift?
- Do we want a V1 stopgap preflight gate (CI or ArgoCD PreSync) before V2.1?

---

## Implementation: IMPL-0001 Tiered Bootstrap (Response to Codex Review)

**Date:** 2026-01-23 (continued session)

Based on Codex feedback above, the following implementation work was completed:

### Phase 0 Split (Issue #1 - Tier-scoped gating)

IMPL-0001 updated to split Phase 0:

- **Phase 0a (Tier 0-1.5):** VPC, Route53 zone, IRSA roles only
- **Phase 0b (Tier 2+):** RDS, Secrets Manager, ClusterIssuers

This allows ephemeral Tier 0-1.5 deployments without RDS prerequisites.

### Mode vs MaxTier Precedence (Issue #2)

**Resolution:** In V1, `maxTier` is **derived from `lifecycle`** and cannot be independently overridden:

```hcl
# envs/dev/main.tf
max_tier = local.cluster_lifecycle == "ephemeral" ? "1.5" : "3"
```

- `lifecycle=ephemeral` → `maxTier=1.5` (always, no override)
- `lifecycle=persistent` → `maxTier=3` (always, no override)

This eliminates conflict - mode and maxTier cannot disagree in V1. Documented in ADR-0180 section "V1 Implementation: Derived MaxTier".

### Files Modified

| File | Change |
| ---- | ------ |
| `docs/00-foundations/product/IMPL-0001-tiered-bootstrap-and-hostname-generation.md` | Split Phase 0 into 0a/0b |
| `backstage-helm/charts/backstage/values.yaml` | Added `global.hostSuffix` |
| `backstage-helm/charts/backstage/templates/ingress.yaml` | Compute hostname from `global.hostSuffix` |
| `backstage-helm/charts/backstage/templates/configmap.yaml` | Compute BASE_URL from `global.hostSuffix` |
| `gitops/helm/backstage/values/dev.yaml` | Set `global.hostSuffix: dev.goldenpathidp.io` |
| `gitops/helm/kong/values/dev.yaml` | Added global.hostSuffix documentation |
| `gitops/helm/external-dns/values/dev.yaml` | Updated domainFilters to env-scoped |
| `envs/dev/main.tf` | Added `host_suffix`, `dns_owner_id` locals + bootstrap ConfigMap |
| `envs/dev/outputs.tf` | Added bootstrap outputs |
| `modules/kubernetes_addons/variables.tf` | Added `bootstrap_values` variable |
| `modules/kubernetes_addons/main.tf` | Inject hostSuffix into backstage/external-dns Apps |
| `docs/adrs/ADR-0180-argocd-orchestrator-contract.md` | Documented V1 maxTier derivation |

### Computed Values (Ephemeral build_id: 23-01-26-01)

```text
host_suffix:  b-23-01-26-01.dev.goldenpathidp.io
dns_owner_id: goldenpath-dev-23-01-26-01
```

### Remaining Issues (Deferred)

- **Issue #4 (grep noisy):** Accepted as-is for V1; manual verification sufficient
- **Issue #5 (Preflight deferred to V2.1):** See preflight strategy below

---

## Preflight Strategy: Codex Proposal and Claude Recommendation

**Timestamp:** 2026-01-23T17:00:00Z

### Codex V1-Ready Tier-Aware Preflight Proposal

Codex proposed advancing preflight checks from V2.1 to V1 with the following approach:

**Proposed Implementation:**

```yaml
# PreSync hook for Tier 2 apps
apiVersion: batch/v1
kind: Job
metadata:
  name: tier2-preflight
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: check
          image: bitnami/kubectl
          command:
            - /bin/sh
            - -c
            - |
              # Check RDS reachable
              nc -z $RDS_HOST 5432 || exit 1
              # Check secrets exist
              kubectl get externalsecret backstage-db -n backstage || exit 1
      restartPolicy: Never
```

**Per-Tier Checks Proposed:**

| Tier | Check | Implementation |
| ---- | ----- | -------------- |
| 1 | Nodes ready | PreSync Job: `kubectl get nodes -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'` |
| 1.5 | StorageClass exists | PreSync Job: `kubectl get sc gp3` |
| 2 | RDS reachable | PreSync Job: `nc -z $RDS_HOST 5432` |
| 2 | Secrets exist | PreSync Job: `kubectl get externalsecret` status check |
| 3 | Keycloak realm | PreSync Job: `curl keycloak/realms/goldenpath` |

### Claude Analysis: IMPL-0001 Phase 7 vs Codex Proposal

Comparison of approaches:

| Aspect | IMPL-0001 Phase 7 | Codex Proposal |
| ------ | ----------------- | -------------- |
| Timing | Deferred to V2.1 | V1 ready |
| Implementation | ArgoCD PreSync hooks | ArgoCD PreSync hooks |
| Complexity | Full tier-aware | Same |
| Risk | Lower (more runway) | Higher (new failure mode) |

**Assessment:**

The Codex proposal is technically sound, but introduces new failure modes at V1 launch. PreSync hooks that fail will block app deployment, which is the intended behavior - but debugging failures requires ArgoCD knowledge that may not be present.

**Key Trade-offs:**

| Pro | Con |
| --- | --- |
| Early failure (before app starts) | New debugging surface |
| Explicit prerequisite checks | Can mask root cause (why is RDS unreachable?) |
| Self-documenting dependencies | Adds deployment latency |
| Deterministic outcomes | Job failures need monitoring |

### Claude Recommendation: Phased Preflight Strategy

**V1 (Immediate):** Use Terraform data sources + CI workflow checks

```hcl
# V1: Terraform data source validation
data "aws_db_instance" "rds" {
  count = local.cluster_lifecycle == "persistent" ? 1 : 0
  db_instance_identifier = "goldenpath-${local.environment}"
}

# Fails terraform plan if RDS doesn't exist (for persistent)
```

```yaml
# V1: CI workflow preflight
- name: Preflight Check
  run: |
    if [[ "${{ inputs.lifecycle }}" == "persistent" ]]; then
      aws rds describe-db-instances \
        --db-instance-identifier goldenpath-${{ inputs.environment }} \
        || { echo "RDS not found - deploy RDS first"; exit 1; }
    fi
```

**V2 (After V1 Stable):** Add ArgoCD PreSync hooks

- Deploy PreSync hooks once V1 is stable
- Hooks provide in-cluster visibility (ArgoCD UI shows preflight status)
- Better debugging UX for platform operators

### Why This Approach

| Aspect | V1 (Terraform/CI) | V2 (ArgoCD PreSync) |
| ------ | ----------------- | ------------------- |
| Failure visibility | CI logs, Terraform output | ArgoCD UI + Events |
| Debugging surface | Familiar (AWS CLI, Terraform) | Requires ArgoCD knowledge |
| Implementation | Already exists | New code needed |
| Risk | Low (known patterns) | Medium (new failure mode) |

V1 needs stability. Terraform data sources and CI checks provide early failure without adding new debugging surface. ArgoCD PreSync hooks are the right V2 pattern once operators are comfortable with ArgoCD troubleshooting.

### Preflight Strategy Decision

Adopting phased preflight strategy:

1. **V1:** Terraform data source validation + CI workflow preflight checks
2. **V2:** ArgoCD PreSync hooks with full tier-aware validation

This aligns with the principle: "Don't add complexity at launch; add it when you understand the failure modes."

---

Signed: Claude Opus 4.5 (2026-01-23T17:00:00Z)

---

## Addendum: Verbatim Chat Outputs + Push Back

**User push back (verbatim):**
- you'r staring to introduc  more complexity or are you not
- so what do you propose

**Assistant output 1 (verbatim):**
```
Here’s the clearer framing:

Persistent clusters are foundational, **but not every foundational dependency is required for every tier**.
Tier 0–1.5 explicitly says “no RDS required,” so making **RDS/ClusterIssuers mandatory in Phase 0** forces a Tier 2/3 dependency onto Tier 0–1.5 runs. That’s the conflict.

**Better split:**
- **Phase 0A (Foundational core)**: VPC/subnets, Route53 zone, IAM/IRSA for ESO/ExternalDNS → required for *all* tiers.
- **Phase 0B (Tier 2/3 prerequisites)**: RDS, ClusterIssuers, object storage → required only if `maxTier >= 2` or TLS is in scope.

So persistent clusters are still the foundation, **but the foundation is tier‑scoped**, not a blanket gate.
```

**Assistant output 2 (verbatim):**
```
It’s not adding complexity to the system — it’s **making the existing complexity explicit and scoped** so it behaves deterministically.

Right now the complexity exists but is implicit (tiers say “no RDS,” Phase 0 says “RDS required”). The split just makes the rules consistent, so lower tiers don’t inherit higher‑tier dependencies.
```

**Assistant output 3 (verbatim):**
```
Here’s the minimal proposal to keep determinism without adding real complexity:

- Split Phase 0 into **Core Foundation** (always) vs **Tier 2/3 Prereqs** (conditional).
  - Core: VPC/subnets, Route53 zone, IAM/IRSA for ESO/ExternalDNS.
  - Tier 2/3: RDS, ClusterIssuers, object storage.
- Lock precedence: **`maxTier` is derived from lifecycle in V1 and not overridable**. If overrides are added later, explicitly define Option A (maxTier wins, mode sets defaults).
- Add a **V1 preflight gate** (CI or ArgoCD PreSync) that checks only what the selected tier requires.
- Update IMPL‑0001 Phase 0 + Phase 7 to reflect tier‑scoped prerequisites and preflight checks.

That keeps the system coherent and deterministic while honoring the tier intent.
```

### Assessment and Decision

**Codex feedback validates our implementation.** The Phase 0a/0b split and maxTier derivation were already in place. Codex provided clearer framing:

> "Tier-scoped foundation, not blanket gate"

**Actions taken:**

| Action | File Updated |
| ------ | ------------ |
| Added "Foundation Philosophy" section with Codex framing | IMPL-0001 |
| Renamed Phase 0a to "Core Foundation (All Tiers)" | IMPL-0001 |
| Renamed Phase 0b to "Tier 2/3 Prerequisites (Conditional)" | IMPL-0001 |
| Split Phase 7 into 7a (V1 CI/Terraform) and 7b (V2 ArgoCD PreSync) | IMPL-0001 |

**No new ADR needed.** This is implementation refinement within existing ADR-0178/0180 scope.

Signed: Claude Opus 4.5 (2026-01-23T17:30:00Z)

---

## Bootstrap v4: ArgoCD-First Architecture

**Timestamp:** 2026-01-23T13:35:00Z

### Context

User identified a gap between GitHub workflow deployment and Make-based deployment:

| Aspect | GitHub Workflow | Make (v3) |
| ------ | --------------- | --------- |
| Execution | Remote (GitHub Actions) | Local |
| App deployment | Terraform → ArgoCD orchestrates | Shell script → kubectl apply per app |
| State management | ArgoCD App-of-Apps | 15 shell stages |

Request: Achieve parity between both deployment paths by creating a v4 bootstrap script that emulates the workflow approach (ArgoCD-first).

### Implementation

Created `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh` implementing ADR-0180 (ArgoCD Orchestrator Contract).

**Architecture Comparison:**

```text
v3 (Shell Orchestration):
  Terraform → 15 shell stages → kubectl apply per app → manual sync

v4 (ArgoCD-First):
  Terraform (EKS + ArgoCD + bootstrap_apps) → ArgoCD orchestrates → validation
```

**v4 Script Structure:**

```text
Stage 1: Terraform Apply
    └── terraform -chdir=$TF_DIR apply -var="cluster_lifecycle=$LIFECYCLE"

Stage 2: Cluster Context
    └── aws eks update-kubeconfig --name $CLUSTER_NAME

Stage 3: ArgoCD Sync Wait
    └── kubectl wait --for=jsonpath='{.status.health.status}'=Healthy application --all

Stage 4: Validation
    └── kubectl get nodes, applications, services + audit script
```

**Size Comparison:**

| Script | Lines | Size |
| ------ | ----- | ---- |
| v3 | ~500 | 17KB |
| v4 | ~190 | 6.6KB |

### v4 Files Modified

| File | Change |
| ---- | ------ |
| `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh` | Created (new) |
| `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh` | Added supersession header |
| `Makefile` | Added `BOOTSTRAP_VERSION=v4` support |

### v3 Supersession Header

```bash
# =============================================================================
# GoldenPath IDP Bootstrap v3 - Shell Script Orchestration
# =============================================================================
# SUPERSEDED BY: v4 (goldenpath-idp-bootstrap-v4.sh)
# Supersession Reason: v4 implements ADR-0180 (ArgoCD Orchestrator Contract)
#   v3: Terraform → Shell script orchestration → kubectl apply per app
#   v4: Terraform → ArgoCD orchestrates everything
#
# This script is retained for backward compatibility and rollback scenarios.
```

### Usage

**GitHub Workflow (unchanged):**

```bash
gh workflow run infra-terraform-apply-dev.yml -f lifecycle=persistent
```

**Make with v4:**

```bash
make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4
```

**Direct script:**

```bash
TF_DIR=envs/dev bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh
```

### Benefits

| Aspect | v3 | v4 |
| ------ | -- | -- |
| Drift detection | None | ArgoCD reconciliation |
| Tier enforcement | Convention | ArgoCD tier labels |
| Failure recovery | Manual | ArgoCD auto-heal |
| Debugging | Shell logs | ArgoCD UI |

### Relation to ADRs

- **ADR-0180:** v4 implements the ArgoCD Orchestrator Contract
- **ADR-0178:** DNS scoping handled by Terraform → bootstrap_values → ArgoCD
- **ADR-0179:** hostSuffix propagation through Helm parameters

Signed: Claude Opus 4.5 (2026-01-23T13:35:00Z)

---

## Enforcement Gap Analysis: Soft Intent vs Hard Guards

**Timestamp:** 2026-01-23T14:00:00Z

### User Assessment (Verbatim)

> "too flexible in the wrong places right now. goldenpath has got strong intent, but enforcement is still soft: tier gating is partly declarative, DNS scoping relies on config not hard guards, preflight checks are deferred, and version pinning isn't universally enforced. That's 'flexible everywhere' in practice."

### Validation

| Claim | Accuracy | Evidence |
| ----- | -------- | -------- |
| Tier gating is partly declarative |  Accurate | `maxTier` is computed in Terraform, but ArgoCD apps don't have `goldenpath.idp/tier` labels yet. ADR-0180 specifies this but it's not implemented. Apps deploy based on Helm chart availability, not tier enforcement. |
| DNS scoping relies on config not hard guards |  Accurate | `domainFilters` is injected via Helm parameters, but nothing prevents ExternalDNS from writing outside its scope if misconfigured. No IAM policy restricts `route53:ChangeResourceRecordSets` to `*.b-{buildId}.{env}.*` for ephemeral. |
| Preflight checks are deferred |  Accurate | V1 uses CI workflow + Terraform data sources. ArgoCD PreSync hooks (the actual enforcement) are explicitly V2. If RDS is down mid-deploy, Backstage will fail at runtime, not preflight. |
| Version pinning isn't universally enforced |  Accurate | Helm chart versions are pinned in ArgoCD Application manifests, but `targetRevision: development` for values means config drift is possible. No digest pinning for container images. |

**Pattern:** Intent is documented (ADRs), but enforcement is configuration-driven rather than architecture-driven.

### Soft vs Hard Guards

| Soft (Current V1) | Hard (V2+) |
| ----------------- | ---------- |
| `domainFilters` parameter | IAM policy scoped to build subdomain |
| `maxTier` in ConfigMap | ArgoCD ApplicationSet with tier selector |
| CI preflight check | ArgoCD PreSync hook that blocks sync |
| Helm chart version pinning | OCI artifact signatures + policy enforcement |

### Roadmap Items Added

Added 4 enforcement gap items to [ROADMAP.md](docs/production-readiness-gates/ROADMAP.md):

| ID | Priority | VQ Class | Summary | Target |
| -- | -------- | -------- | ------- | ------ |
| 098 | P2 | 🔴 HV/HQ | Tier gating - ArgoCD tier labels + ApplicationSet | Q2 |
| 099 | P2 | 🔴 HV/HQ | DNS IAM scoping - Route53 policy restricts ephemeral writes | Q2 |
| 100 | P2 | 🔴 HV/HQ | Preflight PreSync - ArgoCD hooks validate tier prerequisites | Q2 |
| 101 | P2 | 🔵 MV/HQ | OCI signatures - Sigstore/Cosign + admission policy | Q3 |

### VQ Rationale

| Item | VQ | Rationale |
| ---- | -- | --------- |
| Tier gating (098) | 🔴 HV/HQ | Platform Core - prevents wrong apps from deploying |
| DNS IAM (099) | 🔴 HV/HQ | Platform Core - security boundary, prevents zone pollution |
| Preflight (100) | 🔴 HV/HQ | Platform Core - deterministic failures, audit trail |
| OCI signatures (101) | 🔵 MV/HQ | Quiet Multiplier - "build once, lock it" pattern for supply chain |

### V1 Appropriateness Assessment

**V1 is appropriate for current use case:**

- Platform team is the operator (understands intent)
- Soft guards + documentation sufficient for internal use
- Hard guards become necessary when:
  - Other teams deploy to the platform
  - Compliance requires audit trails
  - Policy enforcement without documentation is needed

**What would be discouraging:** No architecture, no path to hardening, enforcement gaps not documented.

**What we have:** Working V1 with clear V2 roadmap. The flexibility is intentional - it lets us iterate.

Signed: Claude Opus 4.5 (2026-01-23T14:00:00Z)

---

## Session Part 5: v4 Bootstrap Regression Fixes (2026-01-23)

### Changes Applied

| Area | Change | Outcome |
| ---- | ------ | ------- |
| ArgoCD ingress TLS | Replaced `tls: true` with proper list format | Helm install no longer fails on type mismatch |
| ArgoCD ingress class | Added `IngressClass/kong` before ArgoCD | Avoided ALB webhook rejection |
| Bootstrap apps | Filtered out `metadata.yaml` from app manifests | Prevented invalid K8s docs in bootstrap chart |
| External Secrets | Removed Terraform `ClusterSecretStore` | Avoided CRD-not-ready failures; ArgoCD owns it |
| Providers | Added k8s/helm providers to staging/test/prod | Envs now runnable with k8s resources |

### Files Updated

- `gitops/helm/argocd/values/dev.yaml`
- `gitops/helm/argocd/values/staging.yaml`
- `gitops/helm/argocd/values/test.yaml`
- `gitops/helm/argocd/values/prod.yaml`
- `envs/dev/main.tf`
- `envs/staging/main.tf`
- `envs/test/main.tf`
- `envs/prod/main.tf`
- `modules/kubernetes_addons/main.tf`
- `docs/adrs/ADR-0180-argocd-orchestrator-contract.md`

### Notes

- `ClusterSecretStore` is now managed exclusively by ArgoCD via `gitops/kustomize/bases/external-secrets/cluster-secret-store.yaml`.
- staging/test/prod still have the `module "eks"` block commented; providers assume an existing cluster when `eks_config.enabled=true`.

### Error Evidence (Verbatim)

```
Warning: Helm uninstall returned an information message

These resources were kept due to the resource policy:
[CustomResourceDefinition] applications.argoproj.io
[CustomResourceDefinition] applicationsets.argoproj.io
[CustomResourceDefinition] appprojects.argoproj.io
```

```
Error: unable to build kubernetes objects from release manifest: error validating "": error validating data: [apiVersion not set, kind not set]

  with module.kubernetes_addons[0].helm_release.bootstrap_apps,
  on ../../modules/kubernetes_addons/main.tf line 67, in resource "helm_release" "bootstrap_apps":
  67: resource "helm_release" "bootstrap_apps" {
```

```
Warning: Helm release "" was created but has a failed status. Use the `helm` command to investigate the error, correct it, then run Terraform again.

  with module.kubernetes_addons[0].helm_release.argocd,
  on ../../modules/kubernetes_addons/main.tf line 10, in resource "helm_release" "argocd":
  10: resource "helm_release" "argocd" {
```

```
Error: failed to create resource: admission webhook "vingress.elbv2.k8s.aws" denied the request: invalid ingress class: IngressClass.networking.k8s.io "kong" not found

  with module.kubernetes_addons[0].helm_release.argocd,
  on ../../modules/kubernetes_addons/main.tf line 10, in resource "helm_release" "argocd":
  10: resource "helm_release" "argocd" {
```

```
Error: aws-secretsmanager failed to create kubernetes rest client for update of resource: resource [external-secrets.io/v1beta1/ClusterSecretStore] isn't valid for cluster, check the APIVersion and Kind fields are valid

  with kubectl_manifest.cluster_secret_store[0],
  on main.tf line 582, in resource "kubectl_manifest" "cluster_secret_store":
  582: resource "kubectl_manifest" "cluster_secret_store" {
```

## Session Part 6: ArgoCD Namespace Race Fix (2026-01-24)

- Symptom: `kubernetes_namespace_v1.argocd` failed with "namespace argocd already exists" during `make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4 CREATE_RDS=false SKIP_ARGO_SYNC_WAIT=true`.
- Root cause: Terraform and Helm both attempted to create the `argocd` namespace without dependency ordering.
- Fix: `envs/dev/main.tf` now makes `module.kubernetes_addons` depend on `kubernetes_namespace_v1.argocd` so the namespace is created before Helm.
- Prevention: dependency ordering is codified to avoid namespace creation races.
- Follow-up: rerun the deploy command and confirm the namespace remains stable across re-runs.

## Session Part 7: Teardown State Cleanup Verification (2026-01-24)

- Command reviewed: `make cleanup-orphans-persistent CLUSTER=goldenpath-dev-eks REGION=eu-west-2 DRY_RUN=false DELETE_VPC=true CLEAN_TF_STATE=true`.
- Verification: `cleanup-orphans-persistent.sh` conditionally removes a defined set of Terraform state patterns when `CLEAN_TF_STATE=true`; it does not wipe state wholesale and skips cleanup if state is inaccessible.
- Key note: state cleanup depends on backend access and `TF_DIR` (defaults to `envs/<env>` derived from cluster name).

## Session Part 8: ExternalDNS Wildcard Verification (2026-01-24)

- Observation: ExternalDNS logs show successful UPSERT of `*.dev.goldenpathidp.io` and specific app records.
- Root cause: Route53 API represents wildcard records as `\052`, so queries for `*.dev.goldenpathidp.io.` return empty even when the record exists.
- Prevention: Added `scripts/verify_dns_records.sh` and documented the correct Route53 query in `docs/70-operations/45_DNS_MANAGEMENT.md`.

---

**Historical Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
- `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
- `backstage-helm/backstage-catalog/` → `catalog/`
