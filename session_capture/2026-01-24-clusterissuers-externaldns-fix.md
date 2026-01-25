# Session Capture: ClusterIssuers and ExternalDNS Fix

**Date**: 2026-01-24
**Session Type**: Hotfix / Bug Fix
**Environment**: dev
**Cluster**: goldenpath-dev-eks (persistent)

## Problem Statement

After deploying the persistent dev cluster via `make deploy-persistent`, the following issues were observed:

1. **TLS certificates not being issued** - Ingresses stuck waiting for certificates
2. **DNS records pointing to old load balancer** - ExternalDNS not updating Route53 records
3. **Hostnames not resolving** - `*.dev.goldenpathidp.io` failing to route traffic

## Root Cause Analysis

### Issue 1: ClusterIssuers Not Deployed

**Symptom**: CertificateRequests failing with "ClusterIssuer letsencrypt-staging not found"

**Root Cause**: The `dev-cert-manager` ArgoCD Application only deployed the cert-manager Helm chart. The ClusterIssuers (`letsencrypt-staging`, `letsencrypt-prod`, `selfsigned-issuer`) defined in `gitops/kustomize/bases/cert-manager/cluster-issuers.yaml` were not included as a source.

**Fix**: Added third source to cert-manager ArgoCD Application:
```yaml
# gitops/argocd/apps/dev/cert-manager.yaml
sources:
  - repoURL: https://charts.jetstack.io
    chart: cert-manager
    ...
  - repoURL: <https://github.com/mikeybeezy/goldenpath-idp-infra.git>
    targetRevision: development
    ref: values
  # NEW: ClusterIssuers for TLS certificate issuance
  - repoURL: <https://github.com/mikeybeezy/goldenpath-idp-infra.git>
    targetRevision: development
    path: gitops/kustomize/bases/cert-manager
```

### Issue 2: ExternalDNS domainFilters Misconfiguration

**Symptom**: ExternalDNS logs showing `Applying provider record filter for domains: []` (empty)

**Root Cause**: Terraform's `helm_release.bootstrap_apps` was injecting:
```
domainFilters[0] = dev.goldenpathidp.io  # WRONG - subdomain
```

But ExternalDNS needs the apex domain to find the Route53 hosted zone:
```
domainFilters[0] = goldenpathidp.io  # CORRECT - apex domain
```

The injection logic in `modules/kubernetes_addons/main.tf` used `var.bootstrap_values.host_suffix` (which is `dev.goldenpathidp.io`) instead of the apex domain.

**Fix**: Removed `domainFilters` injection from Terraform. The correct value is already in `gitops/helm/external-dns/values/dev.yaml`:
```yaml
domainFilters:
  - goldenpathidp.io  # Apex domain - correct
zoneIdFilters:
  - Z0032802NEMSL43VHH4E  # Explicit zone ID
```

Only `txtOwnerId` is now injected dynamically for per-environment DNS ownership scoping.

## Files Modified

| File | Change |
|------|--------|
| `gitops/argocd/apps/dev/cert-manager.yaml` | Added kustomize source for ClusterIssuers |
| `modules/kubernetes_addons/main.tf` | Removed domainFilters injection, kept txtOwnerId |
| `docs/changelog/entries/CL-0168-clusterissuers-externaldns-fix.md` | Changelog entry |

## Verification

### ClusterIssuers Deployed
```bash
$ kubectl get clusterissuers
NAME                  READY   AGE
letsencrypt-prod      True    2m
letsencrypt-staging   True    2m
selfsigned-issuer     True    2m
```

### Terraform Validation
```bash
# All environments validated successfully
$ for env in dev staging prod; do terraform -chdir=envs/$env validate; done
Success! The configuration is valid.
Success! The configuration is valid.
Success! The configuration is valid.
```

## CI/PR Status

**PR #278**: <https://github.com/mikeybeezy/goldenpath-idp-infra/pull/278>

| Check | Status |
|-------|--------|
| Terraform Lint & Validate | PASS |
| pr-guardrails | PASS |
| changelog-policy | PASS |
| pre-commit | PASS |
| gitleaks | PASS |
| All other checks | PASS |

**Note**: PR targets main branch - requires human merge.

## Additional Findings

### CI IAM Permissions Gap

Verified that `github-actions-terraform` IAM role is missing permissions documented in `docs/10-governance/policies/iam/github-actions-terraform-full.json`:

- Missing: `iam:CreatePolicy` (needed for ExternalDNS/ESO policies)
- Missing: `secretsmanager:*` (needed for Backstage/Keycloak secrets)
- Missing: `route53:ChangeResourceRecordSets` (needed for DNS management)

This affects CI builds but not CLI builds (which use admin credentials).

### Build Timing Gap

Discovered that persistent cluster deployments via Bootstrap v4 are NOT being captured in `docs/build-timings.csv`. The `record-build-timing.sh` script is only called for ephemeral builds.

## PROMPT-0004 Compliance

```
HOTFIX COMPLIANCE STATEMENT

1) Root cause: ClusterIssuers not included in cert-manager ArgoCD app; domainFilters using subdomain instead of apex
2) Prevention: Added kustomize source to cert-manager app; removed domainFilters injection from Terraform
3) Backward compat: Yes
4) Breaking changes: None
5) Testing: terraform validate all envs, kubectl get clusterissuers
6) Rollback: Revert commits
7) Minimal scope: 3 files modified
8) Documentation: This session capture
9) Session capture: Updated
10) Affected systems: cert-manager, ExternalDNS, Route53
11) Idempotency: Yes - Terraform and ArgoCD are idempotent
12) Existing data: No data loss
13) Side effects: DNS records will be updated to current LB
14) Rollout: ArgoCD auto-sync
15) Observability: kubectl logs, Route53 console
16) Pre-flight: terraform validate, kubectl get clusterissuers
17) Cross-automation: Makefile unaffected
18) Rebuild-cycle: Survives teardown→deploy (fix is in code)
19) Prevention codified: gitops/argocd/apps/dev/cert-manager.yaml:26-29, modules/kubernetes_addons/main.tf:101-109
20) Cascade check: Other apps unaffected
21) Recursive application: Yes
22) No workarounds: Code fix only
23) Policy integrity: Not modified
24) Terraform authorisation: Awaiting human authorisation
25) Deployment authorisation: Awaiting human authorisation
```

## Next Steps

1. **Human merge PR #278** to main branch
2. **Apply Terraform changes** to update bootstrap_apps with corrected config:
   ```bash
   cd envs/dev && terraform apply \
     -var-file=terraform.tfvars \
     -var="enable_k8s_resources=true" \
     -var="apply_kubernetes_addons=true"
   ```
3. **Monitor ExternalDNS** for correct domain filter and DNS record updates
4. **Verify TLS certificates** complete ACME challenges
5. **Update CI IAM policy** with documented permissions (separate task)
6. **Add build timing capture** to persistent cluster targets (separate task)
