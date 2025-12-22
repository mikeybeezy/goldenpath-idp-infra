# Kustomize Bases

This directory defines cluster-wide resources shared across environments (namespaces, base RBAC, etc.).

```
gitops/kustomize/bases/
├── kustomization.yaml
└── namespaces.yaml
```

- `namespaces.yaml`: declares core namespaces (Kong, Grafana, Loki, monitoring, Keycloak, Backstage).
- `kustomization.yaml`: bundles those resources so overlays can import them.
