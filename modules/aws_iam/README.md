---
id: MODULES_AWS_IAM_README
title: EKS IAM Terraform Module
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - 06_IDENTITY_AND_ACCESS
  - 09_ARCHITECTURE
  - 14_MODULES_OVERVIEW
  - ADR-0031-platform-bootstrap-irsa-service-accounts
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
version: 1.1
dependencies:
  - aws-provider
supported_until: 2028-01-01
breaking_change: false
---
# EKS IAM Module

## Purpose

Creates IAM roles for the EKS cluster and node group, plus optional IRSA roles
for:

- Cluster Autoscaler
- AWS Load Balancer Controller
- OIDC assume-role (optional)

## Inputs

- `cluster_role_name` (string)
- `node_group_role_name` (string)
- `oidc_role_name` (string)
- `enable_oidc_role` (bool)
- `enable_autoscaler_role` (bool)
- `enable_lb_controller_role` (bool)
- `autoscaler_role_name` (string)
- `lb_controller_role_name` (string)
- `autoscaler_service_account_namespace` (string)
- `autoscaler_service_account_name` (string)
- `lb_controller_service_account_namespace` (string)
- `lb_controller_service_account_name` (string)
- `oidc_issuer_url` (string)
- `oidc_provider_arn` (string)
- `oidc_audience` (string)
- `oidc_subject` (string)
- `tags` (map(string), optional)
- `environment` (string, optional)

## Outputs

- Cluster and node role names/ARNs
- Autoscaler role name/ARN
- LB controller role name/ARN

## Notes

- This module does not create Kubernetes ServiceAccounts.
- Requires a valid EKS OIDC provider ARN and issuer URL.
