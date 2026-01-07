---
id: HELM_FLUENT_BIT
title: Fluent Bit Helm Chart (Values)
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
schema_version: 1
relates_to:
  - HELM_LOKI
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
  - chart:fluent-bit
  - image:fluent-bit
supported_until: 2028-01-01
breaking_change: false
---

# Fluent Bit Helm Deployment

Fluent Bit is the DaemonSet that ships logs from every node/pod to Loki (and optionally other destinations like Datadog).

```
gitops/helm/fluent-bit/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications load these value files via `$values/gitops/helm/fluent-bit/values/<env>.yaml`.
