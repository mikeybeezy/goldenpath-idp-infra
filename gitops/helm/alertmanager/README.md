---
id: HELM_ALERTMANAGER
title: Alertmanager Helm Chart (Values)
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
  - 18_BACKSTAGE_MVP
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
supported_until: 2028-01-01
breaking_change: false
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
