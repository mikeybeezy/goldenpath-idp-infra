---
id: CL-0158
title: Route53 DNS Management via Terraform
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - modules/aws_route53/
  - envs/dev/main.tf
  - envs/dev/variables.tf
  - envs/dev/outputs.tf
  - envs/dev/terraform.tfvars
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0162-kong-ingress-dns-strategy
  - ADR-0170-route53-terraform-module
  - session_capture/2026-01-21-route53-dns-terraform
supersedes: []
superseded_by: []
tags:
  - route53
  - dns
  - terraform
  - kong
inheritance: {}
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: high
  potential_savings_hours: 4.0
supported_until: 2028-01-21
date: 2026-01-21
author: platform-team
---

# Route53 DNS Management via Terraform

## Summary

Implemented Route53 DNS management as Infrastructure-as-Code, enabling the `goldenpathidp.io` domain to automatically resolve to the platform's Kong LoadBalancer as part of Terraform deployments.

## Problem

Platform services (ArgoCD, Keycloak, Backstage, Grafana) were only accessible via `kubectl port-forward` or manually configured DNS records. This created:

1. Poor developer experience (requires kubectl access)
2. Non-reproducible infrastructure (DNS not in IaC)
3. Brittleness on cluster rebuilds (LoadBalancer hostname changes)

## Solution

### New Route53 Terraform Module

Created `modules/aws_route53/` with support for:

- Creating or using existing hosted zones
- Wildcard CNAME records for environment subdomains
- Additional CNAME, A, and Alias record types
- Configurable TTL

### Dev Environment Integration

```hcl
# terraform.tfvars
route53_config = {
  enabled                = true
  domain_name            = "goldenpathidp.io"
  zone_id                = "Z0032802NEMSL43VHH4E"
  create_hosted_zone     = false  # Use existing zone
  create_wildcard_record = true   # *.dev.goldenpathidp.io
  record_ttl             = 300
  kong_service_name      = "dev-kong-kong-proxy"
  kong_service_namespace = "kong-system"
}
```

### Dynamic LoadBalancer Resolution

The module reads the Kong LoadBalancer hostname from Kubernetes at apply time:

```hcl
data "kubernetes_service_v1" "kong_proxy" {
  metadata {
    name      = var.route53_config.kong_service_name
    namespace = var.route53_config.kong_service_namespace
  }
}
```

## DNS Configuration

| Record | Target |
|--------|--------|
| `*.dev.goldenpathidp.io` | Kong LoadBalancer hostname |

**Zone ID:** `Z0032802NEMSL43VHH4E`

**Nameservers (configured in Namecheap):**
- `ns-1333.awsdns-38.org`
- `ns-583.awsdns-08.net`
- `ns-127.awsdns-15.com`
- `ns-1998.awsdns-57.co.uk`

## Files Changed

### Created

| File | Purpose |
|------|---------|
| `modules/aws_route53/main.tf` | Hosted zone and DNS record resources |
| `modules/aws_route53/variables.tf` | Module configuration variables |
| `modules/aws_route53/outputs.tf` | Zone ID, nameservers, FQDN outputs |

### Modified

| File | Change |
|------|--------|
| `envs/dev/main.tf` | Added Route53 module with Kong LB lookup |
| `envs/dev/variables.tf` | Added `route53_config` variable |
| `envs/dev/outputs.tf` | Added Route53 outputs |
| `envs/dev/terraform.tfvars` | Enabled Route53 configuration |

## Benefits

1. **Infrastructure as Code** - DNS configuration tracked in git
2. **Reproducible Deployments** - DNS comes up with cluster automatically
3. **Environment Isolation** - Clear `*.{env}.goldenpathidp.io` pattern
4. **Developer Experience** - Bookmarkable URLs, no port-forward needed

## Verification

```bash
# Verify DNS resolution via Route53 nameserver
dig @ns-1333.awsdns-38.org argocd.dev.goldenpathidp.io +short

# Verify Terraform state is in sync
terraform plan -target=module.route53

# Access services
curl -I https://argocd.dev.goldenpathidp.io  # (after TLS setup)
```

## Future Work

- **ExternalDNS**: Auto-update DNS when LoadBalancer changes
- **TLS/cert-manager**: HTTPS certificates for services
- **Staging/Prod**: Extend to other environments

## Rollback

To remove Route53 management:

```hcl
# terraform.tfvars
route53_config = {
  enabled = false
  domain_name = ""
}
```

Then run `terraform apply`. DNS records will be preserved in Route53 but no longer managed by Terraform.
