# Backstage Helm Deployment

Backstage is the developer portal (service catalog, docs, scaffolding) for the IDP.

```
gitops/helm/backstage/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: references the Backstage chart repo.
- `helmrelease.yaml`: installs Backstage into the `backstage` namespace with optional Postgres.
- `values/<env>.yaml`: customize base URL, auth providers, catalog locations per environment.
