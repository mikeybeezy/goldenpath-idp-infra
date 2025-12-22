# Fluent Bit Helm Deployment

Fluent Bit is the DaemonSet that ships logs from every node/pod to Loki (and optionally other destinations like Datadog).

```
gitops/helm/fluent-bit/
├── helmrepository.yaml
├── helmrelease.yaml
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

- `helmrepository.yaml`: references the Fluent Helm repo.
- `helmrelease.yaml`: deploys Fluent Bit into the `monitoring` namespace.
- `values/<env>.yaml`: set log outputs and filters per environment (Loki URL, extra outputs).
