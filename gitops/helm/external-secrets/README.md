---
id: HELM_EXTERNAL_SECRETS
title: External Secrets Helm Chart (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
- chart:external-secrets
- image:external-secrets
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
- ADR-0006
- 06_IDENTITY_AND_ACCESS
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
