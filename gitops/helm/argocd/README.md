---
id: HELM_ARGOCD
title: Argo CD Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
- chart:argo-cd
risk_profile:
  production_impact: high
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- ADR-0001
- BOOTSTRAP_README
---

# Argo CD Deployment

Argo CD is the GitOps controller responsible for syncing all other Helm/Kustomize manifests. Managing it like any other Helm app keeps its installation declarative.

```
gitops/helm/argocd/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Whether Argo CD is installed via a bootstrap script or a future Argo “app-of-apps”, each environment reuses the matching value file (`gitops/helm/argocd/values/<env>.yaml`) for ingress, RBAC, and SSO overrides.
