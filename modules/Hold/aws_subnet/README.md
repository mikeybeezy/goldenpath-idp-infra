---
id: MODULES_AWS_SUBNET_README
title: Subnet Terraform Module
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 09_ARCHITECTURE
  - MODULE_VPC
  - MODULE_AWS_ROUTE_TABLE
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

# Subnet Module

## Purpose

Creates public and private subnets in a VPC from declarative lists.

## Inputs

- `vpc_id` (string): VPC ID to attach subnets to.
- `public_subnets` (list(object), optional): Public subnet definitions.
- `private_subnets` (list(object), optional): Private subnet definitions.
- `tags` (map(string), optional): Common tags for all subnets.
- `environment` (string, optional): Environment tag.

## Outputs

- `public_subnet_ids`
- `private_subnet_ids`

## Notes

- Each subnet entry requires `name`, `cidr_block`, and `availability_zone`.
