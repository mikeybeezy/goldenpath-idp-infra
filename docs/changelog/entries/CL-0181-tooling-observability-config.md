---
id: CL-0181
title: Tooling Observability Configuration (ArgoCD, Backstage, Keycloak)
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - CL-0180-kong-prometheus-plugin
  - CL-0179-loki-datasource-fix
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-24
author: platform-team
breaking_change: false
---

## Summary

Added ServiceMonitor configurations for ArgoCD, Backstage, and Keycloak to enable Prometheus metrics scraping and populate Golden Signals dashboards.

## Problem

The Golden Signals dashboards for tooling applications showed no data because:

1. **ServiceMonitors missing**: Prometheus wasn't discovering metrics endpoints
2. **Missing `release` label**: ServiceMonitors need `release: dev-kube-prometheus-stack` for Prometheus to select them
3. **Metrics endpoints not configured**: Some applications didn't have metrics exposed

## Changes

### ArgoCD (`gitops/helm/argocd/values/dev.yaml`)

Added metrics and ServiceMonitor for all ArgoCD components:

```yaml
controller:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      namespace: argocd
      additionalLabels:
        release: dev-kube-prometheus-stack

server:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      namespace: argocd
      additionalLabels:
        release: dev-kube-prometheus-stack

repoServer:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      namespace: argocd
      additionalLabels:
        release: dev-kube-prometheus-stack

applicationSet:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      namespace: argocd
      additionalLabels:
        release: dev-kube-prometheus-stack

notifications:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
      namespace: argocd
      additionalLabels:
        release: dev-kube-prometheus-stack
```

### Backstage

**Chart template** (`backstage-helm/charts/backstage/templates/servicemonitor.yaml`):
- Added new ServiceMonitor template to the Backstage Helm chart

**Default values** (`backstage-helm/charts/backstage/values.yaml`):
```yaml
serviceMonitor:
  enabled: false
  namespace: ""
  interval: 30s
  scrapeTimeout: 10s
  path: /metrics
  labels: {}
```

**Dev values** (`gitops/helm/backstage/values/dev.yaml`):
```yaml
serviceMonitor:
  enabled: true
  namespace: backstage
  interval: 30s
  labels:
    release: dev-kube-prometheus-stack
```

### Keycloak (`gitops/helm/keycloak/values/dev.yaml`)

Added metrics and ServiceMonitor configuration:

```yaml
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: keycloak
    labels:
      release: dev-kube-prometheus-stack
    interval: 30s
```

Note: Keycloak already had `KC_METRICS_ENABLED=true` in extraEnvVars.

## Metrics Now Available

| Application | Metrics |
|-------------|---------|
| ArgoCD | `argocd_app_info`, `argocd_server_http_requests_total`, `argocd_app_sync_total`, `grpc_server_handled_total` |
| Backstage | `http_request_duration_seconds_*` (requires prom-client plugin) |
| Keycloak | Keycloak built-in metrics via `/metrics` endpoint |

## Files Changed

- `gitops/helm/argocd/values/dev.yaml`
- `gitops/helm/backstage/values/dev.yaml`
- `gitops/helm/keycloak/values/dev.yaml`
- `backstage-helm/charts/backstage/values.yaml`
- `backstage-helm/charts/backstage/templates/servicemonitor.yaml` (new)

## Verification

```bash
# Check ArgoCD ServiceMonitors
kubectl get servicemonitor -n argocd -l release=dev-kube-prometheus-stack

# Check Backstage ServiceMonitor
kubectl get servicemonitor -n backstage -l release=dev-kube-prometheus-stack

# Check Keycloak ServiceMonitor
kubectl get servicemonitor -n keycloak -l release=dev-kube-prometheus-stack

# Query ArgoCD metrics in Prometheus
kubectl exec -n monitoring prometheus-dev-kube-prometheus-stack-prometheus-0 \
  -c prometheus -- wget -qO- "http://localhost:9090/api/v1/query?query=argocd_app_info"
```

## Impact

- **Breaking**: No
- **Downtime**: None (ServiceMonitors don't require restarts)
- Dashboard panels now display:
  - ArgoCD: GitOps health, sync operations, API request rates
  - Backstage: Request rates, latency (when prom-client configured)
  - Keycloak: Authentication metrics, session counts

## Notes

- **Backstage metrics**: Requires Backstage to be configured with `@backstage/plugin-scaffolder-backend-module-prometheus` or custom prom-client integration to expose `/metrics` endpoint. Container-level metrics (CPU, Memory, restarts) work automatically via cAdvisor and kube-state-metrics.
- **ArgoCD**: Native Prometheus metrics are built-in
- **Keycloak**: Metrics endpoint enabled via `KC_METRICS_ENABLED=true` environment variable

---

**Historical Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
- `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
- `backstage-helm/backstage-catalog/` → `catalog/`
