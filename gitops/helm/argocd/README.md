---
id: HELM_ARGOCD
title: Argo CD Helm Chart (Values)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0001-platform-argocd-as-gitops-operator
  - BOOTSTRAP_README
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: delivery
status: active
version: 1.0
dependencies:
  - chart:argo-cd
supported_until: 2028-01-01
breaking_change: false
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
