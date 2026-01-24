---
id: CL-0177
title: Prometheus CRD and ArgoCD Sync Fixes
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
relates_to:
  - CL-0174-kong-prometheus-metrics
  - 20_TOOLING_APPS_MATRIX
---

## Summary

Fixed multiple issues preventing Prometheus server from deploying, causing all Grafana dashboards to show no data.

## Problem

After cluster deployment, Grafana dashboards showed no data. Investigation revealed a cascade of issues:

1. **Prometheus server pod was missing** - only Alertmanager, Grafana, and exporters were running
2. **Prometheus Operator was crash-looping** (16 restarts) with error:
   ```
   failed to list *v1.Prometheus: the server could not find the requested resource
   (get prometheuses.monitoring.coreos.com)
   ```
3. **Root cause**: The `prometheuses.monitoring.coreos.com` CRD was not installed
4. **Secondary issues**: ArgoCD sync conflicts with admission webhooks and PVC spec fields

### CRDs Present vs Missing

| CRD | Status |
|-----|--------|
| alertmanagerconfigs.monitoring.coreos.com | Present |
| alertmanagers.monitoring.coreos.com | Present |
| podmonitors.monitoring.coreos.com | Present |
| probes.monitoring.coreos.com | Present |
| prometheusrules.monitoring.coreos.com | Present |
| servicemonitors.monitoring.coreos.com | Present |
| thanosrulers.monitoring.coreos.com | Present |
| **prometheuses.monitoring.coreos.com** | **MISSING** |

## Root Causes

### 1. CRD Not Applied

ArgoCD's default client-side apply fails silently on large CRDs like `prometheuses.monitoring.coreos.com`.

### 2. Admission Webhook Conflicts

The Prometheus Operator's admission webhooks create ClusterRole/ClusterRoleBinding resources that cause "already exists" errors when ArgoCD retries sync:

```text
hookPhase: Failed
message: clusterroles.rbac.authorization.k8s.io "dev-kube-prometheus-stack-admission" already exists
```

### 3. PVC Spec Immutability

The `Replace=true` sync option caused conflicts with existing PVCs:

```text
PersistentVolumeClaim "dev-kube-prometheus-stack-grafana" is invalid:
spec: Forbidden: spec is immutable after creation
```

The cluster populates `volumeName` and `storageClassName` after creation, causing drift detection.

## Changes

### ArgoCD Application (`gitops/argocd/apps/dev/kube-prometheus-stack.yaml`)

**Sync options:**

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
  syncOptions:
    - CreateNamespace=true
    - ServerSideApply=true  # Required for large CRDs
    # NOTE: Replace=true removed - causes PVC conflicts
```

**Ignore differences for cluster-managed fields:**

```yaml
ignoreDifferences:
  - group: ""
    kind: PersistentVolumeClaim
    jsonPointers:
      - /spec/volumeName
      - /spec/storageClassName
      - /spec/volumeMode
```

### Helm Values (`gitops/helm/kube-prometheus-stack/values/dev.yaml`)

**CRD management:**

```yaml
crds:
  enabled: true

prometheusOperator:
  manageCrds: true
```

**Disable admission webhooks (prevents sync conflicts):**

```yaml
prometheusOperator:
  admissionWebhooks:
    enabled: false
```

## Files Changed

- `gitops/argocd/apps/dev/kube-prometheus-stack.yaml`
- `gitops/helm/kube-prometheus-stack/values/dev.yaml`

## Manual Remediation (Existing Clusters)

For clusters where ArgoCD sync is stuck:

```bash
# 1. Clean up admission webhook resources
kubectl delete clusterrole dev-kube-prometheus-stack-admission --ignore-not-found
kubectl delete clusterrolebinding dev-kube-prometheus-stack-admission --ignore-not-found
kubectl delete role dev-kube-prometheus-stack-admission -n monitoring --ignore-not-found
kubectl delete rolebinding dev-kube-prometheus-stack-admission -n monitoring --ignore-not-found
kubectl delete validatingwebhookconfiguration dev-kube-prometheus-stack-admission --ignore-not-found
kubectl delete mutatingwebhookconfiguration dev-kube-prometheus-stack-admission --ignore-not-found

# 2. Delete and recreate the ArgoCD application
kubectl delete application dev-kube-prometheus-stack -n argocd --wait
kubectl apply -f gitops/argocd/apps/dev/kube-prometheus-stack.yaml

# 3. Verify Prometheus is running
kubectl get prometheus -n monitoring
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus
```

## Verification

```bash
# Check Prometheus CR exists
kubectl get prometheus -n monitoring

# Check Prometheus pod is running
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus

# Verify metrics are being scraped
kubectl exec -n monitoring prometheus-dev-kube-prometheus-stack-prometheus-0 \
  -c prometheus -- wget -qO- "http://localhost:9090/api/v1/query?query=up"
```

## Impact

- **Breaking**: No (fix only)
- **Downtime**: None for new deployments
- **Data Loss**: No
- Prometheus server deploys correctly
- All Grafana dashboards show metrics data

## Lessons Learned

1. **ServerSideApply=true** is required for Helm charts with large CRDs
2. **Replace=true** should NOT be used with stateful resources (PVCs)
3. **Admission webhooks** can cause sync conflicts - disable when not needed
4. **ignoreDifferences** is essential for fields populated by the cluster
5. When dashboards show no data, verify Prometheus itself is running
