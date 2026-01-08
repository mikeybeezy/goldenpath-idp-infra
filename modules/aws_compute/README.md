---
id: MODULES_AWS_COMPUTE_README
title: EC2 Compute Terraform Module
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
schema_version: 1
relates_to:
  - 09_ARCHITECTURE
  - MODULE_AWS_NIC
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

# EC2 Compute Module

## Purpose

Creates a dedicated ENI and an EC2 instance that uses that ENI as its primary
network interface. Use this when you want explicit control over the ENI and
its tags.

## Inputs

- `name` (string): Name tag for the instance.
- `ami_id` (string): AMI ID for the instance.
- `instance_type` (string): EC2 instance type.
- `subnet_id` (string): Subnet where the ENI and instance live.
- `security_group_ids` (list(string)): SGs attached to the ENI.
- `ssh_key_name` (string, optional): EC2 key pair name.
- `user_data` (string, optional): User data script.
- `iam_instance_profile` (string, optional): IAM instance profile name.
- `network_interface_description` (string, optional): ENI description.
- `root_volume_size` (number, optional): Root volume size in GB.
- `root_volume_type` (string, optional): Root volume type (default `gp3`).
- `root_volume_encrypted` (bool, optional): Encrypt root volume.
- `tags` (map(string), optional): Extra tags.
- `environment` (string, optional): Environment tag value.

## Outputs

- `instance_id`: EC2 instance ID.
- `private_ip`: Instance private IP.
- `network_interface_id`: ENI ID.

## Notes

- The instance is attached to the ENI via `primary_network_interface`.
- Security groups must allow required inbound/outbound traffic.

## Failure modes

- Invalid AMI ID or instance type.
- Missing IAM permissions for EC2 or ENI creation.
