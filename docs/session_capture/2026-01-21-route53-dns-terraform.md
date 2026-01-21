---
id: SESSION-2026-01-21-route53
title: Route53 DNS Management in Terraform
type: session-capture
status: completed
owner: platform-team
domain: platform-core
date: 2026-01-21
agent: Claude Opus 4.5
relates_to:
  - ADR-0162-kong-ingress-dns-strategy
  - ADR-0170-route53-terraform-module
  - CL-0158-route53-terraform-integration
tags:
  - route53
  - dns
  - terraform
  - kong
---

# Session Capture: Route53 DNS Management in Terraform

## Session Summary

This session implemented Route53 DNS management as Infrastructure-as-Code and shifted wildcard record ownership to ExternalDNS so Kong LoadBalancer changes are reflected automatically.

## Context

The platform needed a proper domain configuration for developer access to tooling services (ArgoCD, Keycloak, Backstage, Grafana). The domain `goldenpathidp.io` was registered with Namecheap, and we needed to:

1. Delegate DNS to AWS Route53 (not full transfer)
2. Create wildcard DNS records for environment subdomains (ExternalDNS-owned)
3. Handle dynamic LoadBalancer hostnames that change on cluster rebuilds
4. Manage DNS via IaC + GitOps for reproducible deployments

## Work Completed

### 1. Route53 Hosted Zone (Manual Setup)

Created hosted zone via AWS CLI:
```bash
aws route53 create-hosted-zone \
  --name goldenpathidp.io \
  --caller-reference "goldenpath-idp-$(date +%Y%m%d%H%M%S)"
```

**Result:**
- Zone ID: `Z0032802NEMSL43VHH4E`
- Nameservers configured in Namecheap:
  - `ns-1333.awsdns-38.org`
  - `ns-583.awsdns-08.net`
  - `ns-127.awsdns-15.com`
  - `ns-1998.awsdns-57.co.uk`

### 2. Route53 Terraform Module

Created reusable module at `modules/aws_route53/`:

| File | Purpose |
|------|---------|
| `main.tf` | Hosted zone and DNS record resources |
| `variables.tf` | Module configuration variables |
| `outputs.tf` | Zone ID, nameservers, FQDN outputs |

**Features:**
- Create or use existing hosted zone via data source or explicit zone ID
- Wildcard CNAME records for environment subdomains
- Additional CNAME, A, and Alias record support
- Configurable TTL

### 3. Dev Environment Integration

Modified `envs/dev/` to integrate Route53:

| File | Change |
|------|--------|
| `variables.tf` | Added `route53_config` variable |
| `main.tf` | Added Route53 module with Kong LB lookup |
| `outputs.tf` | Added Route53 outputs |
| `terraform.tfvars` | Enabled Route53 with domain config |

**Key Implementation:**
```hcl
# Dynamic Kong LoadBalancer hostname lookup
data "kubernetes_service_v1" "kong_proxy" {
  count = var.route53_config.enabled && var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0
  metadata {
    name      = var.route53_config.kong_service_name
    namespace = var.route53_config.kong_service_namespace
  }
}

module "route53" {
  source              = "../../modules/aws_route53"
  domain_name         = "goldenpathidp.io"
  zone_id             = "Z0032802NEMSL43VHH4E"
  environment         = "dev"
  create_hosted_zone  = false  # Use existing zone
  create_wildcard_record = false # ExternalDNS owns the wildcard
}
```

### 4. ExternalDNS Ownership (Dev + All Envs)

ExternalDNS is deployed via Argo CD with IRSA and owns wildcard DNS records:

- `*.dev.goldenpathidp.io`
- `*.test.goldenpathidp.io`
- `*.staging.goldenpathidp.io`
- `*.prod.goldenpathidp.io`

Kong proxy Services are annotated with `external-dns.alpha.kubernetes.io/hostname`
so the wildcard tracks the Kong LoadBalancer.

