---
id: README
title: Security Group Module
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Security Group Module

## Purpose
Creates a security group with HTTPS ingress and open egress.

## Inputs
- `name` (string): Security group name.
- `description` (string, optional): Description text.
- `vpc_id` (string): VPC ID.
- `ingress_cidr_blocks` (list(string), optional): IPv4 CIDRs for port 443.
- `ingress_ipv6_cidr_blocks` (list(string), optional): IPv6 CIDRs for port 443.
- `tags` (map(string), optional): Extra tags.
- `environment` (string, optional): Environment tag.

## Outputs
- `security_group_id`

## Notes
- Defaults allow HTTPS from all IPv4/IPv6. Tighten for non-dev.
