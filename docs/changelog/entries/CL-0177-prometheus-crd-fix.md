---
id: CL-0177
title: Prometheus CRD Installation Fix
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
relates_to:
  - CL-0174-kong-prometheus-metrics
  - 20_TOOLING_APPS_MATRIX
---

## Summary

Fixed missing Prometheus CRD that prevented Prometheus server from deploying, causing all Grafana dashboards to show no data.

## Problem

After cluster deployment, Grafana dashboards showed no data. Investigation revealed:

1. **Prometheus server pod was missing** - only Alertmanager, Grafana, and exporters were running
2. **Prometheus Operator was crash-looping** (16 restarts) with error:
   ```
   failed to list *v1.Prometheus: the server could not find the requested resource
   (get prometheuses.monitoring.coreos.com)
   ```
3. **Root cause**: The `prometheuses.monitoring.coreos.com` CRD was not installed

### CRDs Present vs Missing

```bash
kubectl get crd | grep monitoring.coreos.com
```

| CRD | Status |
|-----|--------|
| alertmanagerconfigs.monitoring.coreos.com | ✅ Present |
| alertmanagers.monitoring.coreos.com | ✅ Present |
| podmonitors.monitoring.coreos.com | ✅ Present |
| probes.monitoring.coreos.com | ✅ Present |
| prometheusrules.monitoring.coreos.com | ✅ Present |
| servicemonitors.monitoring.coreos.com | ✅ Present |
| thanosrulers.monitoring.coreos.com | ✅ Present |
| **prometheuses.monitoring.coreos.com** | ❌ **MISSING** |

## Root Cause

ArgoCD was not applying the Prometheus CRD because:

1. **Large CRDs require `ServerSideApply=true`** - The Prometheus CRD is large and ArgoCD's default client-side apply can fail silently
2. **Missing sync options** - `Replace=true` helps with CRD updates
3. **CRDs not explicitly enabled** - Though enabled by default, explicit configuration ensures they're included

## Changes

### ArgoCD Application (`gitops/argocd/apps/dev/kube-prometheus-stack.yaml`)

Added sync options for CRD handling:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
  syncOptions:
    - CreateNamespace=true
    - ServerSideApply=true  # Required for large CRDs
    - Replace=true          # Enables CRD replacement on updates
```

### Helm Values (`gitops/helm/kube-prometheus-stack/values/dev.yaml`)

Explicitly enabled CRD management:

```yaml
prometheusOperator:
  manageCrds: true  # Ensure CRDs are managed by the operator

crds:
  enabled: true     # Explicitly enable CRD installation
```

## Files Changed

- `gitops/argocd/apps/dev/kube-prometheus-stack.yaml`
- `gitops/helm/kube-prometheus-stack/values/dev.yaml`

## Manual Remediation (Existing Clusters)

For clusters already deployed without the CRD, apply manually:

```bash
# 1. Install the missing Prometheus CRD
kubectl apply --server-side -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.68.0/example/prometheus-operator-crd/monitoring.coreos.com_prometheuses.yaml

# 2. Verify CRD is installed
kubectl get crd prometheuses.monitoring.coreos.com

# 3. Re-apply the ArgoCD app with new sync options
kubectl apply -f gitops/argocd/apps/dev/kube-prometheus-stack.yaml

# 4. Restart the operator to pick up the CRD
kubectl rollout restart deployment dev-kube-prometheus-stack-operator -n monitoring

# 5. Watch for Prometheus pod to come up
kubectl get pods -n monitoring -w | grep prometheus
```

## Verification

```bash
# Check Prometheus CRD exists
kubectl get crd prometheuses.monitoring.coreos.com

# Check Prometheus CR is created
kubectl get prometheus -n monitoring

# Check Prometheus StatefulSet exists
kubectl get statefulset -n monitoring | grep prometheus

# Check Prometheus pod is running
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus

# Test Prometheus is scraping
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090
# Open http://localhost:9090/targets
```

## Prevention

This fix ensures future deployments will:
1. Use `ServerSideApply=true` for reliable CRD installation
2. Explicitly enable CRDs in Helm values
3. Include all required Prometheus Operator CRDs

## Impact

- **Breaking**: No (fix only)
- **Downtime**: None for new deployments
- **Data Loss**: No
- Prometheus server will now deploy correctly
- All Grafana dashboards will show metrics data

## Lessons Learned

1. Always use `ServerSideApply=true` for Helm charts that include CRDs
2. Explicitly enable CRDs even when they're "default enabled"
3. When dashboards show no data, check if Prometheus itself is running first
4. Prometheus Operator crash-looping is often a sign of missing CRDs