**Preferred policy:** `sync` (ExternalDNS is authoritative for env subdomains).

### 5. State Import (Deprecated)

Terraform no longer manages wildcard records by default, so import is not required
unless you re-enable `create_wildcard_record`. Historical note:
```bash
terraform import \
  'module.route53[0].aws_route53_record.wildcard_cname[0]' \
  'Z0032802NEMSL43VHH4E_*.dev.goldenpathidp.io_CNAME'
```

## DNS Resolution

After configuration (ExternalDNS-managed):
```
*.dev.goldenpathidp.io -> k8s-kongsyst-devkongk-22b85f1b65-557b5cc612cab397.elb.eu-west-2.amazonaws.com
```

Services accessible:
- `argocd.dev.goldenpathidp.io`
- `keycloak.dev.goldenpathidp.io`
- `backstage.dev.goldenpathidp.io`
- `grafana.dev.goldenpathidp.io`

## Architecture Decision

**Why Route53 + ExternalDNS (future)?**

| Approach | Pros | Cons |
|----------|------|------|
| Static CNAME | Simple | Breaks on LB change |
| Route53 + Terraform | IaC managed | Requires apply on LB change |
| Route53 + ExternalDNS | Auto-updates | Additional component |

Current: Route53 + ExternalDNS (wildcard ownership)

## Pending Work

1. **ExternalDNS verification** - Confirm wildcard records and TXT registry in Route53
2. **TLS/cert-manager** - HTTPS certificates for services

## Verification

### Verification Checklist

- Confirm `dev-external-dns` Application exists in Argo CD.
- Confirm `external-dns` pod is running in `kube-system`.
- Verify ExternalDNS logs show record creation for `*.dev.goldenpathidp.io`.
- Verify Route53 wildcard record and TXT registry record exist.
- Verify Kong proxy Service annotation is present.
- Confirm DNS resolution for a tooling hostname (e.g., `argocd.dev.goldenpathidp.io`).

```bash
# Verify via Route53 nameserver directly
dig @ns-1333.awsdns-38.org argocd.dev.goldenpathidp.io +short
# Returns: k8s-kongsyst-devkongk-22b85f1b65-...elb.eu-west-2.amazonaws.com

# ExternalDNS logs
kubectl -n kube-system logs deploy/external-dns --tail=200

# Route53 wildcard record
aws route53 list-resource-record-sets \
  --hosted-zone-id Z0032802NEMSL43VHH4E \
  --query "ResourceRecordSets[?Name == '*.dev.goldenpathidp.io.']"

# Terraform state verification
terraform plan -target=module.route53
# Shows: No changes
```

## Files Created/Modified

### Created
- `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh`
- `modules/aws_route53/main.tf`
- `modules/aws_route53/variables.tf`
- `modules/aws_route53/outputs.tf`
- `docs/session_capture/2026-01-21-route53-dns-terraform.md`
- `docs/adrs/ADR-0170-route53-terraform-module.md`
- `docs/adrs/ADR-0175-externaldns-wildcard-ownership.md`
- `docs/changelog/entries/CL-0158-route53-terraform-integration.md`
- `docs/changelog/entries/CL-0159-externaldns-wildcard-ownership.md`
- `gitops/helm/external-dns/README.md`
- `gitops/helm/external-dns/metadata.yaml`
- `gitops/helm/external-dns/values/dev.yaml`
- `gitops/helm/external-dns/values/test.yaml`
- `gitops/helm/external-dns/values/staging.yaml`
- `gitops/helm/external-dns/values/prod.yaml`
- `gitops/argocd/apps/dev/external-dns.yaml`
- `gitops/argocd/apps/test/external-dns.yaml`
- `gitops/argocd/apps/staging/external-dns.yaml`
- `gitops/argocd/apps/prod/external-dns.yaml`
- `backstage-helm/backstage-catalog/docs/changelogs/changelog-0159.yaml`

