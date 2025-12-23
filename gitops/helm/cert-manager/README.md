# cert-manager Helm Deployment

cert-manager provisions and renews TLS certificates for ingress controllers and workloads.

```
gitops/helm/cert-manager/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Env-specific Argo CD Applications (e.g., `gitops/argocd/apps/dev/cert-manager.yaml`) reference these value files with `$values/gitops/helm/cert-manager/values/<env>.yaml`.
