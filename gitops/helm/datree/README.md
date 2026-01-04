---
id: HELM_DATREE
title: Datree Admission Webhook (Values)
type: documentation
category: gitops
version: 1.0
owner: platform-team
status: active
dependencies:
  - chart:datree
  - image:datree
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
  - ADR-0004
  - ADR-0033
---

# Datree Admission Webhook

Datree enforces Kubernetes policies at admission time to catch any manifests that slip past CI. The Helm chart installs Datree’s validating webhook into the `datree-system` namespace.

```
gitops/helm/datree/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications reference these files when installing the Datree admission webhook.