### Modified
- `modules/aws_iam/main.tf`
- `modules/aws_iam/variables.tf`
- `modules/aws_iam/outputs.tf`
- `envs/dev/main.tf`
- `envs/dev/variables.tf`
- `envs/dev/outputs.tf`
- `envs/dev/terraform.tfvars`
- `envs/test/main.tf`
- `envs/test/variables.tf`
- `envs/staging/main.tf`
- `envs/staging/variables.tf`
- `envs/prod/main.tf`
- `envs/prod/variables.tf`
- `gitops/helm/kong/values/dev.yaml`
- `gitops/helm/kong/values/test.yaml`
- `gitops/helm/kong/values/staging.yaml`
- `gitops/helm/kong/values/prod.yaml`
- `gitops/argocd/CHART_VERSIONS.md`
- `docs/70-operations/20_TOOLING_APPS_MATRIX.md`

---

Signed: Claude Opus 4.5 (2026-01-21T03:00:00Z)

---

## Session Artifact Review - Bugs & Inconsistencies

### **POLICY DECISIONS**

#### 1. **ExternalDNS Policy Set to `sync` - Preferred Choice**
**File:** `gitops/helm/external-dns/values/dev.yaml:20`
```yaml
policy: sync  # ⚠️ This DELETES records not in K8s
```
**Risk:** The `sync` policy will delete DNS records that don't have corresponding K8s resources. If someone manually created a record in Route53, ExternalDNS will delete it.

**Decision:** Keep `sync` as the preferred policy for env subdomains.

---

#### 2. **Session Capture Wildcard Ownership (Resolved)**
**Update:** Session capture now reflects ExternalDNS ownership of wildcard records.

---

#### 3. **ExternalDNS domainFilters Scoped to `dev.goldenpathidp.io` Only**
**File:** `gitops/helm/external-dns/values/dev.yaml:24-25`
```yaml
domainFilters:
  - dev.goldenpathidp.io
```
**Issue:** This is correct for dev, but if someone creates an Ingress with `myapp.goldenpathidp.io` (without `dev.`), ExternalDNS won't manage it. This is **intentional** but worth noting.

---

### **MODERATE ISSUES**

#### 4. **Kong Wildcard Annotation (Resolved)**
**Update:** Kong proxy Service annotations now include wildcard hostnames in
`gitops/helm/kong/values/{dev,test,staging,prod}.yaml`.

---

#### 5. **ExternalDNS Argo App Owner (Resolved)**
**File:** `gitops/argocd/apps/dev/external-dns.yaml:9`
```yaml
goldenpath.idp/owner: platform-team
```
**Update:** Owner is set to `platform-team`.

---

#### 6. **Kong Manager Ingress Missing Environment Labels (Defer)**
**File:** `gitops/manifests/kong-manager-ingress.yaml`
```yaml
metadata:
  labels:
    app.kubernetes.io/name: kong-manager
    app.kubernetes.io/part-of: kong
    # Missing: app.kubernetes.io/instance, environment label
```
**Recommendation:** Add `environment: dev` label for consistency.

---

### **MINOR ISSUES / DOCUMENTATION DRIFT**

#### 7. **Pending Work Section (Resolved)**
**Update:** Pending work now reflects ExternalDNS verification + policy review.

---

#### 8. **Tooling Apps Matrix DNS Requirements (Resolved)**
**Update:** Tooling matrix now reflects ExternalDNS ownership and Kong annotations.

---

### **VERIFICATION NEEDED**

| Item | File to Check | What to Verify |
|------|---------------|----------------|
| ExternalDNS wildcard | Route53 | `*.dev.goldenpathidp.io` record + TXT registry present |
| Kong proxy annotation | `gitops/helm/kong/values/dev.yaml` | `external-dns.alpha.kubernetes.io/hostname` annotation |
| ExternalDNS IRSA trust | `modules/aws_iam/main.tf` | Service account namespace matches (`kube-system`) |

---

### **SUMMARY**

