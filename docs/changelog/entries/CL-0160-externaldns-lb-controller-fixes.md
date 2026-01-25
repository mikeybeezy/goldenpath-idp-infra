---
id: CL-0160
title: ExternalDNS and LB Controller integration fixes
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - modules/aws_iam/main.tf
  - gitops/helm/external-dns/values/dev.yaml
  - gitops/argocd/apps/dev/external-dns.yaml
  - gitops/argocd/apps/dev/kong.yaml
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: medium
schema_version: 1
relates_to:
  - CL-0159-externaldns-wildcard-ownership
  - ADR-0175-externaldns-wildcard-ownership
  - session_capture/2026-01-21-route53-dns-terraform
supersedes: []
superseded_by: []
tags:
  - route53
  - dns
  - external-dns
  - aws-load-balancer-controller
  - iam
  - bugfix
inheritance: {}
supported_until: 2028-01-21
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: high
  potential_savings_hours: 4.0
date: 2026-01-21
author: platform-team
---

# ExternalDNS and LB Controller integration fixes

## Summary

Fixed three issues preventing ExternalDNS from creating Route53 records and
AWS Load Balancer Controller from registering NLB targets.

## What changed

### 1. AWS Load Balancer Controller IAM permissions

Added missing `elasticloadbalancing:RegisterTargets` and `DeregisterTargets`
permissions to the LB controller IAM policy in `modules/aws_iam/main.tf`.

**Symptom:** NLB targets empty, connections timing out.
**Root cause:** IAM policy missing target registration permissions.

### 2. ExternalDNS domain filter correction

Changed `domainFilters` from `dev.goldenpathidp.io` to `goldenpathidp.io`
in `gitops/helm/external-dns/values/dev.yaml`.

**Symptom:** ExternalDNS logs showed empty domain list.
**Root cause:** Domain filter must match hosted zone name, not subdomain.

### 3. ArgoCD Application branch reference

Changed `targetRevision` from `HEAD` to `development` in ArgoCD Application
manifests for ExternalDNS and Kong.

**Symptom:** ArgoCD sync status Unknown, values file not found.
**Root cause:** HEAD resolves to main branch where new files don't exist.

## Files modified

| File | Change |
|------|--------|
| `modules/aws_iam/main.tf:262-263` | Added RegisterTargets/DeregisterTargets |
| `gitops/helm/external-dns/values/dev.yaml` | domainFilters: goldenpathidp.io |
| `gitops/argocd/apps/dev/external-dns.yaml` | targetRevision: development |
| `gitops/argocd/apps/dev/kong.yaml` | targetRevision: development |

## Verification

```bash
# DNS resolution works
dig argocd.dev.goldenpathidp.io +short

# ExternalDNS logs show records created
kubectl -n kube-system logs deploy/dev-external-dns --tail=20

# NLB targets healthy
aws elbv2 describe-target-health \
  --target-group-arn <tg-arn> \
  --query "TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]"

# ArgoCD apps synced
kubectl -n argocd get application dev-external-dns -o jsonpath='{.status.sync.status}'
```

## Notes

- The IAM hotfix was applied via AWS CLI and also added to Terraform for future builds.
- After merging `development` → `main`, consider reverting ArgoCD apps to `HEAD`.
- ExternalDNS `domainFilters` must match Route53 hosted zone name exactly.
