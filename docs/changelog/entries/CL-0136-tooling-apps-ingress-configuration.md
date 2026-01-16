---
id: CL-0136-tooling-apps-ingress-configuration
title: Platform Tooling Apps Ingress Configuration
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - backstage
  - argocd
  - grafana
  - keycloak
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
  - ADR-0162-kong-ingress-dns-strategy
  - CL-0135-kong-ingress-for-tooling-apps
supersedes: []
superseded_by: []
tags:
  - kong
  - ingress
  - dns
  - tooling
inheritance: {}
value_quantification:
  vq_class: "\u26AB LV/LQ"
  impact_tier: medium
  potential_savings_hours: 4.0
supported_until: 2028-01-16
version: '1.0'
breaking_change: false
---

# CL-0136: Platform Tooling Apps Ingress Configuration

**Type**: Feature
**Component**: Platform Tooling / Kong Ingress
**Date**: 2026-01-16
**Related**: ADR-0162, CL-0135

## Summary

Configured Kong Ingress for all platform tooling applications (Backstage, ArgoCD, Grafana) across all environments, enabling DNS-based HTTPS access without port-forwarding.

## Changes

### Backstage Ingress

Added new ingress template to Backstage Helm chart and configured for all environments:

| File | Change |
|------|--------|
| `backstage-helm/charts/backstage/templates/ingress.yaml` | New template |
| `backstage-helm/charts/backstage/values.yaml` | Default ingress config |
| `gitops/helm/backstage/values/dev.yaml` | `backstage.dev.goldenpath.io` |
| `gitops/helm/backstage/values/staging.yaml` | `backstage.staging.goldenpath.io` |
| `gitops/helm/backstage/values/prod.yaml` | `backstage.goldenpath.io` |

### ArgoCD Ingress

Configured ArgoCD server ingress with `--insecure` flag for TLS termination at Kong:

| File | Change |
|------|--------|
| `gitops/helm/argocd/values/dev.yaml` | `argocd.dev.goldenpath.io` |
| `gitops/helm/argocd/values/staging.yaml` | `argocd.staging.goldenpath.io` |
| `gitops/helm/argocd/values/prod.yaml` | `argocd.goldenpath.io` |

### Grafana Ingress

Configured Grafana ingress within kube-prometheus-stack with root_url setting:

| File | Change |
|------|--------|
| `gitops/helm/kube-prometheus-stack/values/dev.yaml` | `grafana.dev.goldenpath.io` |
| `gitops/helm/kube-prometheus-stack/values/staging.yaml` | `grafana.staging.goldenpath.io` |
| `gitops/helm/kube-prometheus-stack/values/prod.yaml` | `grafana.goldenpath.io` |

### Documentation Updated

| Document | Change |
|----------|--------|
| `docs/70-operations/20_TOOLING_APPS_MATRIX.md` | Added Tooling Access URLs section |
| `docs/70-operations/45_DNS_MANAGEMENT.md` | New living doc for DNS management |
| `docs/adrs/ADR-0162-kong-ingress-dns-strategy.md` | New ADR documenting strategy |

## Access URLs

### Dev Environment

| Service | URL |
|---------|-----|
| Backstage | `https://backstage.dev.goldenpath.io` |
| Keycloak | `https://keycloak.dev.goldenpath.io` |
| ArgoCD | `https://argocd.dev.goldenpath.io` |
| Grafana | `https://grafana.dev.goldenpath.io` |

### Staging Environment

| Service | URL |
|---------|-----|
| Backstage | `https://backstage.staging.goldenpath.io` |
| Keycloak | `https://keycloak.staging.goldenpath.io` |
| ArgoCD | `https://argocd.staging.goldenpath.io` |
| Grafana | `https://grafana.staging.goldenpath.io` |

### Production Environment

| Service | URL |
|---------|-----|
| Backstage | `https://backstage.goldenpath.io` |
| Keycloak | `https://keycloak.goldenpath.io` |
| ArgoCD | `https://argocd.goldenpath.io` |
| Grafana | `https://grafana.goldenpath.io` |

## DNS Requirements

Configure wildcard DNS or individual records pointing to Kong LoadBalancer:

```bash
# Get Kong LoadBalancer address
kubectl get svc -n kong-system kong-kong-proxy \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Verification

```bash
# Check ingress resources
kubectl get ingress -A

# Check certificate status
kubectl get certificate -A

# Test access (after DNS configured)
curl -I https://backstage.dev.goldenpath.io
```

## Rollback

To disable ingress for any service, set `ingress.enabled: false` in the respective values file and sync via ArgoCD.
