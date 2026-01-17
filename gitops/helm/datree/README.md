---
id: HELM_DATREE
title: Datree Admission Webhook (Values)
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
  - ADR-0004-platform-datree-policy-as-code-in-ci
  - ADR-0033-platform-ci-orchestrated-modes
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
  - chart:datree
  - image:datree
supported_until: 2028-01-01
breaking_change: false
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
