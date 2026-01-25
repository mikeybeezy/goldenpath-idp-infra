<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 42_APP_EXAMPLE_DEPLOYMENTS
title: App Example Deployments (Argo CD + Helm + Kustomize)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 12_GITOPS_AND_CICD
  - 29_CD_DEPLOYMENT_CONTRACT
  - 42_APP_TEMPLATE_LIVING
  - ADR-0171-platform-application-packaging-strategy
  - CL-0027-app-example-deployments
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# App Example Deployments (Argo CD + Helm + Kustomize)

Doc contract:

- Purpose: Describe how example apps are scaffolded and packaged for Argo CD, Helm, and Kustomize.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/42_APP_TEMPLATE_LIVING.md, docs/40-delivery/12_GITOPS_AND_CICD.md, docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md

## Summary

Each app under `apps/` follows a deterministic, repeatable structure so it can
be deployed via Argo CD using either Helm or Kustomize, while preserving the
Backstage scaffold templates (`{{ values.* }}`) for Golden Path generation.

## Deterministic, recursive approach

1) Keep the Backstage scaffold templates at the app root (mirrors fast-api template).
2) Add a per-app dashboard (`dashboards/configmap-dashboard.yaml`).
3) Create deployable packaging:
   - `deploy/helm/` (Helm chart with `.Values` templating).
   - `deploy/kustomize/` (base + env overlays with concrete example values).
4) Use Argo CD to point at either the Helm chart or the Kustomize overlay.

This pattern is repeated for every app in `apps/` to make deployment consistent.

## Example app structure

```
apps/<example-app>/
├─ README.md
├─ catalog-info.yaml
├─ deployment.yaml
├─ service.yaml
├─ ingress.yaml
├─ servicemonitor.yaml
├─ serviceaccount.yaml
├─ rbac.yaml
├─ networkpolicy.yaml
├─ dashboards/
│  └─ configmap-dashboard.yaml
├─ deploy/
│  ├─ helm/
│  │  ├─ Chart.yaml
│  │  ├─ values.yaml
│  │  └─ templates/
│  │     └─ *.yaml
│  └─ kustomize/
│     ├─ base/
│     │  ├─ kustomization.yaml
│     │  └─ *.yaml
│     └─ overlays/
│        ├─ dev/
│        ├─ test/
│        ├─ staging/
│        └─ prod/
```

## Argo CD deployment examples

### Kustomize (recommended for examples)

Create an Argo CD Application that points to an env overlay:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: dev-sample-stateless-app
  namespace: argocd
spec:
  project: default
  destination:
    namespace: apps-sample-stateless
    server: https://kubernetes.default.svc
  source:
    repoURL: <https://github.com/mikeybeezy/goldenpath-idp-infra.git>
    targetRevision: development
    path: apps/sample-stateless-app/deploy/kustomize/overlays/dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Helm

Create an Argo CD Application pointing at the Helm chart:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: dev-sample-stateless-app-helm
  namespace: argocd
spec:
  project: default
  destination:
    namespace: apps-sample-stateless
    server: https://kubernetes.default.svc
  source:
    repoURL: <https://github.com/mikeybeezy/goldenpath-idp-infra.git>
    targetRevision: development
    path: apps/sample-stateless-app/deploy/helm
    helm:
      valueFiles:
        - values.yaml
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Helm env-specific values (optional)

By default, example charts ship a single `values.yaml`. If you need per-env
overrides, add `values-<env>.yaml` files under `deploy/helm/` and update the
Argo CD Application to reference them, for example:

```yaml
source:
  repoURL: <https://github.com/mikeybeezy/goldenpath-idp-infra.git>
  targetRevision: development
  path: apps/sample-stateless-app/deploy/helm
  helm:
    valueFiles:
      - values.yaml
      - values-dev.yaml
```

## Example apps in this repo

- `apps/sample-stateless-app/`:
  - Stateless example using nginx.
  - Includes dashboard + ServiceMonitor.
- `apps/stateful-app/`:
  - StatefulSet + PVC + resource quota + EFS scaffolds.
  - Includes dashboard + ServiceMonitor.
- `apps/Wordpress-on-EFS/`:
  - WordPress example with EFS scaffolds.
  - Includes dashboard + ServiceMonitor.

Note: `apps/fast-api-app-template/` remains the primary Backstage scaffold
template. It does not include deployable Helm/Kustomize packaging yet.

## Argo CD app manifests in this repo

Example Argo CD Applications are provided under `gitops/argocd/apps/<env>/`:

- `sample-stateless-app.yaml`
- `stateful-app.yaml`
- `wordpress-efs.yaml`

Defaults:

- `dev` apps point at `targetRevision: development`.
- `test`, `staging`, `prod` apps point at `targetRevision: main`.

## Best-practice recommendations

- Use a dedicated namespace per app (`apps-<app>`), with ResourceQuota for stateful workloads.
- Keep `ServiceMonitor` labels aligned (`release: kube-prometheus-stack`) to ensure scrape coverage.
- Use consistent platform labels (`platform.goldenpath.dev/*`) for env, team, and build_id.
- Prefer `ReadWriteOnce` PVCs for most stateful apps; use EFS (`ReadWriteMany`) for shared storage.
- Keep ingress annotations minimal and explicit; avoid wildcard paths unless required.
- Make dashboards opt-out only in exceptional cases; default to shipping one per app.
