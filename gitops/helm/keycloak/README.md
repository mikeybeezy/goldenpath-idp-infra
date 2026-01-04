---
id: HELM_KEYCLOAK
title: Keycloak Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
  - chart:keycloak
  - image:keycloak
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
relates_to:
  - 06_IDENTITY_AND_ACCESS
  - ADR-0005
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
