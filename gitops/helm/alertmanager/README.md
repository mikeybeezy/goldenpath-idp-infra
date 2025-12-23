# Alertmanager Helm Deployment

Alertmanager handles routing of Prometheus/Loki alerts (email, Slack, PagerDuty, etc.).

```
gitops/helm/alertmanager/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Application manifests (`gitops/argocd/apps/<env>/…`) reference these value files.
