---
id: HELM_KUBE_PROMETHEUS_STACK
title: Kube Prometheus Stack Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
  - chart:kube-prometheus-stack
  - image:prometheus
  - image:grafana
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
  - HELM_LOKI
  - HELM_FLUENT_BIT
---

# Kube Prometheus Stack Deployment

This bundle replaces the standalone Prometheus, Grafana, and Alertmanager
charts. Values are environment-specific and referenced by Argo CD Applications.

```
gitops/helm/kube-prometheus-stack/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Referenced from `gitops/argocd/apps/<env>/kube-prometheus-stack.yaml` using
`$values/gitops/helm/kube-prometheus-stack/values/<env>.yaml`.
