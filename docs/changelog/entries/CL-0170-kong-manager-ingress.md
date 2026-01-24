---
id: CL-0170
title: Kong Manager UI Ingress Configuration
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
  - 20_TOOLING_APPS_MATRIX
  - ADR-0002-platform-Kong-as-ingress-API-gateway
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

Enabled Kong Manager UI access via ingress with TLS termination.

## Problem

Kong Manager was configured as `NodePort` service type without ingress. Users could not access the Kong Management UI from outside the cluster without manual port-forwarding.

## Changes

### Service Type Change
- Changed `manager.type` from `NodePort` to `ClusterIP`
- Removed `nodePort: 32002` configuration

### Ingress Configuration
- Added `manager.ingress.enabled: true`
- Set `ingressClassName: kong`
- Configured hostname: `kong-manager.dev.goldenpathidp.io`
- Added cert-manager annotation for TLS: `cert-manager.io/cluster-issuer: letsencrypt-prod`
- Created TLS secret: `kong-manager-tls`

### Environment Variables
- Updated `admin_gui_url` to `https://kong-manager.dev.goldenpathidp.io`

## Files Changed

- `gitops/helm/kong/values/dev.yaml`

## Verification

```bash
# Check ingress
kubectl get ingress -n kong-system dev-kong-kong-manager

# Check certificate
kubectl get certificate -n kong-system kong-manager-tls

# Test access
curl -sI https://kong-manager.dev.goldenpathidp.io/ | head -3
```

## Impact

- Non-breaking change
- Kong Manager UI now accessible at https://kong-manager.dev.goldenpathidp.io
- TLS termination handled by cert-manager with Let's Encrypt
