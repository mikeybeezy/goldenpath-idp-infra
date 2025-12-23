# Datree Admission Webhook

Datree enforces Kubernetes policies at admission time to catch any manifests that slip past CI. The Helm chart installs Datree’s validating webhook into the `datree-system` namespace.

```
gitops/helm/datree/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications reference these files when installing the Datree admission webhook.
