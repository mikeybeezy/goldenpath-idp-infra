---
id: MODULES_AWS_NIC_README
title: Network Interface Terraform Module
type: documentation
category: modules
version: 1.0
owner: platform-team
status: active
dependencies:
- aws-provider
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 09_ARCHITECTURE
- MODULE_AWS_COMPUTE
- MODULE_AWS_SG
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
