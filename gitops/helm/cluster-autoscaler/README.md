# Cluster Autoscaler Helm Deployment

Cluster Autoscaler adjusts the EKS node group size based on pending pods.

ServiceAccount is created by Terraform with IRSA; Helm values set `serviceAccount.create=false`.

```
gitops/helm/cluster-autoscaler/
└── values/
    └── dev.yaml
```

Referenced by Argo CD (`gitops/argocd/apps/<env>/cluster-autoscaler.yaml`).
