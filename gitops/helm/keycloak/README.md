---
id: HELM_KEYCLOAK
title: Keycloak Helm Chart (Values)
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
  - 06_IDENTITY_AND_ACCESS
  - ADR-0005-app-keycloak-as-identity-provider-for-human-sso
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
  - chart:keycloak
  - image:keycloak
supported_until: 2028-01-01
breaking_change: false
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
