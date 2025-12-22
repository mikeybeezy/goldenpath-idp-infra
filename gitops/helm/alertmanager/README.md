# Alertmanager Helm Deployment

Alertmanager handles routing of Prometheus/Loki alerts (email, Slack, PagerDuty, etc.).

```
gitops/helm/alertmanager/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: uses the Prometheus Community chart repo.
- `helmrelease.yaml`: deploys Alertmanager into the `monitoring` namespace.
- `values/<env>.yaml`: configure receivers/routes per environment (e.g., Slack channel, email).
