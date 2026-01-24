---
id: CL-0175
title: Tooling Dashboards ArgoCD Application
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
relates_to:
  - CL-0174-kong-prometheus-metrics
  - 20_TOOLING_APPS_MATRIX
---

## Summary

Added ArgoCD Application to deploy Grafana tooling dashboards via the sidecar pattern.

## Problem

Grafana dashboards for platform tooling existed as ConfigMaps in the repository but were not being deployed:
- `gitops/helm/tooling-dashboards/kong-dashboard.yaml`
- `gitops/helm/tooling-dashboards/argocd-dashboard.yaml`
- `gitops/helm/tooling-dashboards/backstage-dashboard.yaml`
- `gitops/helm/tooling-dashboards/keycloak-dashboard.yaml`

The Kustomization was defined but no ArgoCD Application referenced it, so the dashboards never deployed to the cluster.

## Changes

### ArgoCD Applications Created

| Environment | File | Target Branch |
|-------------|------|---------------|
| dev | `gitops/argocd/apps/dev/tooling-dashboards.yaml` | development |
| staging | `gitops/argocd/apps/staging/tooling-dashboards.yaml` | staging |
| prod | `gitops/argocd/apps/prod/tooling-dashboards.yaml` | main |
| test | `gitops/argocd/apps/test/tooling-dashboards.yaml` | test |

### Configuration

```yaml
spec:
  source:
    repoURL: https://github.com/mikeybeezy/goldenpath-idp-infra.git
    path: gitops/helm/tooling-dashboards
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Sync Wave

Set to `sync-wave: "50"` to ensure dashboards deploy after:
- Core infrastructure components
- Monitoring stack (kube-prometheus-stack with Grafana)
- Target namespaces exist (kong-system, argocd, backstage, keycloak)

## Dashboards Deployed

| Dashboard | Namespace | Description |
|-----------|-----------|-------------|
| Kong Golden Signals | kong-system | API gateway RED metrics, latency, bandwidth |
| ArgoCD Golden Signals | argocd | GitOps health, sync status, app counts |
| Backstage Golden Signals | backstage | Developer portal metrics |
| Keycloak Golden Signals | keycloak | Identity provider metrics |

## Grafana Sidecar Pattern

Dashboards use the Grafana sidecar auto-discovery pattern:
- Label: `grafana_dashboard: "1"`
- Annotation: `k8s-sidecar-target-directory: "/tmp/dashboards/tooling"`
- Grafana sidecar scans all namespaces (`searchNamespace: ALL`)

## Bootstrap Integration

The new ArgoCD apps are automatically included in platform bootstrap:

| Bootstrap Method | Mechanism |
|-----------------|-----------|
| Terraform | `fileset(path_to_app_manifests, "**/*.{yaml,yml}")` |
| Shell script | `for app_file in "${apps_dir}"/*.yaml` |

Both methods iterate over all YAML files in `gitops/argocd/apps/{env}/` and apply them.

## Verification

```bash
# Check ArgoCD app exists
kubectl get application dev-tooling-dashboards -n argocd

# Check ConfigMaps deployed
kubectl get configmap -l grafana_dashboard=1 -A

# Check dashboards in Grafana
# Navigate to: Dashboards > Browse > tooling folder
```

## Files Changed

- `gitops/argocd/apps/dev/tooling-dashboards.yaml` (new)
- `gitops/argocd/apps/staging/tooling-dashboards.yaml` (new)
- `gitops/argocd/apps/prod/tooling-dashboards.yaml` (new)
- `gitops/argocd/apps/test/tooling-dashboards.yaml` (new)

## Impact

- Non-breaking change
- Grafana tooling dashboards now deploy automatically
- Dashboards appear in Grafana under "tooling" folder after sync
