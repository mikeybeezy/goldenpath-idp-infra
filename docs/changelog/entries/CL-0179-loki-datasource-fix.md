---
id: CL-0179
title: Loki Datasource Configuration Fixes
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
  - CL-0177-prometheus-crd-fix
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

Fixed Loki datasource configuration issues preventing logs from displaying in Grafana dashboards.

## Problems

### 1. Wrong Loki Service URL

Grafana's Loki datasource was pointing to a non-existent service:

| Before | After |
|--------|-------|
| `loki-gateway.monitoring.svc:3100` | `dev-loki.monitoring.svc:3100` |

### 2. Duplicate Default Datasource Conflict

Two datasources were marked as `isDefault: true`:
- Prometheus (from kube-prometheus-stack)
- Loki (from loki-stack)

This caused provisioning to fail:

```text
Datasource provisioning error: datasource.yaml config is invalid.
Only one datasource per organization can be marked as default
```

### 3. Missing Datasource UIDs

Dashboard panels reference datasources by UID. Without explicit UIDs, Grafana auto-generates them, causing logs panels to fail:

```json
"datasource": { "type": "loki", "uid": "loki" }
```

The panel expected `uid: "loki"` but no such UID existed.

## Changes

### Grafana Values (`gitops/helm/kube-prometheus-stack/values/dev.yaml`)

Added explicit UIDs and fixed URL:

```yaml
additionalDataSources:
  - name: Loki
    type: loki
    uid: loki                              # Added
    access: proxy
    url: http://dev-loki.monitoring.svc:3100  # Fixed
    jsonData:
      maxLines: 1000
  - name: Tempo
    type: tempo
    uid: tempo                             # Added
    access: proxy
    url: http://tempo.monitoring.svc.cluster.local:3100
```

### Loki Values (`gitops/helm/loki/values/dev.yaml`)

Disabled duplicate datasource creation from loki-stack:

```yaml
grafana:
  sidecar:
    datasources:
      enabled: false  # Prevent duplicate datasource
```

## Files Changed

- `gitops/helm/kube-prometheus-stack/values/dev.yaml`
- `gitops/helm/loki/values/dev.yaml`

## Verification

```bash
# Check Loki datasource has correct UID
kubectl exec -n monitoring deploy/dev-kube-prometheus-stack-grafana -c grafana \
  -- cat /etc/grafana/provisioning/datasources/datasource.yaml | grep -A 3 "name: Loki"

# Test Loki query from Grafana
kubectl exec -n monitoring deploy/dev-kube-prometheus-stack-grafana -c grafana \
  -- wget -qO- 'http://dev-loki.monitoring.svc:3100/loki/api/v1/labels'

# Check no provisioning errors
kubectl logs -n monitoring deploy/dev-kube-prometheus-stack-grafana -c grafana \
  | grep -i "provision"
```

## Impact

- **Breaking**: No
- **Downtime**: None (Grafana restart only)
- **Data Loss**: No
- Dashboard logs panels now render correctly
- Loki datasource accessible in Grafana Explore

## Lessons Learned

1. **Always set explicit datasource UIDs** - Dashboards reference by UID, not name
2. **Only one datasource can be default** - When multiple charts create datasources, coordinate who sets `isDefault`
3. **Verify service names** - Helm charts may create services with prefixes (e.g., `dev-loki` not `loki`)
