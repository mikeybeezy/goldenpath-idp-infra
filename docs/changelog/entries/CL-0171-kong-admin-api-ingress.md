<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0171
title: Kong Admin API External Ingress
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
  - CL-0170-kong-manager-ingress
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

Exposed Kong Admin API via ingress to enable Kong Manager data flow.

## Problem

Kong Manager UI was accessible but showed no data. The root cause was that `admin_gui_api_url` pointed to an internal Kubernetes DNS name (`dev-kong-kong-admin.kong-system.svc.cluster.local:8001`) that browsers cannot resolve.

Kong Manager runs in the browser and makes requests to the Admin API. For this to work, the Admin API must be accessible from the browser, not just from within the cluster.

## Changes

### Admin API Ingress
- Added `admin.ingress.enabled: true`
- Set `ingressClassName: kong`
- Configured hostname: `kong-admin.dev.goldenpathidp.io`
- Added cert-manager annotation: `cert-manager.io/cluster-issuer: letsencrypt-prod`
- Added protocol annotation: `konghq.com/protocols: "https"`
- Created TLS secret: `kong-admin-tls`

### Environment Variables
- Updated `admin_gui_api_url` from internal K8s DNS to `<https://kong-admin.dev.goldenpathidp.io`>

### Security Warning
Added comment warning that Admin API should be protected with authentication in production environments.

## Files Changed

- `gitops/helm/kong/values/dev.yaml`

## Verification

```bash
# Check ingress created
kubectl get ingress -n kong-system dev-kong-kong-admin

# Check certificate
kubectl get certificate -n kong-system kong-admin-tls

# Test Admin API access
curl -s <https://kong-admin.dev.goldenpathidp.io/routes> | head -5

# Verify CORS header for Kong Manager
curl -sI <https://kong-admin.dev.goldenpathidp.io/> | grep access-control
```

## Security Considerations

- Admin API is now publicly accessible (protected by TLS)
- In production, add authentication via:
  - Basic auth KongPlugin
  - mTLS client certificates
  - OIDC authentication
  - Network policies restricting access

## Impact

- Non-breaking change
- Kong Manager UI now displays route, service, and plugin data
- Admin API accessible at <https://kong-admin.dev.goldenpathidp.io>
- CORS headers configured for Kong Manager origin
