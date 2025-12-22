# Loki Helm Deployment

The Loki stack provides log storage (Loki) plus promtail agents for scraping.

```
gitops/helm/loki/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: points to Grafana’s chart repo (used for Loki stack).
- `helmrelease.yaml`: installs `loki-stack` (Loki + promtail) into the `loki` namespace.
- `values/<env>.yaml`: adjust storage, retention, promtail targets for each environment.
