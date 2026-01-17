---
id: ADR-0162
title: Kong Ingress DNS Strategy for Platform Tooling
type: adr
status: accepted
date: 2026-01-16
deciders:
  - platform-team
domain: platform-core
owner: platform-team
lifecycle: active
schema_version: 1
tags:
  - kong
  - ingress
  - dns
  - tooling
relates_to:
  - 45_DNS_MANAGEMENT
  - ADR-0005
  - CL-0135
  - CL-0136
---
## Status

Accepted

## Context

Platform tooling applications (Backstage, Keycloak, ArgoCD, Grafana) are deployed on EKS clusters and need to be accessible to developers and operators. Previously, access required kubectl port-forwarding for each service, which:

1. **Poor Developer Experience**: Requires kubectl access and manual port-forward commands
2. **No Bookmarkable URLs**: Can't share links to specific Backstage entities or Grafana dashboards
3. **Session Management**: Port-forwards timeout and need to be re-established
4. **Security Inconsistency**: Different access patterns for different services

Kong is already deployed as the API Gateway and Ingress Controller. Cert-manager is configured with Let's Encrypt for automated TLS certificate provisioning.

## Decision

Adopt a standardized Kong Ingress pattern for all platform tooling applications with environment-specific DNS subdomains.

### DNS Naming Convention

```text
<service>.<env>.goldenpathidp.io     # Dev and Staging
<service>.goldenpathidp.io           # Production
```

### Services Exposed via Ingress

|Service|Dev|Staging|Prod|
|---------|-----|---------|------|
|Backstage|backstage.dev.goldenpathidp.io|backstage.staging.goldenpathidp.io|backstage.goldenpathidp.io|
|Keycloak|keycloak.dev.goldenpathidp.io|keycloak.staging.goldenpathidp.io|keycloak.goldenpathidp.io|
|ArgoCD|argocd.dev.goldenpathidp.io|argocd.staging.goldenpathidp.io|argocd.goldenpathidp.io|
|Grafana|grafana.dev.goldenpathidp.io|grafana.staging.goldenpathidp.io|grafana.goldenpathidp.io|

### Services NOT Exposed (Internal Only)

|Service|Reason|Access Method|
|---------|--------|---------------|
|Prometheus|Security - metrics data|Port-forward or Grafana|
|Alertmanager|Security - alert management|Port-forward|
|Loki|Backend service|Via Grafana Explore|
|Kong Admin|Security - gateway config|Port-forward|

### Standard Ingress Configuration Pattern

All tooling apps follow this pattern in their Helm values:

```yaml
ingress:
  enabled: true
  ingressClassName: kong
  hostname: <service>.<env>.goldenpathidp.io
  path: /
  pathType: Prefix
  tls: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging  # or letsencrypt-prod
```

### Certificate Issuers by Environment

|Environment|Issuer|Reason|
|-------------|--------|--------|
|dev|letsencrypt-staging|Avoid rate limits, browser warnings acceptable|
|staging|letsencrypt-staging|Testing environment, browser warnings acceptable|
|prod|letsencrypt-prod|Production-trusted certificates required|

### DNS Configuration Options

### Option 1: Wildcard DNS (Recommended)

Configure wildcard records for each environment subdomain:

```text
*.dev.goldenpathidp.io     -> Kong LoadBalancer (dev cluster)
*.staging.goldenpathidp.io -> Kong LoadBalancer (staging cluster)
*.goldenpathidp.io         -> Kong LoadBalancer (prod cluster)
```

### Option 2: Individual Records

Create individual A/CNAME records for each service pointing to the respective Kong LoadBalancer.

## Consequences

### Positive

1. **Consistent Access Pattern**: All tooling accessible via HTTPS with valid certificates
2. **Bookmarkable URLs**: Share links to Backstage entities, Grafana dashboards, ArgoCD apps
3. **No kubectl Required**: Developers don't need cluster access for basic tooling
4. **Security via SSO**: Kong can enforce authentication via Keycloak OIDC
5. **Audit Trail**: All access logged through Kong

### Negative

1. **DNS Dependency**: Requires DNS configuration for each environment
2. **Certificate Management**: cert-manager must be healthy for TLS
3. **Internet Exposure**: Services are publicly accessible (mitigated by SSO)

### Risks and Mitigations

|Risk|Mitigation|
|------|------------|
|Unauthorized access|Keycloak SSO integration via Kong OIDC plugin|
|DDoS on tooling|Kong rate-limiting plugin|
|Certificate expiry|cert-manager auto-renewal|
|DNS misconfiguration|Document in runbook, health checks|

## Implementation

### Files Modified

|File|Change|
|------|--------|
|`backstage-helm/charts/backstage/templates/ingress.yaml`|New template|
|`backstage-helm/charts/backstage/values.yaml`|Ingress defaults|
|`gitops/helm/backstage/values/{dev,staging,prod}.yaml`|Ingress enabled|
|`gitops/helm/argocd/values/{dev,staging,prod}.yaml`|Ingress enabled|
|`gitops/helm/kube-prometheus-stack/values/{dev,staging,prod}.yaml`|Grafana ingress|
|`gitops/helm/keycloak/values/dev.yaml`|Already configured|

### Verification Commands

```bash
# Check all ingress resources
kubectl get ingress -A

# Check certificate status
kubectl get certificate -A

# Get Kong LoadBalancer address
kubectl get svc -n kong-system kong-kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test HTTPS access
curl -I https://backstage.dev.goldenpathidp.io
```

## References

- [Kong Kubernetes Ingress Controller](https://docs.konghq.com/kubernetes-ingress-controller/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
- Living Doc: `docs/70-operations/45_DNS_MANAGEMENT.md`
