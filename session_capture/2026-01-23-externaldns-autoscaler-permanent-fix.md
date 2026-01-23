---
id: SC-2026-01-23-externaldns-autoscaler-permanent-fix
title: ExternalDNS and Cluster Autoscaler Permanent Fixes
type: session_capture
domain: platform-core
owner: platform-team
lifecycle: active
status: complete
schema_version: 1
risk_profile:
  production_impact: high
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
relates_to:
  - ADR-0178
  - ADR-0179
  - ADR-0180
---
# ExternalDNS and Cluster Autoscaler Permanent Fixes

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-23
**Timestamp:** 2026-01-23T17:00:00Z
**Branch:** development

## Scope

- Fix cluster autoscaler "no node group config" errors
- Fix DNS not resolving for applications (ExternalDNS not creating Route53 records)
- Ensure fixes are permanent and survive cluster recreation

## Work Summary

- Diagnosed cluster autoscaler was using hardcoded old cluster name from previous ephemeral build
- Implemented dynamic cluster name injection via Terraform → ArgoCD Application parameters
- Diagnosed ExternalDNS "All records up to date" while no A records existed in Route53
- Found root cause: `domainFilters` set to subdomain (`dev.goldenpathidp.io`) instead of hosted zone (`goldenpathidp.io`)
- Fixed ExternalDNS configuration with correct domain filter and explicit zone ID filter

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Cluster autoscaler "no node group config" for all nodes | Hardcoded `clusterName` in values file pointed to old ephemeral build ID (`goldenpath-dev-eks-31-12-25-04`) | Implemented dynamic injection via Terraform ArgoCD Application parameters; values file now has placeholder `INJECTED_BY_TERRAFORM` |
| Terraform localhost provider error on fresh deploy | `depends_on = [module.eks]` on data sources caused deferred evaluation | Removed `depends_on` from EKS data sources; use bootstrap v4 two-pass approach instead |
| DNS not resolving - ExternalDNS says "All records up to date" | Route53 wildcard record pointed to deleted NLB (`07cb02b67f`); ExternalDNS didn't detect stale ALIAS target | Manually deleted stale record; investigated deeper issue |
| ExternalDNS not creating ANY records | `domainFilters: [dev.goldenpathidp.io]` doesn't match hosted zone `goldenpathidp.io`; ExternalDNS uses domainFilters to FIND zones, not just filter records | Changed `domainFilters` to `goldenpathidp.io`; added explicit `zoneIdFilters` |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cluster name injection method | Terraform → ArgoCD Application helm parameters | Keeps values files environment-agnostic; dynamic injection at deploy time; works for both persistent and ephemeral |
| ExternalDNS domain filter scope | Match hosted zone name (`goldenpathidp.io`) not subdomain | ExternalDNS uses domainFilters for zone discovery, not just record filtering; subdomain filter prevents finding parent zone |
| Zone ID filter | Explicit `zoneIdFilters: [Z0032802NEMSL43VHH4E]` | Defense in depth; ensures correct zone even if multiple zones exist |

## Artifacts Touched (links)

### Modified

- `gitops/helm/external-dns/values/dev.yaml` - Fixed domainFilters from `dev.goldenpathidp.io` to `goldenpathidp.io`; added zoneIdFilters
- `gitops/helm/cluster-autoscaler/values/dev.yaml` - Changed hardcoded clusterName to placeholder with documentation
- `modules/kubernetes_addons/main.tf` - Fixed cluster-autoscaler parameter injection pattern (8-space indent for multi-source format)
- `envs/dev/main.tf` - Removed `depends_on = [module.eks]` from data sources

### Referenced / Executed

- Route53 hosted zone `Z0032802NEMSL43VHH4E` (goldenpathidp.io)
- Kong proxy service `dev-kong-kong-proxy` in `kong-system` namespace
- ExternalDNS deployment in `kube-system` namespace
- Cluster autoscaler deployment in `kube-system` namespace

## Validation

- `kubectl logs -n kube-system dev-cluster-autoscaler-...` - No more "no node group config" errors; correctly managing 6 nodes
- `kubectl get application dev-cluster-autoscaler -n argocd -o jsonpath='{.spec.sources[0].helm.parameters}'` - Shows `autoDiscovery.clusterName: goldenpath-dev-eks` injected
- `aws route53 list-resource-record-sets --hosted-zone-id Z0032802NEMSL43VHH4E --query "ResourceRecordSets[?contains(Name, 'dev.goldenpathidp')]"` - Shows `*.dev.goldenpathidp.io` A record and TXT ownership records
- `dig @8.8.8.8 hello-goldenpath-idp.dev.goldenpathidp.io +short` - Returns `35.177.226.141, 35.177.45.205`
- `curl -s -o /dev/null -w "%{http_code}" http://hello-goldenpath-idp.dev.goldenpathidp.io/` - Returns `200`

## Current State / Follow-ups

- ExternalDNS permanently fixed - will automatically create/update DNS records on cluster recreation
- Cluster autoscaler permanently fixed - uses dynamic cluster name from Terraform
- Changes need to be committed to `development` branch for ArgoCD to persist them
- ArgoCD selfHeal currently disabled for external-dns (re-enabled after testing)

Signed: Claude Opus 4.5 (2026-01-23T17:30:00Z)

---

## Technical Deep Dive

### ExternalDNS Domain Filter Issue

**Symptom**: ExternalDNS logs showed:
```
Skipping record ... because no hosted zone matching record DNS Name was detected
```

**Root Cause Analysis**:

1. ExternalDNS was configured with `domainFilters: [dev.goldenpathidp.io]`
2. The Route53 hosted zone is `goldenpathidp.io` (root domain)
3. ExternalDNS uses `domainFilters` for TWO purposes:
   - **Zone discovery**: Find which hosted zone to use
   - **Record filtering**: Restrict which records can be created
4. When checking if `*.dev.goldenpathidp.io` belongs to zone `goldenpathidp.io`:
   - ExternalDNS looks for a zone that matches the domain filter
   - `dev.goldenpathidp.io` doesn't match any zone name
   - Therefore: "no hosted zone matching record DNS Name"

**Fix**:
```yaml
# BEFORE (broken)
domainFilters:
  - dev.goldenpathidp.io

# AFTER (fixed)
domainFilters:
  - goldenpathidp.io  # Must match the hosted zone name
zoneIdFilters:
  - Z0032802NEMSL43VHH4E  # Explicit zone targeting
```

### Cluster Autoscaler Injection Pattern

**Problem**: Multi-source ArgoCD Applications use 8-space indentation, not 10-space.

**Fix in `modules/kubernetes_addons/main.tf`**:
```terraform
# cluster-autoscaler: inject clusterName (multi-source format uses 8-space indent)
basename(f) == "cluster-autoscaler.yaml" ?
replace(
  file("${var.path_to_app_manifests}/${f}"),
  "      helm:\n        valueFiles:",
  "      helm:\n        parameters:\n          - name: autoDiscovery.clusterName\n            value: ${var.cluster_name}\n        valueFiles:"
) :
```

This injects the parameter block before `valueFiles:` in the YAML structure.

---

## Commit Checklist

Files to commit:
- [x] `gitops/helm/external-dns/values/dev.yaml`
- [x] `gitops/helm/cluster-autoscaler/values/dev.yaml`
- [x] `modules/kubernetes_addons/main.tf`
- [x] `envs/dev/main.tf`
