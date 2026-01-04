---
id: MODULE_AWS_IAM
title: EKS IAM Terraform Module
type: documentation
category: modules
version: 1.1
owner: platform-team
status: active
dependencies:
  - aws-provider
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - 09_ARCHITECTURE
  - 06_IDENTITY_AND_ACCESS
  - ADR-0031
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
