---
id: GITOPS_KUSTOMIZE_BASES_README
title: Kustomize Bases
type: documentation
category: gitops
version: '1.0'
owner: platform-team
status: active
dependencies: []
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

# Kustomize Bases

This directory defines cluster-wide resources shared across environments (namespaces, base RBAC, etc.).

```
gitops/kustomize/bases/
├── kustomization.yaml
└── namespaces.yaml
```

- `namespaces.yaml`: declares core namespaces (Kong, Grafana, Loki, monitoring, Keycloak, Backstage).
- `kustomization.yaml`: bundles those resources so overlays can import them.
