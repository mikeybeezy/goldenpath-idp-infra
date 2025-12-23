# External Secrets Helm Deployment

External Secrets Operator syncs data from AWS Secrets Manager (and future Vault integration) into Kubernetes secrets.

```
gitops/helm/external-secrets/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications (such as `gitops/argocd/apps/dev/external-secrets.yaml`) pull the relevant file via `$values/gitops/helm/external-secrets/values/<env>.yaml`.
