---
id: HELM_KUBE_PROMETHEUS_STACK
title: Kube Prometheus Stack Helm Chart (Values)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - HELM_LOKI
  - HELM_FLUENT_BIT
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
  - chart:kube-prometheus-stack
  - image:prometheus
  - image:grafana
supported_until: 2028-01-01
breaking_change: false
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
