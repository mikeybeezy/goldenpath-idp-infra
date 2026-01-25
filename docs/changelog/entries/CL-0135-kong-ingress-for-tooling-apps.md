<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0135-kong-ingress-for-tooling-apps
title: Kong Ingress for Tooling Apps
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - backstage
  - keycloak
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0162
  - CL-0133-idp-stack-deployment-runbook
  - CL-0134-backstage-catalog-governance-registry-sync
  - CL-0135-kong-ingress-for-tooling-apps
  - CL-0136-tooling-apps-ingress-configuration
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - kong
  - ingress
  - backstage
  - dns
inheritance: {}
supported_until: 2028-01-16
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 2.0
version: '1.0'
breaking_change: false
---

## CL-0135: Kong Ingress for Tooling Apps

**Type**: Feature
**Component**: Backstage / Kong
**Date**: 2026-01-16
**Related**: CL-0133, CL-0134

## Summary

Added Kong Ingress support to the Backstage Helm chart, enabling DNS-based access to Backstage without port-forwarding.

## Changes

### New Template: ingress.yaml

Added `backstage-helm/charts/backstage/templates/ingress.yaml` with:

- Conditional rendering via `ingress.enabled`
- Kong ingress class support
- TLS configuration with cert-manager integration
- Configurable hostname, path, and pathType

### Values Updates

|Environment|Hostname|Cert Issuer|
|-------------|----------|-------------|
|dev|`backstage.dev.goldenpathidp.io`|letsencrypt-staging|
|staging|`backstage.staging.goldenpathidp.io`|letsencrypt-staging|
|prod|`backstage.goldenpathidp.io`|letsencrypt-prod|

### Configuration Pattern

```yaml
ingress:
  enabled: true
  ingressClassName: kong
  hostname: backstage.dev.goldenpathidp.io
  path: /
  pathType: Prefix
  tls: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
```

### Base URL Update

Updated `appConfig` to remove `:7007` port from base URLs since Kong handles routing:

```yaml
app:
  baseUrl: ${BASE_URL}  # Was: ${BASE_URL}:7007
backend:
  baseUrl: ${BASE_URL}  # Was: ${BASE_URL}:7007
```

## Benefits

1. **No Port-Forwarding Required**: Access Backstage via `https://backstage.dev.goldenpathidp.io`
2. **TLS Termination**: Kong handles HTTPS with Let's Encrypt certificates
3. **Consistent Pattern**: Matches Keycloak ingress configuration
4. **Environment Isolation**: Each environment has its own subdomain

## DNS Requirements

Ensure the following DNS records exist (or wildcard `*.goldenpathidp.io`):

|Record|Type|Target|
|--------|------|--------|
|`backstage.dev.goldenpathidp.io`|A/CNAME|Kong LoadBalancer|
|`backstage.staging.goldenpathidp.io`|A/CNAME|Kong LoadBalancer|
|`backstage.goldenpathidp.io`|A/CNAME|Kong LoadBalancer|

## Verification

```bash
# After ArgoCD sync, verify ingress created
kubectl get ingress -n backstage

# Check certificate status
kubectl get certificate -n backstage

# Access Backstage (once DNS propagates)
curl -I https://backstage.dev.goldenpathidp.io
```

## Files Modified

|File|Change|
|------|--------|
|`backstage-helm/charts/backstage/templates/ingress.yaml`|New template|
|`backstage-helm/charts/backstage/values.yaml`|Added ingress defaults|
|`gitops/helm/backstage/values/dev.yaml`|Enabled Kong ingress|
|`gitops/helm/backstage/values/staging.yaml`|Enabled Kong ingress|
|`gitops/helm/backstage/values/prod.yaml`|Enabled Kong ingress|
