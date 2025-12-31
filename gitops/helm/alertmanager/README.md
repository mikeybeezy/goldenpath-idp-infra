# Alertmanager Helm Deployment (Deprecated)

Alertmanager is now deployed via the `kube-prometheus-stack` bundle. This chart
is retained only for reference and should not be deployed in new environments.

```
gitops/helm/alertmanager/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Use `gitops/argocd/apps/<env>/kube-prometheus-stack.yaml` instead.
