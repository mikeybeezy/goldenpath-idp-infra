---
id: 45_DNS_MANAGEMENT
title: Platform DNS Management
type: reference
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: dns-revert
  observability_tier: silver
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0162-kong-ingress-dns-strategy
  - 20_TOOLING_APPS_MATRIX
supersedes: []
superseded_by: []
tags:
  - dns
  - kong
  - ingress
  - operations
  - living-doc
inheritance: {}
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 4.0
supported_until: 2028-01-16
version: 1.0
breaking_change: false
---

# Platform DNS Management

This living document captures the DNS configuration strategy, naming conventions, and operational procedures for the GoldenPath IDP platform.

**Last Updated**: 2026-01-16
**Maintainer**: platform-team

---

## DNS Architecture Overview

```text
                    ┌─────────────────────────────────────┐
                    │           DNS Provider              │
                    │     (Route53 / Cloudflare / etc)    │
                    └─────────────────┬───────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
   *.dev.goldenpathidp.io    *.staging.goldenpathidp.io     *.goldenpathidp.io
            │                         │                         │
            ▼                         ▼                         ▼
   ┌────────────────┐       ┌────────────────┐       ┌────────────────┐
   │  Kong LB (Dev) │       │ Kong LB (Stg)  │       │ Kong LB (Prod) │
   └────────┬───────┘       └────────┬───────┘       └────────┬───────┘
            │                         │                         │
            ▼                         ▼                         ▼
   ┌────────────────┐       ┌────────────────┐       ┌────────────────┐
   │  EKS Dev       │       │  EKS Staging   │       │  EKS Prod      │
   │  Cluster       │       │  Cluster       │       │  Cluster       │
   └────────────────┘       └────────────────┘       └────────────────┘
```

---

## DNS Naming Convention

### Pattern

```text
<service>.<environment>.goldenpathidp.io   # Dev and Staging
<service>.goldenpathidp.io                 # Production (no env prefix)
```

### Environment Subdomains

| Environment | Subdomain Pattern | Example |
|-------------|-------------------|---------|
| Development | `*.dev.goldenpathidp.io` | `backstage.dev.goldenpathidp.io` |
| Staging | `*.staging.goldenpathidp.io` | `backstage.staging.goldenpathidp.io` |
| Production | `*.goldenpathidp.io` | `backstage.goldenpathidp.io` |

---

## Current DNS Records

### Platform Tooling Services

| Service | Dev | Staging | Prod |
|---------|-----|---------|------|
| **Backstage** | backstage.dev.goldenpathidp.io | backstage.staging.goldenpathidp.io | backstage.goldenpathidp.io |
| **Keycloak** | keycloak.dev.goldenpathidp.io | keycloak.staging.goldenpathidp.io | keycloak.goldenpathidp.io |
| **ArgoCD** | argocd.dev.goldenpathidp.io | argocd.staging.goldenpathidp.io | argocd.goldenpathidp.io |
| **Grafana** | grafana.dev.goldenpathidp.io | grafana.staging.goldenpathidp.io | grafana.goldenpathidp.io |

### Internal Services (Not Exposed)

| Service | Access Method | Reason |
|---------|---------------|--------|
| Prometheus | Port-forward | Security - metrics data |
| Alertmanager | Port-forward | Security - alert config |
| Loki | Via Grafana | Backend service |
| Kong Admin | Port-forward | Security - gateway config |

---

## Configuration Guide

### Step 1: Get Kong LoadBalancer Address

```bash
# Dev cluster
kubectl get svc -n kong-system kong-kong-proxy \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Example output:
# a1b2c3d4e5f6g7h8i9j0.elb.eu-west-2.amazonaws.com
```

### Step 2: Configure DNS Records

#### Option A: Wildcard DNS (Recommended)

Create wildcard CNAME records pointing to the Kong LoadBalancer:

| Record | Type | Target |
|--------|------|--------|
| `*.dev.goldenpathidp.io` | CNAME | `<dev-kong-lb>.elb.eu-west-2.amazonaws.com` |
| `*.staging.goldenpathidp.io` | CNAME | `<staging-kong-lb>.elb.eu-west-2.amazonaws.com` |
| `*.goldenpathidp.io` | CNAME | `<prod-kong-lb>.elb.eu-west-2.amazonaws.com` |

**Pros**: Single record covers all services, automatic for new services

**Cons**: All subdomains resolve, even non-existent ones

#### Option B: Individual Records

Create individual CNAME records for each service:

