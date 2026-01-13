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
  - Added `aws_vpc_endpoint` resources for:
    - `ecr.api` (Interface)
    - `ecr.dkr` (Interface)
    - `s3` (Gateway)
- **Module**: `envs/dev`
  - Updated `main.tf` to inject necessary Security Groups for endpoints (if logic requires).

### Validation
- Validated via `terraform plan` to ensure endpoints attach to private route tables.
- Verification target: Deployment of `goldenpath-dev-eks` with functional node bootstrapping.
