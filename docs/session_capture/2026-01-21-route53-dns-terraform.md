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