| Severity | Count | Action |
|----------|-------|--------|
| **Critical** | 0 | Preferred policy set to `sync` |
| **Moderate** | 1 | Consider env labels on Kong Manager ingress |

---

## Session Artifact Verification (2026-01-21)

### Files Verified as Existing

All files listed in the "Files Created" section have been verified:

| File | Status |
|------|--------|
| `docs/adrs/ADR-0175-externaldns-wildcard-ownership.md` | ✓ Exists |
| `docs/changelog/entries/CL-0159-externaldns-wildcard-ownership.md` | ✓ Exists |
| `gitops/argocd/apps/dev/external-dns.yaml` | ✓ Exists |
| `gitops/argocd/apps/test/external-dns.yaml` | ✓ Exists |
| `gitops/argocd/apps/staging/external-dns.yaml` | ✓ Exists |
| `gitops/argocd/apps/prod/external-dns.yaml` | ✓ Exists |
| `gitops/helm/external-dns/values/dev.yaml` | ✓ Exists |
| `gitops/helm/external-dns/values/test.yaml` | ✓ Exists |
| `gitops/helm/external-dns/values/staging.yaml` | ✓ Exists |
| `gitops/helm/external-dns/values/prod.yaml` | ✓ Exists |
| `modules/aws_route53/main.tf` | ✓ Exists |
| `modules/aws_route53/variables.tf` | ✓ Exists |
| `modules/aws_route53/outputs.tf` | ✓ Exists |
| `backstage-helm/backstage-catalog/docs/changelogs/changelog-0159.yaml` | ✓ Exists |

### Key Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| ExternalDNS owns wildcard records | ✓ Accurate | `create_wildcard_record = false` in Terraform |
| Kong proxy has ExternalDNS annotation | ✓ Accurate | `gitops/helm/kong/values/dev.yaml:27`: `external-dns.alpha.kubernetes.io/hostname: "*.dev.goldenpathidp.io"` |
| ArgoCD app owner is `platform-team` | ✓ Accurate | `gitops/argocd/apps/dev/external-dns.yaml:9` |
| ExternalDNS policy is `sync` | ✓ Accurate | `gitops/helm/external-dns/values/dev.yaml:20` |
| ServiceAccount `create: false` (IRSA) | ✓ Accurate | `gitops/helm/external-dns/values/dev.yaml:38-39` |
| ExternalDNS IRSA outputs exist | ✓ Accurate | `modules/aws_iam/outputs.tf:37-44` |

### Outstanding Items Requiring Live Cluster Verification

| Item | Command | Expected Result |
|------|---------|-----------------|
| ExternalDNS wildcard record | `aws route53 list-resource-record-sets --hosted-zone-id Z0032802NEMSL43VHH4E --query "ResourceRecordSets[?Name == '*.dev.goldenpathidp.io.']"` | CNAME + TXT registry present |
| ExternalDNS pod running | `kubectl -n kube-system get pods -l app.kubernetes.io/name=external-dns` | Running pod |
| Kong annotation applied | `kubectl -n kong-system get svc dev-kong-kong-proxy -o jsonpath='{.metadata.annotations}'` | Contains `external-dns.alpha.kubernetes.io/hostname` |

### Verification Result

**All file-level claims verified as accurate.** The session capture correctly reflects:
- ExternalDNS ownership of wildcard DNS records
- Terraform deferring wildcard management (`create_wildcard_record = false`)
- Kong Service annotations for ExternalDNS hostname registration
- IRSA configuration for ExternalDNS

---

Verified by: Claude Opus 4.5 (2026-01-21)

---

## Issues Encountered and Resolution (2026-01-21)

### Issue 1: ExternalDNS Not Creating Route53 Records

**Symptom:** ExternalDNS logs showed `Applying provider record filter for domains: []` - empty domain list.

