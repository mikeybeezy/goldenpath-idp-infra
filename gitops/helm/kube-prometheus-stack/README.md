---
id: README
title: Kube Prometheus Stack Deployment
type: documentation
owner: platform-team
status: active
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
relates_to: []
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
