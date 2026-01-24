---
id: CL-0174
title: Kong Prometheus Metrics Integration
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
relates_to:
  - CL-0170-kong-manager-ingress
  - 20_TOOLING_APPS_MATRIX
  - ADR-0002-platform-Kong-as-ingress-API-gateway
---

## Summary

Enabled Kong Prometheus metrics endpoint and ServiceMonitor for API traffic visualization in Grafana.

## Problem

Kong Manager OSS provides read-only visibility into routes, services, and plugins but lacks API analytics dashboards showing:
- Request rates and throughput
- Latency percentiles (P50/P95/P99)
- Error rates by status code
- Bandwidth utilization

The platform already has Prometheus + Grafana deployed, and a Kong Golden Signals dashboard existed but had no metrics to display.

## Changes

### Status API (Metrics Endpoint)
- Added `status.enabled: true`
- Configured HTTP endpoint on port 8100
- Exposes `/metrics` in Prometheus format

### ServiceMonitor
- Added `serviceMonitor.enabled: true`
- Configured 30-second scrape interval
- ServiceMonitor created in `kong-system` namespace
- Prometheus Operator auto-discovers and scrapes metrics

## Files Changed

- `gitops/helm/kong/values/dev.yaml`

## Metrics Exposed

Kong now exposes the following Prometheus metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `kong_http_requests_total` | Counter | Total HTTP requests by route/service/status |
| `kong_request_latency_ms` | Histogram | Request latency in milliseconds |
| `kong_upstream_latency_ms` | Histogram | Upstream (backend) latency |
| `kong_bandwidth_bytes` | Counter | Traffic volume by direction |
| `kong_nginx_connections_total` | Gauge | Active/waiting connections |
| `kong_upstream_target_health` | Gauge | Upstream health status |

## Verification

```bash
# Check status endpoint is responding
kubectl port-forward svc/dev-kong-kong-status -n kong-system 8100:8100
curl -s http://localhost:8100/metrics | head -20

# Check ServiceMonitor created
kubectl get servicemonitor -n kong-system

# Verify Prometheus is scraping Kong
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090
# Open http://localhost:9090/targets - look for kong-system/kong
```

## Grafana Dashboard

An existing dashboard `kong-golden-signals` (in `kong-system` namespace) displays:
- Total Request Rate (RPS)
- Requests by Status Code
- Error Rate (%)
- Request Latency P50/P95/P99
- Upstream Latency P50/P95/P99
- Active Connections
- Bandwidth In/Out
- Upstream Health
- Kong Logs (via Loki)

Access at: `https://grafana.dev.goldenpathidp.io` > Dashboards > Kong Ingress - Golden Signals

## Impact

- Non-breaking change
- Kong pod restarts to enable status endpoint
- API traffic now visible in Grafana
- Enables proactive monitoring and alerting on API gateway health
