# Kong Helm Deployment

Kong acts as the platform’s ingress/API gateway, handling routing, auth, and policies for north-south traffic.

```
gitops/helm/kong/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: references the Kong Helm repo (`charts.konghq.com`).
- `helmrelease.yaml`: workload definition reconciled by GitOps (Argo/Flux).
- `values/<env>.yaml`: override proxy type, plugins, ingress settings per environment.
