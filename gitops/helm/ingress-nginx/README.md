# ingress-nginx Helm Deployment

The ingress-nginx controller terminates TLS and routes north-south HTTP traffic before it reaches Kong or internal services.

```
gitops/helm/ingress-nginx/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Each Argo CD Application (`gitops/argocd/apps/<env>/ingress-nginx.yaml`) references the matching value file via `$values/gitops/helm/ingress-nginx/values/<env>.yaml`.
