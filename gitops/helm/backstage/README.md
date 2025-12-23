# Backstage Helm Deployment

Backstage is the developer portal (service catalog, docs, scaffolding) for the IDP.

```
gitops/helm/backstage/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Used by `gitops/argocd/apps/<env>/backstage.yaml` to supply environment-specific overrides (base URL, SSO, catalog settings).
