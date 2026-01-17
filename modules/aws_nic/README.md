---
id: MODULES_AWS_NIC_README
title: Network Interface Terraform Module
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - 09_ARCHITECTURE
  - 14_MODULES_OVERVIEW
  - MODULE_AWS_COMPUTE
  - MODULE_AWS_SG
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
