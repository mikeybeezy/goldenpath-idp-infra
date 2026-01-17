---
id: CL-0138-tooling-apps-dashboards
title: RED/Golden Signals Dashboards for Tooling Applications
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - backstage
  - keycloak
  - argocd
  - kong
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0162
  - ADR-0162-kong-ingress-dns-strategy
  - CL-0136
  - CL-0136-tooling-apps-ingress-configuration
  - CL-0137
  - CL-0137-ootb-observability-dashboards
  - CL-0138
supersedes: []
superseded_by: []
tags:
  - grafana
  - dashboards
  - observability
  - red-metrics
  - golden-signals
  - loki
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: high
  potential_savings_hours: 8.0
supported_until: 2028-01-16
version: '1.0'
breaking_change: false
---
## CL-0138: RED/Golden Signals Dashboards for Tooling Applications

**Type**: Feature
**Component**: Observability / Grafana Dashboards
**Date**: 2026-01-16
**Related**: CL-0136

## Summary

Created comprehensive observability dashboards for all platform tooling applications following the RED (Rate, Errors, Duration) methodology and Golden Signals principles. Each dashboard includes Loki log panels for error investigation.

## Problem Statement

Tooling applications (Backstage, Keycloak, ArgoCD, Kong) lacked dedicated observability dashboards. While sample applications had RED metrics dashboards, platform tooling was only covered by generic cluster-level dashboards.

## Solution

Created dedicated ConfigMap-based dashboards for each tooling application that are automatically discovered by the Grafana sidecar.

## Dashboards Created

### 1. Backstage Dashboard (`backstage-golden-signals`)

|Panel|Metric Type|Description|
|-------|-------------|-------------|
|Request Rate (RPS)|Rate|HTTP requests per second by method|
|Error Rate (%)|Errors|4xx and 5xx error percentages|
|Latency P50/P95/P99|Duration|Response time percentiles|
|CPU/Memory Usage|Saturation|Container resource usage|
|Pod Restarts|Saturation|Restart count indicator|
|Error Logs|Logs|Loki panel filtering errors|
|All Logs|Logs|Complete application logs|

### 2. Keycloak Dashboard (`keycloak-golden-signals`)

|Panel|Metric Type|Description|
|-------|-------------|-------------|
|Login Attempts (RPS)|Rate|Successful and failed logins|
|HTTP Request Rate|Rate|API requests per second|
|Error Rate (%)|Errors|HTTP errors and login failure rate|
|HTTP Latency|Duration|P50/P95/P99 response times|
|Active Sessions|Traffic|Current authenticated sessions|
|JVM Heap Usage|Saturation|Java memory usage|
|Auth Events & Errors|Logs|Login/logout and error events|

### 3. ArgoCD Dashboard (`argocd-golden-signals`)

|Panel|Metric Type|Description|
|-------|-------------|-------------|
|Application Health|Overview|Healthy/Degraded/OutOfSync counts|
|API Request Rate|Rate|HTTP and gRPC requests|
|Error Rate (%)|Errors|5xx and gRPC error percentages|
|Request Duration P95|Duration|HTTP and gRPC latency|
|Sync Operations Rate|Rate|Sync operations by phase|
|Git Operations Rate|Rate|Git requests by type|
|CPU/Memory by Component|Saturation|Per-component resource usage|
|Sync Events & Errors|Logs|Sync and reconciliation logs|

### 4. Kong Dashboard (`kong-golden-signals`)

|Panel|Metric Type|Description|
|-------|-------------|-------------|
|Total Request Rate|Rate|Overall and per-service RPS|
|Requests by Status|Rate|Breakdown by HTTP status code|
|Error Rate (%)|Errors|4xx and 5xx percentages|
|Request Latency|Duration|Client-facing latency P50/P95/P99|
|Upstream Latency|Duration|Backend latency percentiles|
|Active Connections|Saturation|Connection states|
|Bandwidth In/Out|Saturation|Network throughput|
|Upstream Health|Traffic|Healthy upstream count|
|Kong Errors & Warnings|Logs|Error and warning logs|

## Files Created

|File|Purpose|
|------|---------|
|`gitops/helm/tooling-dashboards/backstage-dashboard.yaml`|Backstage ConfigMap|
|`gitops/helm/tooling-dashboards/keycloak-dashboard.yaml`|Keycloak ConfigMap|
|`gitops/helm/tooling-dashboards/argocd-dashboard.yaml`|ArgoCD ConfigMap|
|`gitops/helm/tooling-dashboards/kong-dashboard.yaml`|Kong ConfigMap|
|`gitops/helm/tooling-dashboards/kustomization.yaml`|Kustomize bundle|
|`gitops/helm/tooling-dashboards/metadata.yaml`|Governance metadata|

## Deployment

Deploy using Kustomize:

```bash
kubectl apply -k gitops/helm/tooling-dashboards/
```

Dashboards will be auto-discovered by Grafana sidecar within ~60 seconds.

## Verification

```bash
# Check ConfigMaps are deployed
kubectl get configmaps -A -l grafana_dashboard=1 | grep -E "(backstage|keycloak|argocd|kong)"

# Verify in Grafana UI
# Navigate to Dashboards -> Browse -> Search for "Golden Signals"
```

## Data Sources Required

- **Prometheus**: For metrics (auto-configured in kube-prometheus-stack)
- **Loki**: For logs (requires loki datasource with uid "loki")

## Rollback

```bash
kubectl delete -k gitops/helm/tooling-dashboards/
```
