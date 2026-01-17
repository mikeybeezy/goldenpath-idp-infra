---
id: MODULES_AWS_EKS_README
title: EKS Cluster Terraform Module
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - 09_ARCHITECTURE
  - 14_MODULES_OVERVIEW
  - ADR-0032-platform-eks-access-model
  - MODULE_AWS_IAM
  - MODULE_VPC
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
  - kubernetes-provider
  - helm-provider
supported_until: 2028-01-01
breaking_change: false
---
# EKS Cluster Module

## Purpose

Creates an EKS cluster, a managed node group, a cluster security group, IAM
roles, and an OIDC provider. Installs core add-ons and optionally storage
add-ons.

## Inputs

- `cluster_name` (string): Cluster name.
- `kubernetes_version` (string): EKS version.
- `vpc_id` (string): VPC ID.
- `subnet_ids` (list(string)): Subnets for cluster/node group.
- `node_group_config` (object): Node group sizing and instance config.
- `access_config` (object, optional): Auth mode and bootstrap permissions.
- `enable_ssh_break_glass` (bool, optional): Enable SSH access.
- `ssh_key_name` (string, optional): EC2 key pair name for SSH.
- `ssh_source_security_group_ids` (list(string), optional): Allowed SSH SGs.
- `addon_versions` (map(string), optional): Pin add-on versions.
- `addon_replica_counts` (map(number), optional): Replica counts for add-ons.
- `enable_storage_addons` (bool, optional): Enable EBS/EFS/snapshot add-ons.
- `tags` (map(string), optional): Tags for resources.
- `environment` (string, optional): Environment tag.

## Outputs

- `cluster_name`
- `cluster_endpoint`
- `cluster_security_group_id`
- `cluster_ca`
- `node_group_name`
- `node_group_role_arn`
- `oidc_issuer_url`
- `oidc_provider_arn`

## Notes

- Creates cluster and node IAM roles internally.
- Core add-ons: `coredns`, `kube-proxy`, `vpc-cni`.
- Storage add-ons are gated by `enable_storage_addons`.

## Failure modes

- Private subnets missing NAT/endpoint routing (nodes fail to join).
- Insufficient IAM permissions for EKS and IAM roles.
