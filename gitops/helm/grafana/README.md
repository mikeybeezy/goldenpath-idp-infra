# Grafana Helm Deployment

Grafana provides dashboards and alert visualization for the platform. This chart installs Grafana into the `grafana` namespace and uses environment-specific values so each cluster can point to the right datasources and credentials.

```
gitops/helm/grafana/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Referenced from `gitops/argocd/apps/<env>/grafana.yaml` using `$values/gitops/helm/grafana/values/<env>.yaml`.
