---
id: 2026-01-24-persistent-cluster-teardown-and-deploy-fix
title: Persistent Cluster Teardown and Deploy Data Source Fix
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - RB-0033-persistent-cluster-teardown
  - TEARDOWN_README
  - ADR-0180-argocd-orchestrator-contract
  - IMPL-0001-tiered-bootstrap-and-hostname-generation
---
# Session Capture: Persistent Cluster Teardown and Deploy Fix

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-24
**Timestamp:** 2026-01-24T10:00:00Z
**Branch:** development (goldenpath-idp-infra)

## Scope

- Create persistent cluster orphan cleanup script (no BuildId tags)
- Fix Terraform data source blocking v4 bootstrap two-pass deploy
- Add Terraform state cleanup to orphan cleanup script

## Work Summary

### cleanup-orphans-persistent.sh Created

Created new script for cleaning up persistent cluster resources that don't have BuildId tags (unlike ephemeral clusters):

**Discovery methods:**
- `kubernetes.io/cluster/<cluster-name>=owned` tag
- `elbv2.k8s.aws/cluster=<cluster-name>` tag
- `Lifecycle=persistent` + `Environment=<env>` tags
- Name patterns: `*<cluster-name>*` or `*<prefix>-<env>*`

**Key differences from cleanup-orphans.sh:**

| Aspect | cleanup-orphans.sh | cleanup-orphans-persistent.sh |
|--------|-------------------|------------------------------|
| Discovery | BuildId tag | Cluster name pattern |
| VPC deletion | Included | Requires `DELETE_VPC=true` |
| RDS deletion | Included | Requires `DELETE_RDS=true` |
| TF state cleanup | Not included | Optional `CLEAN_TF_STATE=true` |

### v4 Bootstrap Two-Pass Data Source Fix

**Problem:** Deploy failed with:
```
Error: reading EKS Cluster (goldenpath-dev-eks): couldn't find resource

  with data.aws_eks_cluster.this[0],
  on main.tf line 416
```

**Root cause:** Data source count only checked `eks_config.enabled`, not `enable_k8s_resources`. On Pass 1 (EKS creation), the data source tried to read a non-existent cluster.

**Fix:** Updated count condition:
```hcl
# Before
count = var.eks_config.enabled ? 1 : 0

# After
count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0
```

**How v4 two-pass works now:**

| Pass | `enable_k8s_resources` | Data source count | Behavior |
|------|------------------------|-------------------|----------|
| Pass 1 | `false` | 0 | Creates VPC, EKS without reading cluster |
| Pass 2 | `true` | 1 | Reads existing cluster for k8s provider |

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Persistent orphans not cleaned | No script for clusters without BuildId | Created `cleanup-orphans-persistent.sh` |
| Security group DependencyViolation | ENIs still attached | Added second-pass cleanup after NAT deletion |
| State drift after orphan cleanup | Resources deleted outside Terraform | Added `CLEAN_TF_STATE=true` option |
| v4 bootstrap deploy fails | Data source reads non-existent cluster | Added `enable_k8s_resources` to data source count |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| VPC preservation default | DELETE_VPC=false | Persistent VPCs should survive cluster rebuilds |
| RDS preservation default | DELETE_RDS=false | Standalone RDS lifecycle (ADR-0158) |
| TF state cleanup | Opt-in flag | Destructive operation needs explicit consent |
| Data source gating | Use enable_k8s_resources | Aligns with v4 two-pass architecture |

## Artifacts Touched

### Modified

- `envs/dev/main.tf` - Fixed data source count conditions (lines 416-427)
- `Makefile` - Added `cleanup-orphans-persistent` target
- `bootstrap/60_tear_down_clean_up/README.md` - Added persistent cleanup docs
- `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md` - Added troubleshooting section

### Added

- `bootstrap/60_tear_down_clean_up/cleanup-orphans-persistent.sh` - New script

## Validation

- `make cleanup-orphans-persistent CLUSTER=goldenpath-dev-eks REGION=eu-west-2 DRY_RUN=true` (Shows resources to delete)
- `make cleanup-orphans-persistent CLUSTER=goldenpath-dev-eks REGION=eu-west-2 DRY_RUN=false DELETE_VPC=true CLEAN_TF_STATE=true` (Full cleanup completed)

## Current State / Follow-ups

**Immediate next step:**
```bash
make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4 CREATE_RDS=false SKIP_ARGO_SYNC_WAIT=true
```

**Data source fix enables:**
- v4 two-pass bootstrap on fresh clusters
- Pass 1 creates infrastructure without k8s data sources
- Pass 2 configures k8s resources after EKS exists

