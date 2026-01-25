<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0176
title: hello-goldenpath-idp Grafana Dashboard
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
  - CL-0175-tooling-dashboards-argocd-app
  - CL-0174-kong-prometheus-metrics
  - 20_TOOLING_APPS_MATRIX
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

Added Grafana Golden Signals dashboard for the hello-goldenpath-idp sample application.

## Problem

The hello-goldenpath-idp test application (`https://hello-goldenpath-idp.dev.goldenpathidp.io`) had no observability dashboard, unlike other platform tooling (Kong, ArgoCD, Backstage, Keycloak).

## Changes

### Dashboard Created

- File: `gitops/helm/tooling-dashboards/hello-goldenpath-idp-dashboard.yaml`
- Namespace: `apps`
- UID: `hello-goldenpath-idp`

### Dashboard Panels

| Section | Metrics |
|---------|---------|
| **Application Health** | Pod status, restarts (24h), container ready, replicas available |
| **Traffic (RED)** | Request rate via Kong, requests by status code, error rate % |
| **Latency** | Request latency P50/P95/P99, upstream latency P50/P95/P99 |
| **Saturation** | CPU usage, memory usage by pod |
| **Logs** | Application logs via Loki |

### Kustomization Updated

Added to `gitops/helm/tooling-dashboards/kustomization.yaml`:
```yaml
resources:
  - hello-goldenpath-idp-dashboard.yaml
```

## Bootstrap Verification

The dashboard will deploy on bootstrap because:
1. Added to `kustomization.yaml` resources
2. `tooling-dashboards` ArgoCD app deploys all resources in the Kustomization
3. Both Terraform and shell bootstrap methods apply all YAML files in the apps directory

## Grafana Sidecar Pattern

- Label: `grafana_dashboard: "1"`
- Annotation: `k8s-sidecar-target-directory: "/tmp/dashboards/tooling"`
- Deployed to `apps` namespace (same as the application)

## Files Changed

- `gitops/helm/tooling-dashboards/hello-goldenpath-idp-dashboard.yaml` (new)
- `gitops/helm/tooling-dashboards/kustomization.yaml` (updated)

## Verification

```bash
# Check ConfigMap deployed
kubectl get configmap hello-goldenpath-idp-dashboard -n apps

# Check in Grafana
# Navigate to: Dashboards > Browse > tooling > hello-goldenpath-idp - Golden Signals
```

## Impact

- Non-breaking change
- Sample application now has full observability coverage
- Demonstrates dashboard pattern for tenant applications
