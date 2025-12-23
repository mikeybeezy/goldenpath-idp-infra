# Kong Helm Deployment

Kong acts as the platform’s ingress/API gateway, handling routing, auth, and policies for north-south traffic.

```
gitops/helm/kong/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications under `gitops/argocd/apps/<env>/kong.yaml` reference these value files via `$values/gitops/helm/kong/values/<env>.yaml`.
