---
id: HELM_CERT_MANAGER
title: cert-manager Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
- chart:cert-manager
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 09_ARCHITECTURE
- ADR-0070
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
