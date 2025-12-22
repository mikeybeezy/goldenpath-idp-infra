# Keycloak Helm Deployment

Keycloak provides OIDC identity for Backstage, Kong, and platform workloads.

```
gitops/helm/keycloak/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: uses the Bitnami Keycloak chart repo.
- `helmrelease.yaml`: installs Keycloak into the `keycloak` namespace.
- `values/<env>.yaml`: configure admin credentials, ingress, database/storage per environment.
