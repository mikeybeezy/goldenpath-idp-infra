# Repository Structure & Workflow

This document explains how the Golden Path IDP repository is organized and why each area exists. Use it as the canonical reference when adding new platform capabilities.

## ASCII Overview

```
goldenpath-idp-infra/
├── bootstrap-scripts/
│   └── helm-bootstrap.sh
├── compliance/
│   └── datree/
├── docs/
│   ├── 01_GOVERNANCE.md
│   ├── 02_GOVERNANCE_MODEL.md
│   ├── 03_GOVERNANCE_BACKSTAGE.md
│   ├── 04_REPO_STRUCTURE.md
│   └── 05_OBSERVABILITY_DECISIONS.md
├── envs/
│   ├── dev/
│   ├── test/
│   ├── staging/
│   └── prod/
├── gitops/
│   ├── helm/
│   │   ├── kong/
│   │   │   ├── helmrepository.yaml
│   │   │   ├── helmrelease.yaml
│   │   │   └── values/
│   │   │       ├── dev.yaml
│   │   │       ├── test.yaml
│   │   │       ├── staging.yaml
│   │   │       └── prod.yaml
│   │   ├── grafana/
│   │   ├── loki/
│   │   ├── alertmanager/
│   │   ├── fluent-bit/
│   │   ├── keycloak/
│   │   └── backstage/
│   └── kustomize/
│       ├── bases/
│       │   ├── kustomization.yaml
│       │   └── namespaces.yaml
│       └── overlays/
│           ├── dev/
│           │   └── kustomization.yaml
│           ├── test/
│           ├── staging/
│           └── prod/
├── idp-tooling/
│   ├── kong/
│   ├── grafana-config/
│   ├── keycloak/
│   ├── monitoring-config/
│   │   ├── grafana/
│   │   ├── alertmanager/
│   │   └── fluent-bit/
│   ├── backstage-config/
│   └── aws-secrets-manager/
├── modules/
├── Makefile
└── eksctl-template.yaml
```

## Folder Details

### `envs/`
Per-environment Terraform stacks (dev/test/staging/prod). Each directory composes the shared modules to provision AWS infrastructure consistently.

### `modules/`
Reusable Terraform modules for networking, compute, and other shared infra components consumed by `envs/*`.

### `idp-tooling/`
Terraform provider modules that configure platform tooling **after** it is deployed:
- `kong/`: defines Kong services, routes, and plugins.
- `grafana-config/`: manages dashboards, datasources, and alert rules via the Grafana provider.
- `keycloak/`: automates realms, clients, and roles.
- `monitoring-config/`: holds provider-driven config for Grafana, Alertmanager, and Fluent Bit pipelines.
- `backstage-config/`: manages Backstage catalog entities once the service is running.
- `aws-secrets-manager/`: codifies secrets, policies, and rotation settings exposed through External Secrets.

### `gitops/`
GitOps workloads that install tooling inside the cluster:
- `helm/`: chart releases (or HelmRelease manifests) for Kong, Grafana, Loki, Alertmanager, Fluent Bit, Keycloak, Backstage. These define the workloads and namespaces.
- `kustomize/`: base manifests plus environment-specific overlays so Argo CD/Flux can reconcile per environment.

### `compliance/datree/`
Datree policies and documentation describing how Kubernetes manifest checks run in CI. Keeps policy-as-code colocated with repo.

### `docs/`
Governance and capability documentation ordered numerically for easy navigation. This file (`04_REPO_STRUCTURE.md`) documents layout and workflow.

### Root Files
- `eksctl-template.yaml`: starter config for creating EKS clusters via eksctl.
- `Makefile`: wraps Terraform commands (`make init/plan/apply ENV=<env>`).

## Workflow Summary

1. **Infrastructure (VPC, cluster, etc.)** – Terraform modules in `modules/` + `envs/<env>` provision AWS networking, EKS clusters, IAM roles.
2. **Tooling Deployments (Kong, Grafana, Loki, Fluent Bit, Keycloak, Backstage)** – Helm charts/Kustomize manifests under `gitops/` deploy the actual workloads via Argo CD/Flux.
3. **Tooling Configuration (Kong APIs, Grafana dashboards, Keycloak realms)** – Terraform provider modules in `idp-tooling/` manage API-level config so changes are versioned and promoted top-to-bottom.

This separation keeps infrastructure, workloads, and configuration decoupled but fully code-driven, enabling safe promotions across environments.

## Application vs Tooling Layout

- **Kustomize (cluster plumbing)** – `gitops/kustomize/bases` defines shared namespaces/cluster objects; `gitops/kustomize/overlays/<env>` layers environment-specific tweaks. Used for base cluster resources.

- **Helm (platform tooling & apps)** – `gitops/helm/<component>/` contains:
  - `helmrepository.yaml`: source chart repo.
  - `helmrelease.yaml`: deployment spec consumed by GitOps controller.
  - `values/<env>.yaml`: environment-specific overrides (dev/test/staging/prod). Reference these from HelmRelease (Flux `valuesFrom` or Argo `valueFiles`) so each env gets tailored settings (URLs, replicas, secrets, etc.).

This separation keeps cluster scaffolding (namespaces, CRDs) in Kustomize while Helm handles workloads (Kong, Grafana, Loki, Keycloak, Backstage). GitOps controllers reconcile both trees so every environment stays consistent.
