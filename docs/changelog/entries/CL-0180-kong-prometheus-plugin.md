---
id: CL-0180
title: Kong Prometheus Plugin for RED Metrics
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
relates_to:
  - CL-0174-kong-prometheus-metrics
  - CL-0179-loki-datasource-fix
---

## Summary

Enabled Kong Prometheus plugin globally to expose RED metrics (Requests, Errors, Duration) required for dashboard visualizations.

## Problem

Dashboard panels showing "Duration - Latency", "RED Metrics - Traffic", and "Connections & Bandwidth" were empty because:

1. **Kong's default `/metrics` endpoint only exposes basic metrics:**
   - `kong_datastore_reachable`
   - `kong_memory_*`
   - `kong_nginx_*`

2. **Traffic metrics require the Prometheus plugin:**
   - `kong_http_requests_total` (request rate by status code)
   - `kong_request_latency_ms_bucket` (latency histograms)
   - `kong_bandwidth_bytes` (ingress/egress bandwidth)

3. **ServiceMonitor was not discovered by Prometheus:**
   - Missing `release: dev-kube-prometheus-stack` label
   - Prometheus only selects ServiceMonitors with this label

## Changes

### Kong Values (`gitops/helm/kong/values/dev.yaml`)

**Added release label to ServiceMonitor:**

```yaml
serviceMonitor:
  enabled: true
  namespace: kong-system
  interval: 30s
  labels:
    release: dev-kube-prometheus-stack  # Required for Prometheus discovery
```

**Added KongClusterPlugin via extraDeploy:**

```yaml
extraDeploy:
  - apiVersion: configuration.konghq.com/v1
    kind: KongClusterPlugin
    metadata:
      name: prometheus
      labels:
        global: "true"
      annotations:
        kubernetes.io/ingress.class: kong
    config:
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true
      upstream_health_metrics: true
    plugin: prometheus
```

## Metrics Now Available

| Metric | Description |
|--------|-------------|
| `kong_http_requests_total` | HTTP requests by service/route/status code |
| `kong_request_latency_ms_bucket` | Request latency histogram |
| `kong_upstream_latency_ms_bucket` | Upstream service latency |
| `kong_bandwidth_bytes` | Ingress/egress bandwidth |

## Files Changed

- `gitops/helm/kong/values/dev.yaml`

## Verification

```bash
# Check ServiceMonitor has release label
kubectl get servicemonitor dev-kong-kong -n kong-system -o jsonpath='{.metadata.labels.release}'

# Check KongClusterPlugin exists
kubectl get kongclusterplugins prometheus -o yaml

# Query Kong metrics in Prometheus
kubectl exec -n monitoring prometheus-dev-kube-prometheus-stack-prometheus-0 \
  -c prometheus -- wget -qO- "http://localhost:9090/api/v1/query?query=kong_http_requests_total"
```

## Impact

- **Breaking**: No
- **Performance**: Minimal - optional metrics add ~5% overhead
- Dashboard panels now display:
  - Request rates and status codes
  - Latency percentiles (P50/P95/P99)
  - Bandwidth throughput
  - Error rates

## Notes

Per Kong documentation, the optional metrics (`status_code_metrics`, `latency_metrics`, etc.) are disabled by default to prevent high-cardinality issues. They are explicitly enabled here for observability.
