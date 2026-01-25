<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 04_REPO_STRUCTURE
title: Repository Structure & Workflow
type: adr
applies_to:
  - infra
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-2
  potential_savings_hours: 1.0
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - 12_GITOPS_AND_CICD
  - 17_BUILD_RUN_FLAGS
  - 18_BACKSTAGE_MVP
category: architecture
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Repository Structure & Workflow

This document explains how the Golden Path IDP repository is organized and why each area exists. Use it as the canonical reference when adding new platform capabilities.

## ASCII Overview

```text

goldenpath-idp-infra/
├── bootstrap/
│   └── 10_bootstrap/
│       └── goldenpath-idp-bootstrap.sh
├── compliance/
│   └── datree/
├── docs/
│   ├── 01_GOVERNANCE.md
│   ├── 02_GOVERNANCE_MODEL.md
│   ├── 03_GOVERNANCE_BACKSTAGE.md
│   ├── 04_REPO_STRUCTURE.md
│   ├── 05_OBSERVABILITY_DECISIONS.md
│   └── 07_REPO_DECOUPLING_OPTIONS.md
├── envs/
│   ├── dev/
│   ├── test/
│   ├── staging/
│   └── prod/
├── gitops/
│   ├── helm/
│   │   ├── kong/
│   │   │   ├── values/
│   │   │   │   ├── dev.yaml
│   │   │   │   ├── test.yaml
│   │   │   │   ├── staging.yaml
│   │   │   │   └── prod.yaml
│   │   ├── grafana/
│   │   ├── loki/
│   │   ├── alertmanager/
│   │   ├── fluent-bit/
│   │   ├── keycloak/
│   │   ├── backstage/
│   │   ├── datree/
│   │   └── argocd/
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
├── scripts/
│   └── resolve-cluster-name.sh
├── Makefile
├── CONTRIBUTING.md
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

- `helm/`: Helm values for Kong, kube-prometheus-stack, Loki, Fluent Bit, Keycloak, Backstage, Datree, Argo CD, Argo Rollouts. These define workload configuration consumed by Argo CD Applications.
- `kustomize/`: base manifests plus environment-specific overlays so Argo CD can reconcile per environment.

### `compliance/datree/`

Datree policies and documentation describing how Kubernetes manifest checks run in CI. Keeps policy-as-code colocated with repo.

### `docs/`

Governance and capability documentation ordered numerically for easy navigation. This file (`04_REPO_STRUCTURE.md`) documents layout and workflow.

Notable docs:

- `docs/00-foundations/18_BACKSTAGE_MVP.md` – first‑app checklist to validate CI → GitOps → Kong.
- `docs/40-delivery/12_GITOPS_AND_CICD.md` – CI/CD overview, runner requirements, and bootstrap notes.
- `docs/40-delivery/17_BUILD_RUN_FLAGS.md` – canonical list of runtime flags for build/bootstrap/teardown.

### Root Files

- `eksctl-template.yaml`: starter config for creating EKS clusters via eksctl.
- `Makefile`: wraps Terraform commands (`make init/plan/apply ENV=<env>`).
- `CONTRIBUTING.md`: branch strategy and branch protection checklist.

### `scripts/`

Helper scripts used by CI and local runs.

- `scripts/resolve-cluster-name.sh`: computes the effective EKS cluster name

  from `terraform.tfvars` (adds `-<build_id>` for ephemeral runs).

## Workflow Summary

1. **Infrastructure (VPC, cluster, etc.)** – Terraform modules in `modules/` + `envs/<env>` provision AWS networking, EKS clusters, IAM roles.
2. **Bootstrap (cluster bring-up)** – `bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh` installs Argo CD, core add-ons, and platform apps in a deterministic order.
3. **Tooling Deployments (Kong, kube-prometheus-stack, Loki, Fluent Bit, Keycloak, Backstage)** – Helm charts/Kustomize manifests under `gitops/` deploy the actual workloads via Argo CD.
4. **Tooling Configuration (Kong APIs, Grafana dashboards, Keycloak realms)** – Terraform provider modules in `idp-tooling/` manage API-level config so changes are versioned and promoted top-to-bottom.

CI workflow stub:

- `/.github/workflows/ci-bootstrap.yml` stages infra apply, bootstrap, and teardown

  for ephemeral runs. It resolves the effective cluster name when not provided.

This separation keeps infrastructure, workloads, and configuration decoupled but fully code-driven, enabling safe promotions across environments.

## Application vs Tooling Layout

- **Kustomize (cluster plumbing)** – `gitops/kustomize/bases` defines shared namespaces/cluster objects; `gitops/kustomize/overlays/<env>` layers environment-specific tweaks. Used for base cluster resources.

- **Helm (platform tooling & apps)** – `gitops/helm/<component>/` contains:
  - `values/`: environment-specific Helm values consumed by Argo CD Applications.
  - `values/<env>.yaml`: environment-specific overrides (dev/test/staging/prod). Reference these from Argo `valueFiles` so each env gets tailored settings (URLs, replicas, secrets, etc.).

This separation keeps cluster scaffolding (namespaces, CRDs) in Kustomize while Helm handles workloads (Kong, Grafana, Loki, Keycloak, Backstage). GitOps controllers reconcile both trees so every environment stays consistent.
