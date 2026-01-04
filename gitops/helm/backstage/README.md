---
id: HELM_BACKSTAGE
title: Backstage Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
- image:backstage
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 18_BACKSTAGE_MVP
- ADR-0008
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