**Root Cause:** The `domainFilters` was set to `dev.goldenpathidp.io`, but ExternalDNS looks for a hosted zone matching that exact domain. The hosted zone is `goldenpathidp.io` (parent domain).

**Fix:** Changed `domainFilters` from `dev.goldenpathidp.io` to `goldenpathidp.io` in `gitops/helm/external-dns/values/dev.yaml`.

```yaml
# Before (broken)
domainFilters:
  - dev.goldenpathidp.io

# After (working)
domainFilters:
  - goldenpathidp.io
```

**Lesson:** ExternalDNS `domainFilters` must match the Route53 hosted zone name, not the subdomain you want to create records in.

---

### Issue 2: ArgoCD Application Using Wrong Git Branch

**Symptom:** ArgoCD Application status was `Unknown` with error `no such file or directory` for values file.

**Root Cause:** `targetRevision: HEAD` resolves to the default branch (`main`), but the ExternalDNS and Kong values files with new annotations were only on `development` branch.

**Fix:** Changed `targetRevision` from `HEAD` to `development` in ArgoCD Application manifests:
- `gitops/argocd/apps/dev/external-dns.yaml`
- `gitops/argocd/apps/dev/kong.yaml`

```yaml
# Before (broken)
- repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
  targetRevision: HEAD
  ref: values

# After (working)
- repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
  targetRevision: development
  ref: values
```

**Recommendation:** After merging `development` → `main`, consider pointing staging/prod back to `main` (or pin to release tags/SHAs) for stability.

---

### Issue 3: AWS Load Balancer Controller Missing IAM Permissions

**Symptom:** Services accessible via DNS but connections timing out. ELB targets showing as empty.

**Root Cause:** AWS Load Balancer Controller IAM policy was missing `elasticloadbalancing:RegisterTargets` and `elasticloadbalancing:DeregisterTargets` permissions.

**Error in logs:**
```
api error AccessDenied: User: arn:aws:sts::593517239005:assumed-role/goldenpath-idp-aws-load-balancer-controller/...
is not authorized to perform: elasticloadbalancing:RegisterTargets
```

**Hotfix (applied immediately):**
```bash
# Added permissions via AWS CLI
aws iam create-policy-version \
  --policy-arn arn:aws:iam::593517239005:policy/goldenpath-load-balancer-controller-policy \
  --policy-document file:///tmp/lb-policy-updated.json \
  --set-as-default

# Restarted controller to pick up new permissions
kubectl -n kube-system rollout restart deployment aws-load-balancer-controller
```

**Permanent Fix:** Added permissions to Terraform IAM module at `modules/aws_iam/main.tf:262-263`:
```hcl
"elasticloadbalancing:RegisterTargets",
"elasticloadbalancing:DeregisterTargets",
```

**Lesson:** AWS LB Controller requires `RegisterTargets`/`DeregisterTargets` for NLB target group management. Always verify IAM permissions match the official AWS LB Controller policy.

---

### Summary of Fixes

| Issue | File Changed | Change |
|-------|--------------|--------|
| ExternalDNS domain filter | `gitops/helm/external-dns/values/dev.yaml` | `domainFilters: goldenpathidp.io` |
| ArgoCD branch reference | `gitops/argocd/apps/dev/*.yaml` | `targetRevision: development` |
| LB Controller IAM | `modules/aws_iam/main.tf` | Added RegisterTargets/DeregisterTargets |

---

Updated by: Claude Opus 4.5 (2026-01-21T05:20:00Z)

---

## Reviewer Feedback (Codex)

- Consider updating the title/tags to mention ExternalDNS + wildcard ownership so the topic is discoverable at a glance.
- Replace any "future enhancement" language with "implemented" (or "planned") to prevent doc drift as the repo changes.
- Add a short preflight note above verification commands (AWS profile/region set, hosted zone id for the env, ExternalDNS app deployed).
- Add an example "expected" ELB hostname format (or reference the Kong service command) so readers can validate quickly.
- Clarify teardown v5 scope: persistent AWS clusters only, and ExternalDNS app deletion/suspension is included before Kong teardown.

