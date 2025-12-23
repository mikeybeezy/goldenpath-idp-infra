# Loki Helm Deployment

The Loki stack provides log storage (Loki) plus promtail agents for scraping.

```
gitops/helm/loki/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Used by Argo CD Applications (`gitops/argocd/apps/<env>/loki.yaml`) via `$values/gitops/helm/loki/values/<env>.yaml`.
