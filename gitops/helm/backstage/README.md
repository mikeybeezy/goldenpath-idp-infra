---
id: README
title: Backstage Helm Deployment
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

# Backstage Helm Deployment

Backstage is the developer portal (service catalog, docs, scaffolding) for the IDP.

```
gitops/helm/backstage/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Used by `gitops/argocd/apps/<env>/backstage.yaml` to supply environment-specific overrides (base URL, SSO, catalog settings).