**Outstanding:**
- Deploy in progress (user to validate)
- RDS deployment after EKS is up

Signed: Claude Opus 4.5 (2026-01-24T10:30:00Z)

---

## Update - 2026-01-24T10:30:00Z

**What changed**
- Fixed `data.aws_eks_cluster.this` count condition
- Fixed `data.aws_eks_cluster_auth.this` count condition
- Updated comment block explaining two-pass behavior

**Issues fixed**

| Issue | Root Cause | Fix |
|-------|------------|-----|
| v4 bootstrap Pass 1 fails | Data source reads non-existent EKS | Added `&& var.enable_k8s_resources` to count |

**Artifacts touched**
- `envs/dev/main.tf:416-427`

**Validation**
- Terraform plan with `enable_k8s_resources=false` no longer attempts EKS data source read

**Next steps**
- User to run `make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4`
- Validate full v4 two-pass deploy completes

**Outstanding**
- Deploy validation pending
- RDS deployment after EKS is operational

Signed: Claude Opus 4.5 (2026-01-24T10:30:00Z)

---

## Update - 2026-01-24T11:00:00Z

**What changed**

### 1. Forward-Thinking Solutions Mandate (Governance)

User identified recurring pattern of hot-fix-only proposals. Implemented governance mandate across 4 docs:

| Document | Change |
|----------|--------|
| `docs/10-governance/07_AI_AGENT_GOVERNANCE.md` | Added Section 10: Forward-Thinking Solutions Mandate |
| `docs/10-governance/07_1_AI_COLLABORATION_PROTOCOL.md` | Added Solution Quality Gate checklist |
| `docs/80-onboarding/24_PR_GATES.md` | Added Prevention Required Gate section |
| `docs/80-onboarding/23_NEW_JOINERS.md` | Added The Prevention Mindset section |

**Required Pattern (now enforced):**
```text
Problem → Root Cause → Fix + Prevention → Document → Never Again
```

**Anti-Pattern (prohibited):**
```text
Problem → Hot Fix → Move On → Same Problem Later → Another Hot Fix
```

### 2. Cleanup Script IAM Discovery Fix (Prevention)

**Problem:** Deploy failed with `EntityAlreadyExists` for IAM roles:

- `goldenpath-idp-cluster-autoscaler`
- `goldenpath-idp-aws-load-balancer-controller`
- `goldenpath-idp-eso-role`
- `goldenpath-idp-external-dns`
- `goldenpath-idp-eso-role-policy`
- `goldenpath-idp-external-dns-policy`

**Root cause:** Cleanup script discovered resources by `goldenpath-dev-*` pattern but IRSA roles use `goldenpath-idp-*` naming convention.

**Fix + Prevention:**

- Added `${name_prefix}-idp-*` pattern discovery to cleanup script
- Added Environment tag filtering to prevent cross-environment deletion
- Added IAM policy cleanup section for `goldenpath-idp-*` policies
- Updated README documentation

### 3. IAM Resources Deleted from AWS

Deleted orphaned resources to unblock Terraform (import failed due to k8s provider issues):

**Roles deleted:**

- `goldenpath-idp-cluster-autoscaler`
- `goldenpath-idp-aws-load-balancer-controller`
- `goldenpath-idp-eso-role`
- `goldenpath-idp-external-dns`

**Policies deleted:**

- `goldenpath-idp-eso-role-policy`
- `goldenpath-idp-external-dns-policy`

### Issues Fixed (Update 3)

| Issue              | Root Cause            | Fix              | Prevention                           |
|--------------------|-----------------------|------------------|--------------------------------------|
| IAM roles orphaned | Wrong naming pattern  | Deleted from AWS | Added `goldenpath-idp-*` discovery   |
| Hot-fix proposals  | No governance mandate | N/A              | Forward-Thinking Solutions Mandate   |

### Artifacts Touched (Update 3)

- `docs/10-governance/07_AI_AGENT_GOVERNANCE.md` - Added Section 10
- `docs/10-governance/07_1_AI_COLLABORATION_PROTOCOL.md` - Added Solution Quality Gate
- `docs/80-onboarding/24_PR_GATES.md` - Added Prevention Required Gate
- `docs/80-onboarding/23_NEW_JOINERS.md` - Added The Prevention Mindset
- `bootstrap/60_tear_down_clean_up/cleanup-orphans-persistent.sh` - Added IAM pattern discovery
- `bootstrap/60_tear_down_clean_up/README.md` - Updated IAM cleanup docs

### Validation (Update 3)

- Governance updates pass `bin/governance lint`
- IAM roles/policies deleted via AWS CLI
- Cleanup script will now discover `goldenpath-idp-*` roles with Environment tag filtering

