# Argo CD Deployment

Argo CD is the GitOps controller responsible for syncing all other Helm/Kustomize manifests. Managing it like any other Helm app keeps its installation declarative.

```
gitops/helm/argocd/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Whether Argo CD is installed via a bootstrap script or a future Argo “app-of-apps”, each environment reuses the matching value file (`gitops/helm/argocd/values/<env>.yaml`) for ingress, RBAC, and SSO overrides.
