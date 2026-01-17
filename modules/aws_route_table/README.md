---
id: MODULES_AWS_ROUTE_TABLE_README
title: Route Table Terraform Module
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
  maturity: 1
schema_version: 1
relates_to:
  - 09_ARCHITECTURE
  - 14_MODULES_OVERVIEW
  - MODULE_AWS_SUBNET
  - MODULE_VPC
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
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
# Route Table Module

## Purpose

Creates a route table, optional default route to an IGW or NAT gateway, and
associates it to one or more subnets.

## Inputs

- `vpc_id` (string): VPC ID for the route table.
- `name` (string, optional): Name tag for the route table.
- `gateway_id` (string, optional): Internet gateway ID for the default route.
- `nat_gateway_id` (string, optional): NAT gateway ID for the default route.
- `destination_cidr_block` (string, optional): Default route CIDR.
- `subnet_ids` (list(string), optional): Subnet IDs to associate.
- `tags` (map(string), optional): Extra tags.
- `environment` (string, optional): Environment tag.

## Outputs

- `route_table_id`
- `route_table_association_ids`

## Notes

- Set either `gateway_id` or `nat_gateway_id`, not both.
