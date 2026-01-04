---
id: HELM_ALERTMANAGER
title: Alertmanager Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
- chart:kube-prometheus-stack
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 18_BACKSTAGE_MVP
---

# Alertmanager Helm Deployment (Deprecated)

Alertmanager is now deployed via the `kube-prometheus-stack` bundle. This chart
is retained only for reference and should not be deployed in new environments.

```
gitops/helm/alertmanager/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Use `gitops/argocd/apps/<env>/kube-prometheus-stack.yaml` instead.