### Outstanding (Update 3)

- Run deploy: `make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4 CREATE_RDS=false SKIP_ARGO_SYNC_WAIT=true`
- Validate IAM roles recreated correctly by Terraform
- RDS deployment after EKS is operational

Signed: Claude Opus 4.5 (2026-01-24T11:00:00Z)

---

## Update - 2026-01-24T11:30:00Z

### ArgoCD Namespace Missing (Recurring Regression)

**Problem:** Deploy failed with:

```text
Error: namespaces "argocd" not found
  with kubernetes_config_map_v1.argocd_bootstrap[0],
  on main.tf line 595
```

**Root cause:** The `argocd_bootstrap` ConfigMap references `namespace = "argocd"` but Terraform doesn't create that namespace. ArgoCD is installed via Helm AFTER Terraform, but the ConfigMap needs the namespace during Terraform's apply phase.

**Why this regressed:** Previous builds had ArgoCD installed (namespace existed). After teardown, namespace was deleted. Fresh builds fail because namespace doesn't exist when ConfigMap is created.

**Fix + Prevention:**

1. Added `kubernetes_namespace_v1.argocd` resource to `envs/dev/main.tf`
2. Updated ConfigMap to reference namespace dynamically: `kubernetes_namespace_v1.argocd[0].metadata[0].name`
3. Added explicit `depends_on` for proper ordering
4. Added `kubernetes_namespace_v1.argocd` to cleanup script state patterns

**This prevents recurrence because:** Terraform now creates the argocd namespace as a prerequisite. The namespace will exist before the ConfigMap is created, regardless of whether ArgoCD Helm is installed.

### Issues Fixed (Update 4)

| Issue                      | Root Cause                           | Fix                                    | Prevention                                   |
|----------------------------|--------------------------------------|----------------------------------------|----------------------------------------------|
| `argocd` namespace missing | ConfigMap refs namespace not created | Added `kubernetes_namespace_v1.argocd` | Terraform creates namespace before ConfigMap |

### Artifacts Touched (Update 4)

- `envs/dev/main.tf` — Added `kubernetes_namespace_v1.argocd` resource, updated ConfigMap
- `bootstrap/60_tear_down_clean_up/cleanup-orphans-persistent.sh` — Added argocd namespace to state patterns

### Outstanding (Update 4)

- User to run deploy: `make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4 CREATE_RDS=false SKIP_ARGO_SYNC_WAIT=true`
- Validate argocd namespace created and ConfigMap succeeds

Signed: Claude Opus 4.5 (2026-01-24T11:30:00Z)

---

## Update - 2026-01-24T12:00:00Z

### Security Group DependencyViolation Fix (Permanent)

**Problem:** Cleanup script failed with:

```text
An error occurred (DependencyViolation) when calling the DeleteSecurityGroup operation:
resource sg-03b8e8062cdd8a823 has a dependent object
```

**Root cause:** After load balancer deletion, AWS takes 10-30 seconds to release associated ENIs. The cleanup script immediately attempted security group deletion, which failed because ENIs were still attached.

**Fix + Prevention:**

1. Added `run_with_retry` function to cleanup script (exponential backoff, 5 attempts, starting at 10s)
2. Updated security group deletion to use retry: `run_with_retry 5 10 "aws ec2 delete-security-group ..."`
3. This handles transient DependencyViolation errors automatically

**This prevents recurrence because:** The retry logic waits for ENIs to detach naturally. Future cleanups will succeed without manual intervention.

### PROMPT-0004 Enhanced (25 Requirements)

Added requirements 21-25 based on session learnings:

| # | Requirement | Closes Gap |
|---|-------------|------------|
| 21 | Recursive application | Policy applies to errors during execution |
| 22 | No workarounds | Agent must fix underlying code |
| 23 | Policy integrity | Agent cannot amend policy without authorisation |
| 24 | Terraform authorisation | No terraform apply without human approval |
| 25 | Deployment authorisation | No deployment without human approval |

### Issues Fixed (Update 5)

| Issue | Root Cause | Fix | Prevention |
|-------|------------|-----|------------|
| SG DependencyViolation | ENIs not yet released after LB deletion | Manual wait + delete | Added `run_with_retry` with exponential backoff |
| Policy gaps | No recursive application clause | N/A | Added requirements 21-25 to PROMPT-0004 |

### Artifacts Touched (Update 5)

- `bootstrap/60_tear_down_clean_up/cleanup-orphans-persistent.sh` — Added `run_with_retry` function, updated SG deletion
- `prompt-templates/PROMPT-0004-hotfix-permanent-fix-required.txt` — Added requirements 21-25

### Validation (Update 5)

