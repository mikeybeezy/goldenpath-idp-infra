# Fluent Bit Helm Deployment

Fluent Bit is the DaemonSet that ships logs from every node/pod to Loki (and optionally other destinations like Datadog).

```
gitops/helm/fluent-bit/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications load these value files via `$values/gitops/helm/fluent-bit/values/<env>.yaml`.
