# Kube Prometheus Stack Deployment

This bundle replaces the standalone Prometheus, Grafana, and Alertmanager
charts. Values are environment-specific and referenced by Argo CD Applications.

```
gitops/helm/kube-prometheus-stack/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Referenced from `gitops/argocd/apps/<env>/kube-prometheus-stack.yaml` using
`$values/gitops/helm/kube-prometheus-stack/values/<env>.yaml`.
