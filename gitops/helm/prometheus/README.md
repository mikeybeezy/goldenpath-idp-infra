# Prometheus Helm Deployment

Prometheus scrapes metrics from workloads, exporters, and the platform control plane.

```
gitops/helm/prometheus/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications (`gitops/argocd/apps/<env>/prometheus.yaml`) include the matching value file via `$values/gitops/helm/prometheus/values/<env>.yaml`.
