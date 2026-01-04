---
id: README
title: Cluster Autoscaler Helm Deployment
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

# Cluster Autoscaler Helm Deployment

Cluster Autoscaler adjusts the EKS node group size based on pending pods.

ServiceAccount is created by Terraform with IRSA; Helm values set `serviceAccount.create=false`.

```
gitops/helm/cluster-autoscaler/
└── values/
    └── dev.yaml
```

Referenced by Argo CD (`gitops/argocd/apps/<env>/cluster-autoscaler.yaml`).
