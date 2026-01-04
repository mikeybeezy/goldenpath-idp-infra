---
id: README
title: Network Interface Module
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

# Network Interface Module

## Purpose
Creates a standalone ENI in a subnet with optional static private IPs.

## Inputs
- `name` (string): Name tag for the ENI.
- `subnet_id` (string): Subnet ID.
- `security_group_ids` (list(string), optional).
- `private_ips` (list(string), optional).
- `description` (string, optional).
- `tags` (map(string), optional).
- `environment` (string, optional).

## Outputs
- `network_interface_id`: ENI ID.

## Notes
- Useful when attaching ENIs to instances or other resources later.
