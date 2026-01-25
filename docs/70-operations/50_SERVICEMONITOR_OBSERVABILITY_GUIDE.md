---
id: 50_SERVICEMONITOR_OBSERVABILITY_GUIDE
title: ServiceMonitor Observability Guide
type: policy
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: compliance
---

# ServiceMonitor Observability Guide

> How to instrument custom applications for Prometheus metrics collection

## Overview

A **ServiceMonitor** is a Kubernetes Custom Resource Definition (CRD) provided by the Prometheus Operator. It tells Prometheus **how to discover and scrape metrics** from your application's `/metrics` endpoint.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Prometheus Metrics Collection Flow                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌─────────────────┐     ┌──────────────────────────┐ │
│   │ Application │     │  ServiceMonitor │     │       Prometheus         │ │
│   │             │     │                 │     │                          │ │
│   │  :8080      │────▶│  selector:      │────▶│  Scrapes /metrics every  │ │
│   │  /metrics   │     │    app: myapp   │     │  30s based on discovery  │ │
│   └─────────────┘     │  endpoints:     │     └──────────────────────────┘ │
│         │             │    - port: http │               │                  │
│         │             │      path: /... │               │                  │
│         ▼             └─────────────────┘               ▼                  │
│   ┌─────────────┐                             ┌──────────────────────────┐ │
│   │   Service   │                             │        Grafana           │ │
│   │  (port 80)  │                             │   (visualize metrics)    │ │
│   └─────────────┘                             └──────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## The Critical Label

Prometheus Operator **only watches ServiceMonitors** that match its label selector:

```yaml
# This label is REQUIRED for Prometheus to discover your ServiceMonitor
labels:
  release: dev-kube-prometheus-stack
```

Without this label, your ServiceMonitor will be ignored.

## When Do You Need a ServiceMonitor?

| Metrics Type | Source | ServiceMonitor Needed? |
|--------------|--------|------------------------|
| **Application metrics** (request counts, business KPIs) | App's `/metrics` endpoint | **Yes** |
| **Container resources** (CPU, memory) | cAdvisor (kubelet) | No - automatic |
| **Pod status** (restarts, ready state) | kube-state-metrics | No - automatic |
| **Ingress traffic** (requests, latency) | Kong Prometheus plugin | No - Kong's ServiceMonitor |
| **Database queries** | App's `/metrics` endpoint | **Yes** |

## Example: Minimal ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: apps
  labels:
    release: dev-kube-prometheus-stack  # REQUIRED
spec:
  selector:
    matchLabels:
      app: my-app  # Must match your Service labels
  namespaceSelector:
    matchNames:
      - apps
  endpoints:
    - port: http       # Must match Service port name
      path: /metrics
      interval: 30s
```

## Example: Application with Prometheus Metrics

### Node.js (using prom-client)

```javascript
const promClient = require('prom-client');
const express = require('express');
const app = express();

// Collect default metrics (memory, CPU, event loop)
promClient.collectDefaultMetrics();

// Custom metric: HTTP request duration
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
});

// Middleware to record request duration
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer();
  res.on('finish', () => {
    end({ method: req.method, route: req.path, status_code: res.statusCode });
  });
  next();
});

// Expose /metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});

app.listen(8080);
```

### Go (using prometheus/client_golang)

```go
package main

import (
    "net/http"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var httpRequestsTotal = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total number of HTTP requests",
    },
    []string{"method", "path", "status"},
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

### Python (using prometheus-client)

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import Flask, Response

app = Flask(__name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(port=8080)
```

## Metrics Without /metrics Endpoint

If your application doesn't expose metrics, you still get observability through:

### 1. Infrastructure Metrics (Automatic)
```promql
# CPU usage
rate(container_cpu_usage_seconds_total{namespace="apps", pod=~"my-app.*"}[2m])

# Memory usage
container_memory_usage_bytes{namespace="apps", pod=~"my-app.*"}
```

### 2. Pod Health (Automatic via kube-state-metrics)
```promql
# Pod restarts
kube_pod_container_status_restarts_total{namespace="apps", pod=~"my-app.*"}

# Pod status
kube_pod_status_phase{namespace="apps", pod=~"my-app.*"}
```

### 3. Ingress Traffic (via Kong)
```promql
# Request rate
rate(kong_http_requests_total{service=~".*my-app.*"}[2m])

# Latency percentiles
histogram_quantile(0.95, sum(rate(kong_request_latency_ms_bucket{service=~".*my-app.*"}[5m])) by (le))

# Error rate
sum(rate(kong_http_requests_total{service=~".*my-app.*", code=~"5.."}[2m]))
  / sum(rate(kong_http_requests_total{service=~".*my-app.*"}[2m]))
```

## Troubleshooting

### ServiceMonitor Not Being Scraped

1. **Check the release label**:
   ```bash
   kubectl get servicemonitor my-app -n apps -o jsonpath='{.metadata.labels.release}'
   # Should output: dev-kube-prometheus-stack
   ```

2. **Verify Service selector matches**:
   ```bash
   kubectl get svc my-app -n apps -o jsonpath='{.metadata.labels}'
   kubectl get servicemonitor my-app -n apps -o jsonpath='{.spec.selector.matchLabels}'
   ```

3. **Check Prometheus targets**:
   ```bash
   kubectl port-forward -n monitoring svc/dev-kube-prometheus-stack-prometheus 9090:9090
   # Visit http://localhost:9090/targets
   ```

4. **Check if /metrics returns data**:
   ```bash
   kubectl exec -n apps deploy/my-app -- curl -s localhost:8080/metrics
   ```

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Target not found | Missing `release` label | Add `release: dev-kube-prometheus-stack` |
| Target down | App not exposing /metrics | Add Prometheus client library |
| Wrong port | Port name mismatch | Ensure ServiceMonitor port matches Service |
| Empty metrics | App returning empty | Check app metrics implementation |

## Best Practices

1. **Use meaningful metric names**: Follow [Prometheus naming conventions](https://prometheus.io/docs/practices/naming/)
2. **Add labels wisely**: Labels create cardinality - avoid high-cardinality labels (user IDs, request IDs)
3. **Set appropriate intervals**: 30s is standard; increase for low-traffic apps
4. **Include units in names**: `_seconds`, `_bytes`, `_total`
5. **Document your metrics**: Add `help` text to all metrics

## Related Resources

- [hello-goldenpath-idp ServiceMonitor](../../gitops/helm/tooling-dashboards/hello-goldenpath-idp-servicemonitor.yaml) - Example for custom apps
- [ADR-0069: Observability Baseline](../adrs/ADR-0069-platform-observability-baseline-golden-signals.md) - Golden Signals strategy
- [CL-0181: Tooling Observability](../changelog/entries/CL-0181-tooling-observability-config.md) - Recent ServiceMonitor additions
