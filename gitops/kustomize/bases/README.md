---
id: GITOPS_KUSTOMIZE_BASES_README
title: Kustomize Bases
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
relates_to: []
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
version: '1.0'
dependencies: []
supported_until: 2028-01-01
breaking_change: false
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
