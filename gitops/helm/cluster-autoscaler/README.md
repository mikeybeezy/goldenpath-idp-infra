---
id: HELM_CLUSTER_AUTOSCALER
title: Cluster Autoscaler Helm Chart (Values)
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
  - MODULE_AWS_IAM
  - ADR-0031
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
  - chart:cluster-autoscaler
  - module:aws_iam
supported_until: 2028-01-01
breaking_change: false
---

# Cluster Autoscaler Helm Deployment

Cluster Autoscaler adjusts the EKS node group size based on pending pods.

ServiceAccount is created by Terraform with IRSA; Helm values set `serviceAccount.create=false`.

```
gitops/helm/cluster-autoscaler/
└── values/
    └── dev.yaml
```

Referenced by Argo CD (`gitops/argocd/apps/<env>/cluster-autoscaler.yaml`).
