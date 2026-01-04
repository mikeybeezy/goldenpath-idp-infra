---
id: README
title: Loki Helm Deployment
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
