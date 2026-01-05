---
id: HELM_PROMETHEUS
title: Prometheus Reference Chart (Deprecated)
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
  - HELM_KUBE_PROMETHEUS_STACK
---

# Prometheus Helm Deployment (Deprecated)

Prometheus is now deployed via the `kube-prometheus-stack` bundle. This chart
is retained only for reference and should not be deployed in new environments.

```
gitops/helm/prometheus/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Use `gitops/argocd/apps/<env>/kube-prometheus-stack.yaml` instead.
