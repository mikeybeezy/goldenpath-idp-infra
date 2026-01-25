<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 14_MODULES_OVERVIEW
title: Modules Overview
type: adr
applies_to:
  - infra
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-2
  potential_savings_hours: 1.0
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - MODULES_AWS_COMPUTE_README
  - MODULES_AWS_EKS_README
  - MODULES_AWS_IAM_README
  - MODULES_AWS_NIC_README
  - MODULES_AWS_ROUTE_TABLE_README
  - MODULES_AWS_SG_README
  - MODULES_AWS_SUBNET_README
  - MODULES_VPC_README
category: architecture
supported_until: 2028-01-01
version: '1.0'
dependencies:
  - module:aws_compute
  - module:aws_eks
  - module:aws_iam
  - module:aws_nic
  - module:aws_route_table
  - module:aws_sg
  - module:aws_subnet
  - module:vpc
breaking_change: false
---

# Modules Overview

This page summarizes each Terraform module and links to its README.

## Core network

- `modules/vpc/README.md`: VPC, IGW, NAT gateway, and shared tags.
- `modules/aws_subnet/README.md`: Public/private subnets from declarative lists.
- `modules/aws_route_table/README.md`: Route tables and subnet associations.
- `modules/aws_sg/README.md`: HTTPS security group (tighten for non-dev).

## EKS

- `modules/aws_eks/README.md`: EKS cluster, node group, OIDC, and add-ons.
- `modules/aws_iam/README.md`: EKS IAM roles, OIDC trust, and policies.

## Compute and networking

- `modules/aws_compute/README.md`: EC2 instance with user data and tags.
- `modules/aws_nic/README.md`: Network interface with security group attach.

## Notes

- Each module README lists inputs, outputs, and caveats.
- Use module READMEs as the source of truth for supported variables.
