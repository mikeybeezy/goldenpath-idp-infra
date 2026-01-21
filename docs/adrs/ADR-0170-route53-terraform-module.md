---
id: ADR-0170
title: Route53 DNS Management via Terraform Module
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: terraform-destroy
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0162-kong-ingress-dns-strategy
  - CL-0158-route53-terraform-integration
  - session_capture/2026-01-21-route53-dns-terraform
supersedes: []
superseded_by: []
tags:
  - route53
  - dns
  - terraform
  - infrastructure
inheritance: {}
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: high
  potential_savings_hours: 4.0
supported_until: '2028-01-21'
date: 2026-01-21
deciders:
  - platform-team
---

## Status

Accepted

## Context

The Golden Path IDP platform requires DNS management for developer access to tooling services (ArgoCD, Keycloak, Backstage, Grafana). The domain `goldenpathidp.io` is registered with Namecheap, and services are exposed via Kong Ingress Controller.

### Problem Statement

1. **Manual DNS Management**: DNS records were created manually, not tracked in IaC
2. **Dynamic LoadBalancer**: Kong LoadBalancer hostname changes on cluster rebuild
3. **Environment Isolation**: Need separate DNS patterns for dev/staging/prod
4. **Reproducibility**: DNS should be part of automated deployment

### Previous State

- Domain registered with Namecheap
- No Route53 integration
- Services accessed via port-forward or manual DNS entries

## Decision

Implement Route53 DNS management as a reusable Terraform module with the following characteristics:

### 1. Module Architecture

```
modules/aws_route53/
├── main.tf       # Hosted zone and record resources
├── variables.tf  # Configuration variables
└── outputs.tf    # Zone ID, nameservers, FQDNs
```

### 2. Hosted Zone Strategy

**Delegated DNS (Not Transfer)**

- Keep domain registration at Namecheap
- Delegate DNS queries to Route53 nameservers
- Faster setup, no transfer waiting period

```
Namecheap (registrar) -> Route53 (DNS hosting)
```

### 3. DNS Pattern

```
*.{env}.goldenpathidp.io -> Kong LoadBalancer (per environment)
```

| Environment | Pattern | Example |
|-------------|---------|---------|
| dev | `*.dev.goldenpathidp.io` | `argocd.dev.goldenpathidp.io` |
| staging | `*.staging.goldenpathidp.io` | `argocd.staging.goldenpathidp.io` |
| prod | `*.goldenpathidp.io` | `argocd.goldenpathidp.io` |

### 4. Dynamic LoadBalancer Resolution

The module reads Kong LoadBalancer hostname from Kubernetes at plan/apply time:

```hcl
data "kubernetes_service_v1" "kong_proxy" {
  metadata {
    name      = var.route53_config.kong_service_name
    namespace = var.route53_config.kong_service_namespace
  }
}

locals {
  kong_lb_hostname = try(
    data.kubernetes_service_v1.kong_proxy[0].status[0].load_balancer[0].ingress[0].hostname,
    ""
  )
}
```

### 5. Configuration Interface

```hcl
variable "route53_config" {
  type = object({
    enabled                = bool
    domain_name            = string
    zone_id                = optional(string, "")
    create_hosted_zone     = optional(bool, false)
    create_wildcard_record = optional(bool, true)
    record_ttl             = optional(number, 300)
    kong_service_name      = optional(string, "dev-kong-kong-proxy")
    kong_service_namespace = optional(string, "kong-system")
    cname_records          = optional(map(object({
      target = string
      ttl    = optional(number)
    })), {})
  })
}
```

## Consequences

### Positive

1. **Infrastructure as Code**: DNS configuration tracked in git, auditable
2. **Reproducible Deployments**: DNS comes up automatically with cluster
3. **Environment Isolation**: Clear separation via subdomain pattern
4. **Wildcard Efficiency**: Single record covers all services
5. **Terraform Integration**: Consistent workflow with other infrastructure

### Negative

1. **Terraform Dependency**: DNS updates require Terraform apply
2. **LB Change Detection**: Manual apply needed when LoadBalancer changes
3. **Propagation Delay**: DNS changes take time to propagate globally

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LB hostname changes on rebuild | Future: ExternalDNS for auto-updates |
| Nameserver misconfiguration | Document nameservers, verify with dig |
| Accidental zone deletion | Zone not managed by Terraform (data source) |
| DNS propagation issues | Low TTL (300s), verify via nameserver directly |

## Future Enhancements

### ExternalDNS Integration

Deploy ExternalDNS to automatically update Route53 when LoadBalancer changes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
spec:
  template:
    spec:
      containers:
      - name: external-dns
        image: registry.k8s.io/external-dns/external-dns:v0.14.0
        args:
        - --source=service
        - --source=ingress
        - --provider=aws
        - --domain-filter=goldenpathidp.io
        - --policy=upsert-only
```

This will be implemented in a future session.

## Implementation

### Files Created

| File | Purpose |
|------|---------|
| `modules/aws_route53/main.tf` | Route53 resources |
| `modules/aws_route53/variables.tf` | Module variables |
| `modules/aws_route53/outputs.tf` | Module outputs |

### Files Modified

| File | Change |
|------|--------|
| `envs/dev/main.tf` | Route53 module invocation |
| `envs/dev/variables.tf` | `route53_config` variable |
| `envs/dev/outputs.tf` | Route53 outputs |
| `envs/dev/terraform.tfvars` | Route53 configuration |

### Verification

```bash
# Verify DNS resolution via Route53 nameserver
dig @ns-1333.awsdns-38.org argocd.dev.goldenpathidp.io +short

# Verify Terraform state
terraform plan -target=module.route53

# List Route53 records
aws route53 list-resource-record-sets --hosted-zone-id Z0032802NEMSL43VHH4E
```

## References

- [AWS Route53 Documentation](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/)
- [Terraform AWS Route53 Resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_zone)
- [ExternalDNS](https://github.com/kubernetes-sigs/external-dns)
- ADR-0162: Kong Ingress DNS Strategy