- `bash -n cleanup-orphans-persistent.sh` — Syntax OK
- Retry logic: 5 attempts, 10s initial delay, exponential backoff

### Outstanding (Update 5)

- User to run deploy when ready (requires human authorisation per PROMPT-0004 requirement 25)

Signed: Claude Opus 4.5 (2026-01-24T12:00:00Z)

---

## Update - 2026-01-24T12:30:00Z

### CI IAM Permissions Drift (DNS Root Cause)

**Problem:** User asked "why is DNS not working."

**Root cause:** The DNS implementation code exists and is correct:

- `envs/dev/main.tf:52-60` — `host_suffix` and `dns_owner_id` locals
- `envs/dev/main.tf:568-569` — passed to argocd_bootstrap ConfigMap
- ADR-0175, ADR-0178, ADR-0179 — DNS architecture documented

However, DNS cannot work because **deployment fails before ExternalDNS is created**. The failure chain:

1. CI role lacks `iam:CreatePolicy` permission
2. Terraform cannot create `goldenpath-idp-external-dns-policy`
3. ExternalDNS IRSA role has no policy attachment
4. ExternalDNS cannot authenticate to Route53
5. No DNS records are created

**This is policy drift:** The documented policy (`github-actions-terraform-full.json`) has all required permissions, but the actual AWS role doesn't have this policy applied.

**Fix:** Apply `github-actions-terraform-full.json` to the `github-actions-terraform` IAM role in AWS.

**Prevention:** ADR-0177 (already exists) supersedes ADR-0030 and documents the required permissions. V1.1 follow-up will create bootstrap Terraform to manage CI permissions in code.

### Issues Fixed (Update 6)

| Issue           | Root Cause                        | Fix                              | Prevention                           |
|-----------------|-----------------------------------|----------------------------------|--------------------------------------|
| DNS not working | CI role missing `iam:CreatePolicy` | User to apply documented policy | ADR-0177 + V1.1 bootstrap Terraform |

### Artifacts Touched (Update 6)

- (None — diagnosis only, fix requires user action in AWS Console)

### Outstanding (Update 6)

- User to apply `github-actions-terraform-full.json` to AWS role
- User to run deploy after IAM fix

Signed: Claude Opus 4.5 (2026-01-24T12:30:00Z)

---

## Update - 2026-01-24T13:00:00Z

### ClusterIssuers Missing from ArgoCD Deployment (TLS Root Cause)

**Problem:** Build was done via CLI (not CI). DNS IS working (ExternalDNS created wildcard record `*.dev.goldenpathidp.io`). However, Backstage/Grafana ingresses show no ADDRESS and Kong logs show TLS secret not found.

**Root cause chain:**

1. Ingress annotations reference `cert-manager.io/cluster-issuer: letsencrypt-staging`
2. cert-manager creates CertificateRequest
3. CertificateRequest fails: `ClusterIssuer "letsencrypt-staging" not found`
4. No TLS secret is created
5. Kong can't find secret → refuses to route traffic
6. Ingress has no ADDRESS

**Why ClusterIssuer didn't exist:**

The `dev-cert-manager` ArgoCD app only deployed the Helm chart (cert-manager itself). The ClusterIssuers defined in `gitops/kustomize/bases/cert-manager/cluster-issuers.yaml` were not included as a source.

**Fix + Prevention:**

Added third source to ArgoCD Application at `gitops/argocd/apps/dev/cert-manager.yaml`:

```yaml
# ClusterIssuers for TLS certificate issuance
- repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
  targetRevision: development
  path: gitops/kustomize/bases/cert-manager
```

**This prevents recurrence because:** ClusterIssuers are now part of the automated ArgoCD sync. They will be created on every fresh deploy.

### Issues Fixed (Update 7)

| Issue                 | Root Cause                              | Fix                                    | Prevention                      |
|-----------------------|-----------------------------------------|----------------------------------------|---------------------------------|
| ClusterIssuer missing | Not included in ArgoCD cert-manager app | Added kustomize source to ArgoCD app   | Part of automated GitOps sync   |

### Artifacts Touched (Update 7)

- `gitops/argocd/apps/dev/cert-manager.yaml` — Added ClusterIssuers kustomize source

### Validation (Update 7)

- YAML syntax validated with Python yaml.safe_load
- ArgoCD will sync on next reconciliation or manual sync

### Outstanding (Update 7)

- Push changes to development branch
- ArgoCD will auto-sync and create ClusterIssuers
- Certificates will issue and TLS secrets will be created
- Kong will route traffic and ingresses will get ADDRESS

Signed: Claude Opus 4.5 (2026-01-24T13:00:00Z)
