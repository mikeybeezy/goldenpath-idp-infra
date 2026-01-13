---
id: CL-0122-vpc-endpoints-implementation
title: 'CL-0122: VPC Endpoints Implementation'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---

# CL-0122: VPC Endpoints Implementation

## Overview
Added AWS VPC Endpoints to the networking layer to resolve `NodeCreationFailure` issues in private EKS clusters. This ensures robust, private connectivity to ECR and S3 without relying on NAT Gateways.

## Changes

### Governance
- Added `docs/adrs/ADR-0152-vpc-endpoints-for-private-clusters.md`

### Infrastructure (Terraform)
- **Module**: `modules/vpc`
  - Refactored to support Dynamic Interface Endpoints (`aws_vpc_endpoint.interface` loop).
  - Added explicit `aws_vpc_endpoint_route_table_association` for S3 Gateway Endpoint to fix routing issues.
- **Environment**: `envs/dev`
  - Enabled Full Suite of Endpoints: `ec2`, `eks`, `sts`, `ssm`, `logs`, `ecr.api`, `ecr.dkr`.

## Capabilities Delivered
- **VPC Interface Endpoints**: EC2, EKS, SSM, ECR (API/DKR), STS.
- **Explicit S3 Route**: The S3 Gateway Endpoint is now correctly routed in the Private Route Table.
- **Strict IAM**: Node Role has SSM Core permissions (`AmazonSSMManagedInstanceCore`).
- **No NAT Dependency**: The Critical Boot Path is entirely Private and reliable.

### Validation
- **Verified**: `kubectl get nodes` returns 4 Ready nodes in private subnets.
- **Verified**: SSM Session Manager connectivity established to private nodes.
- **Verified**: Manual `curl` tests to S3 and ECR from within the node.
