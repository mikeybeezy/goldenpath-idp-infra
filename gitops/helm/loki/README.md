---
id: HELM_LOKI
title: Loki Helm Chart (Values)
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
  - HELM_FLUENT_BIT
  - HELM_KUBE_PROMETHEUS_STACK
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
  - chart:loki
  - image:loki
supported_until: 2028-01-01
breaking_change: false
---

# Loki Helm Deployment

The Loki stack provides log storage (Loki) plus promtail agents for scraping.
The platform default is **Single Binary** mode in the `monitoring` namespace.

```
gitops/helm/loki/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Used by Argo CD Applications (`gitops/argocd/apps/<env>/loki.yaml`) via `$values/gitops/helm/loki/values/<env>.yaml`.
