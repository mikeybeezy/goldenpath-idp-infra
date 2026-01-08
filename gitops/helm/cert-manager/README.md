---
id: HELM_CERT_MANAGER
title: cert-manager Helm Chart (Values)
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
  observability_tier: bronze
schema_version: 1
relates_to:
  - 09_ARCHITECTURE
  - ADR-0070
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
  - chart:cert-manager
supported_until: 2028-01-01
breaking_change: false
---

# cert-manager Helm Deployment

cert-manager provisions and renews TLS certificates for ingress controllers and workloads.

```
gitops/helm/cert-manager/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Env-specific Argo CD Applications (e.g., `gitops/argocd/apps/dev/cert-manager.yaml`) reference these value files with `$values/gitops/helm/cert-manager/values/<env>.yaml`.
