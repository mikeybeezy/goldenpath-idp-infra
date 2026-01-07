---
id: HELM_EXTERNAL_SECRETS
title: External Secrets Helm Chart (Values)
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
  - ADR-0006
  - 06_IDENTITY_AND_ACCESS
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: delivery
status: active
version: 1.0
dependencies:
  - chart:external-secrets
  - image:external-secrets
supported_until: 2028-01-01
breaking_change: false
---

# External Secrets Helm Deployment

External Secrets Operator syncs data from AWS Secrets Manager (and future Vault integration) into Kubernetes secrets.

```
gitops/helm/external-secrets/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications (such as `gitops/argocd/apps/dev/external-secrets.yaml`) pull the relevant file via `$values/gitops/helm/external-secrets/values/<env>.yaml`.
