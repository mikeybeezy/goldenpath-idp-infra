---
id: README
title: Route Table Module
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