---

## Branch Strategy Recommendation: ArgoCD `targetRevision` per Environment

### Context

During this session, we changed ArgoCD Applications from `targetRevision: HEAD` to `targetRevision: development` because:
- `HEAD` resolves to the default branch (`main`)
- New files/changes on `development` branch weren't visible to ArgoCD until merged

This raises the question: **Should different environments track different branches?**

### Recommended Pattern (Default)

Avoid `HEAD` in ArgoCD manifests; it resolves to the default branch (currently `main`) and can change over time.

| Environment | ArgoCD `targetRevision` | Sync Policy | Rationale |
|-------------|------------------------|-------------|-----------|
| **dev** | `development` | Automated | Immediate feedback on changes |
| **test** | `main` | Automated | Validate merged code with lower blast radius |
| **staging** | `main` | Automated | Pre-prod validation of merged code |
| **prod** | Release tag or SHA | **Manual** | Immutable, auditable releases |

### Benefits

1. **Dev environment gets immediate feedback** - Changes visible without waiting for PR merge
2. **Staging/prod stay stable** - Only see code that's been reviewed and merged
3. **Clear promotion path** - Code flows: `development` → PR → `main` → staging → prod
4. **Manual prod sync** - Extra safety layer for production deployments

### Comparison with ADR-0042 (Platform Branching Strategy)

**ADR-0042 establishes:**
- Two-branch model: `development` → `main`
- All work branches from `development`
- Only `development` merges into `main`
- CI guard to prevent direct-to-main merges

**Gap identified:** ADR-0042 defines the Git branching model but does **not** specify:
- How ArgoCD `targetRevision` should map to environments
- Whether dev environments should track `development` vs `main`
- Sync policy recommendations (automated vs manual) per environment

**Recommendation:** Propose a follow-up ADR (e.g., ADR-0176) to document the ArgoCD `targetRevision` → environment mapping as a GitOps extension to ADR-0042.

### Implementation Checklist

If adopting environment-to-branch mapping:

- [ ] Update `gitops/argocd/apps/dev/*.yaml` → `targetRevision: development`
- [ ] Keep `gitops/argocd/apps/test/*.yaml` → `targetRevision: main`
- [ ] Keep `gitops/argocd/apps/staging/*.yaml` → `targetRevision: main`
- [ ] Pin `gitops/argocd/apps/prod/*.yaml` → release tag or SHA
- [ ] Set `syncPolicy.automated: false` for prod apps (manual sync)
- [ ] If using tags/SHAs, add automation to bump `targetRevision` per release
- [ ] Document in ADR-0176 (proposed)

### Verify Current State

Run this before relying on the matrix below to avoid stale assumptions:

```bash
rg -n "targetRevision:" gitops/argocd/apps/{dev,test,staging,prod}/*.yaml
```

**Note:** After merging `development` → `main`, you can optionally repoint dev to `main` if you prefer stability over iteration speed.

---

Added by: Claude Opus 4.5 (2026-01-21T06:00:00Z)

---

## Teardown V5 Script Review

### Overview

The script (`bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v5.sh`) is a comprehensive EKS cluster teardown tool with 9 stages and ExternalDNS integration added in v5. It's well-structured with proper error handling and extensive configurability.

### Strengths

| Area | Details |
|------|---------|
| **Defensive coding** | `set -euo pipefail`, required command validation, proper exit traps |
| **Idempotency** | Most operations check existence before acting, skip if already deleted |
| **Observability** | Explicit `[STEP:]`, `[BREAK-GLASS]`, stage banners with timestamps |
| **Fallback strategies** | RDS/secrets cleanup uses BuildId → cluster tag → name pattern |
| **DRY_RUN mode** | All destructive flags disabled when `DRY_RUN=true` |
| **Timeouts** | Configurable waits with heartbeat logging |
| **Resource ordering** | ExternalDNS → Kong → Ingress → LB → nodegroups → cluster |

