---
id: MODULES_AWS_SG_README
title: Security Group Terraform Module
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - ADR-0003
  - MODULE_VPC
  - MODULE_AWS_NIC
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: 1.0
dependencies:
  - aws-provider
supported_until: 2028-01-01
breaking_change: false
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
