---
id: CL-0161
title: ArgoCD targetRevision standardization for env apps
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - gitops/argocd/apps/dev/*.yaml
  - gitops/argocd/apps/test/*.yaml
  - gitops/argocd/apps/staging/*.yaml
  - gitops/argocd/apps/prod/*.yaml
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - session_capture/2026-01-21-route53-dns-terraform
supersedes: []
superseded_by: []
tags:
  - gitops
  - argocd
  - branch-policy
inheritance: {}
supported_until: 2028-01-21
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 1.0
date: 2026-01-21
author: platform-team
---

# ArgoCD targetRevision standardization for env apps

## Summary

Standardized ArgoCD app `targetRevision` values for environment applications
that source values/manifests from `goldenpath-idp-infra`.

## What changed

- **dev** apps referencing this repo now use `targetRevision: development`.
- **test/staging/prod** apps referencing this repo now use `targetRevision: main`.
- Removed feature branch references (e.g., `feature/tooling-apps-config`) in dev apps.

## Notes

- Helm chart versions remain pinned and unchanged.
- If prod should pin release tags/SHAs, add automation to bump `targetRevision`
  per release.

## Verification

```bash
rg -n "targetRevision:" gitops/argocd/apps/{dev,test,staging,prod}/*.yaml
```
