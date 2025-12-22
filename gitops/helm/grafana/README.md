# Grafana Helm Deployment

Grafana provides dashboards and alert visualization for the platform. This chart installs Grafana into the `grafana` namespace and uses environment-specific values so each cluster can point to the right datasources and credentials.

```
gitops/helm/grafana/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: references the official Grafana Helm repository.
- `helmrelease.yaml`: defines how Argo CD (or Flux) deploys the chart.
- `values/<env>.yaml`: per-environment overrides (admin password, datasources, ingress).
