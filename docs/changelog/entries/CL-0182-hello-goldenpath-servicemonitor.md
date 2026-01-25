---
id: CL-0182
title: hello-goldenpath-idp ServiceMonitor and Observability Guide
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
  - CL-0181-tooling-observability-config
  - CL-0176-hello-goldenpath-idp-dashboard
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

Added a ServiceMonitor for hello-goldenpath-idp as a reference pattern for custom application monitoring, plus comprehensive documentation on ServiceMonitor usage.

## Purpose

Demonstrates the complete observability instrumentation pattern for applications deployed on the Golden Path IDP, even when the application doesn't yet expose a `/metrics` endpoint.

## Changes

### ServiceMonitor (`gitops/helm/tooling-dashboards/hello-goldenpath-idp-servicemonitor.yaml`)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hello-goldenpath-idp
  namespace: apps
  labels:
    release: dev-kube-prometheus-stack  # Required for Prometheus discovery
spec:
  selector:
    matchLabels:
      app: hello-goldenpath-idp
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

### Kustomization Update

Added ServiceMonitor to `kustomization.yaml` resources.

### Documentation (`docs/70-operations/50_SERVICEMONITOR_OBSERVABILITY_GUIDE.md`)

Comprehensive guide covering:
- What ServiceMonitors are and how they work
- The critical `release: dev-kube-prometheus-stack` label requirement
- When to use ServiceMonitors vs. relying on automatic metrics
- Code examples for Node.js, Go, and Python metrics instrumentation
- Troubleshooting guide for common issues
- PromQL queries for apps without custom metrics

## Key Insight: Metrics Without /metrics Endpoint

Apps without custom metrics still get observability through:

| Metric Source | Collected By | Example Query |
|---------------|--------------|---------------|
| CPU/Memory | cAdvisor | `container_cpu_usage_seconds_total{pod=~"hello.*"}` |
| Pod status | kube-state-metrics | `kube_pod_status_phase{pod=~"hello.*"}` |
| HTTP traffic | Kong | `kong_http_requests_total{service=~".*hello.*"}` |
| Latency | Kong | `kong_request_latency_ms_bucket{service=~".*hello.*"}` |

## Files Changed

- `gitops/helm/tooling-dashboards/hello-goldenpath-idp-servicemonitor.yaml` (new)
- `gitops/helm/tooling-dashboards/kustomization.yaml`
- `docs/70-operations/50_SERVICEMONITOR_OBSERVABILITY_GUIDE.md` (new)

## Verification

```bash
# Check ServiceMonitor is created
kubectl get servicemonitor hello-goldenpath-idp -n apps

# Check it has the correct label
kubectl get servicemonitor hello-goldenpath-idp -n apps \
  -o jsonpath='{.metadata.labels.release}'
# Expected: dev-kube-prometheus-stack

# Check Prometheus discovered it (may show as "down" if app has no /metrics)
kubectl port-forward -n monitoring svc/dev-kube-prometheus-stack-prometheus 9090:9090
# Visit: http://localhost:9090/targets
```

## Impact

- **Breaking**: No
- **Pattern Established**: Teams can copy this ServiceMonitor as a template
- **Documentation**: Comprehensive guide reduces onboarding friction

## Next Steps

To enable custom metrics in hello-goldenpath-idp:
1. Add `prom-client` (Node.js) or equivalent to the application
2. Expose `/metrics` endpoint on port 8080
3. ServiceMonitor will automatically start scraping
