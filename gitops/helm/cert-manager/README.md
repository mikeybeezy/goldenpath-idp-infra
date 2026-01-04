---
id: README
title: cert-manager Helm Deployment
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
