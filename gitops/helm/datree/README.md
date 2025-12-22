# Datree Admission Webhook

Datree enforces Kubernetes policies at admission time to catch any manifests that slip past CI. The Helm chart installs Datree’s validating webhook into the `datree-system` namespace.

```
gitops/helm/datree/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: points to Datree’s chart repo.
- `helmrelease.yaml`: deploys the admission webhook with failurePolicy=Fail by default.
- `values/<env>.yaml`: set `datreeToken` and environment-specific behavior (namespaces to skip, policy bundles, etc.).
