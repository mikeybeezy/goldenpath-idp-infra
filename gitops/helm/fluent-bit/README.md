---
id: README
title: Fluent Bit Helm Deployment
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
