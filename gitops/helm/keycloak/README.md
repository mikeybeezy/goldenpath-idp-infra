# Keycloak Helm Deployment

Keycloak provides OIDC identity for Backstage, Kong, and platform workloads.

```
gitops/helm/keycloak/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Referenced by Argo CD (`gitops/argocd/apps/<env>/keycloak.yaml`) when pulling the Bitnami chart.