| Record | Type | Target |
|--------|------|--------|
| `backstage.dev.goldenpathidp.io` | CNAME | `<dev-kong-lb>...` |
| `keycloak.dev.goldenpathidp.io` | CNAME | `<dev-kong-lb>...` |
| `argocd.dev.goldenpathidp.io` | CNAME | `<dev-kong-lb>...` |
| `grafana.dev.goldenpathidp.io` | CNAME | `<dev-kong-lb>...` |

**Pros**: Explicit control, only known services resolve

**Cons**: Manual update required for each new service

### Step 3: Verify DNS Resolution

```bash
# Check DNS resolution
dig backstage.dev.goldenpathidp.io +short

# Check HTTPS access
curl -I https://backstage.dev.goldenpathidp.io

# Check certificate
openssl s_client -connect backstage.dev.goldenpathidp.io:443 -servername backstage.dev.goldenpathidp.io </dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## TLS Certificate Management

### Certificate Issuers

| Environment | ClusterIssuer | Certificate Type |
|-------------|---------------|------------------|
| dev | `letsencrypt-staging` | Staging (browser warnings) |
| staging | `letsencrypt-staging` | Staging (browser warnings) |
| prod | `letsencrypt-prod` | Production (trusted) |

### Certificate Lifecycle

1. **Provisioning**: cert-manager automatically provisions certificates when Ingress is created
2. **Renewal**: Automatic renewal 30 days before expiry
3. **Monitoring**: Check certificate status via `kubectl get certificate -A`

### Troubleshooting Certificates

```bash
# Check certificate status
kubectl get certificate -A

# Describe certificate for details
kubectl describe certificate <cert-name> -n <namespace>

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager

# Force certificate renewal
kubectl delete certificate <cert-name> -n <namespace>
```

---

## Adding New Services

### Checklist for New Tooling Service

1. **Determine DNS name**: Follow naming convention `<service>.<env>.goldenpathidp.io`
2. **Configure Helm values**: Add ingress configuration to values file
3. **Verify Ingress created**: `kubectl get ingress -n <namespace>`
4. **Verify Certificate issued**: `kubectl get certificate -n <namespace>`
5. **Update DNS** (if not using wildcard): Add CNAME record
6. **Update documentation**: Add to this doc and `20_TOOLING_APPS_MATRIX.md`

### Standard Ingress Values Pattern

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

---

## Operational Procedures

### DNS Failover

If Kong LoadBalancer changes (e.g., cluster rebuild):

1. Get new LoadBalancer address
2. Update DNS records
3. Wait for DNS propagation (TTL-dependent)
4. Verify access to all services

### Emergency DNS Rollback

```bash
# If DNS is misconfigured, services can be accessed via port-forward
kubectl port-forward svc/dev-backstage -n backstage 7007:7007
kubectl port-forward svc/dev-keycloak -n keycloak 8080:8080
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80
```

### Health Checks

```bash
# Check all ingress status
kubectl get ingress -A -o wide

# Check certificate expiry
kubectl get certificate -A -o custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,READY:.status.conditions[0].status,EXPIRY:.status.notAfter

# Check Kong proxy status
kubectl get svc -n kong-system kong-kong-proxy
```

---

## Security Considerations

### Services Exposed via Ingress

All publicly exposed services should be protected by:

1. **Keycloak SSO**: Configure Kong OIDC plugin for authentication
2. **Rate Limiting**: Kong rate-limiting plugin to prevent abuse
3. **WAF Rules**: Kong request-transformer for header validation

### Services NOT Exposed

The following services are intentionally NOT exposed via ingress:

| Service | Reason | Mitigation |
|---------|--------|------------|
| Prometheus | Contains sensitive metrics | Access via Grafana or port-forward |
| Alertmanager | Alert configuration access | Port-forward only |
| Loki | Log data access | Access via Grafana Explore |
| Kong Admin | Gateway configuration | Port-forward only |
| Kubernetes API | Cluster access | VPN or kubectl context |

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-16 | platform-team | Initial document creation |
| 2026-01-16 | platform-team | Added tooling services DNS configuration |

---

## References

- [ADR-0162: Kong Ingress DNS Strategy](../adrs/ADR-0162-kong-ingress-dns-strategy.md)
- [Tooling Apps Matrix](20_TOOLING_APPS_MATRIX.md)
- [Kong Ingress Controller Docs](https://docs.konghq.com/kubernetes-ingress-controller/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
