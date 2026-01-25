---
id: CL-0172
title: Kong Admin API TLS Routing Fix
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
  - CL-0171-kong-admin-api-ingress
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

Fixed Kong Admin API ingress routing by disabling backend TLS to use correct port.

## Problem

After enabling Admin API ingress (CL-0171), requests returned HTTP 400:

```
400 The plain HTTP request was sent to HTTPS port
```

Root cause: The Kong Helm chart defaulted the admin ingress backend to port 8444 (TLS) when `admin.tls` was not explicitly disabled. Kong ingress already terminates TLS at the edge, so the backend should receive plain HTTP on port 8001.

```yaml
# Before (incorrect)
backend:
  service:
    port:
      number: 8444  # TLS port - expects encrypted traffic

# After (correct)
backend:
  service:
    port:
      number: 8001  # HTTP port - plain traffic from ingress
```

## Changes

### Admin TLS Configuration
- Added `admin.tls.enabled: false`
- This instructs the Helm chart to route ingress traffic to port 8001 (HTTP)

### Path Configuration
- Added explicit `admin.ingress.path: /`

## Files Changed

- `gitops/helm/kong/values/dev.yaml`

## Technical Details

Kong Admin API Service exposes two ports:
- `8001` - HTTP (plain traffic)
- `8444` - HTTPS (TLS traffic)

With TLS termination at the Kong ingress controller:
1. Client connects via HTTPS to ingress
2. Ingress terminates TLS
3. Ingress forwards plain HTTP to backend
4. Backend must listen on HTTP port (8001)

Setting `admin.tls.enabled: false` tells the Helm chart to use port 8001 for ingress backend.

## Verification

```bash
# Check backend port
kubectl get ingress dev-kong-kong-admin -n kong-system \
  -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.port.number}'
# Should return: 8001

# Test Admin API
curl -s https://kong-admin.dev.goldenpathidp.io/ | head -5
# Should return JSON response, not 400 error
```

## Impact

- Non-breaking change
- Admin API now returns HTTP 200 with valid JSON
- Kong Manager can successfully fetch data from Admin API