### Issues and Recommendations

#### 1. ExternalDNS Route53 Record Orphaning Risk (Medium)

**Problem:** When ExternalDNS is deleted (Stage 2), its Route53 TXT registry records may be left behind if ExternalDNS doesn't have time to clean up before the pod terminates.

**Current flow:**
```
delete_external_dns_application  # --wait=false
delete_argo_application          # Kong, also --wait=false
delete_kong_resources            # Deletes Kong LB Service
```

**Recommendation:** Add a brief wait or check for ExternalDNS pod termination before deleting Kong:
```bash
# After delete_external_dns_application
sleep 10  # Allow ExternalDNS to process deletion
```

Or use `--wait=true` for ExternalDNS specifically since DNS cleanup is critical.

#### 2. ARGO_APP_NAMESPACE Default Mismatch (Low)

**Line 142:**
```bash
ARGO_APP_NAMESPACE="${ARGO_APP_NAMESPACE:-kong-system}"
```

This default assumes the Kong ArgoCD Application lives in `kong-system`, but ArgoCD Applications typically live in the `argocd` namespace. The script later uses this for Kong application deletion.

**Recommendation:** Verify the default matches your deployment pattern or add a comment explaining the assumption.

#### 3. Missing Validation for `drain-nodegroup.sh` (Low)

**Line 1774:**
```bash
bash "${repo_root}/bootstrap/60_tear_down_clean_up/drain-nodegroup.sh" "${ng}" || \
```

The script doesn't check if `drain-nodegroup.sh` exists before calling it.

**Recommendation:** Add existence check:
```bash
if [[ -f "${repo_root}/bootstrap/60_tear_down_clean_up/drain-nodegroup.sh" ]]; then
```

#### 4. Secret Name Pattern Stripping May Fail (Low)

**Lines 1852, 1889:**
```bash
secret_name="${secret_name%%-[A-Za-z0-9][A-Za-z0-9][A-Za-z0-9][A-Za-z0-9][A-Za-z0-9][A-Za-z0-9]}"
```

This pattern assumes the AWS Secrets Manager version suffix is exactly 6 characters. AWS uses a 6-character suffix, but this is fragile if AWS changes the format.

#### 5. No Route53 TXT Registry Cleanup Option (Feature Gap)

The script deletes the ExternalDNS ArgoCD Application but doesn't provide an option to clean up orphaned TXT registry records in Route53. If ExternalDNS is deleted abruptly, records like `external-dns-*.dev.goldenpathidp.io` may persist.

**Recommendation:** Add optional Route53 cleanup for TXT registry records:
```bash
# Optional: Clean up ExternalDNS TXT registry records
DELETE_EXTERNALDNS_TXT_RECORDS="${DELETE_EXTERNALDNS_TXT_RECORDS:-false}"
EXTERNALDNS_TXT_PREFIX="${EXTERNALDNS_TXT_PREFIX:-external-dns}"
```

### Security Considerations

| Check | Status |
|-------|--------|
| No hardcoded credentials | ✓ |
| Uses AWS CLI credential chain | ✓ |
| TEARDOWN_CONFIRM gate required | ✓ |
| No interactive prompts in dangerous paths | ✓ |
| Proper quoting throughout | ✓ |

### Summary

**Overall:** Production-ready with good safety defaults. The ExternalDNS integration follows the established patterns.

**Priority fixes:**
1. Consider adding a brief wait after ExternalDNS deletion to allow DNS record cleanup
2. Verify `ARGO_APP_NAMESPACE` default matches your deployment pattern
3. Add existence check for `drain-nodegroup.sh`

**Optional enhancements:**
- Route53 TXT registry record cleanup option
- ExternalDNS deletion with `--wait=true` to ensure clean DNS state

---

Reviewed by: Claude Opus 4.5 (2026-01-21T06:30:00Z)
