---
id: HELM_BACKSTAGE
title: Backstage Helm Chart (Values)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 18_BACKSTAGE_MVP
  - ADR-0008
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
  - image:backstage
supported_until: 2028-01-01
breaking_change: false
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
