---
id: README
title: Keycloak Helm Deployment
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

# Keycloak Helm Deployment

Keycloak provides OIDC identity for Backstage, Kong, and platform workloads.

```
gitops/helm/keycloak/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Referenced by Argo CD (`gitops/argocd/apps/<env>/keycloak.yaml`) when pulling the Bitnami chart.
