---
id: CL-0009-autoscaler-ephemeral-discovery
title: 'CL-0009: Autoscaler discovery for ephemeral clusters'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - CL-0009
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-04
version: '1.0'
breaking_change: false
---

# CL-0009: Autoscaler discovery for ephemeral clusters

Date: 2025-12-31
Owner: platform-team
Scope: dev, EKS, cluster-autoscaler
Related: <https://github.com/mikeybeezy/goldenpath-idp-infra/pull/78>

## Summary

- Ensure cluster-autoscaler targets the effective ephemeral cluster name at bootstrap.
- Tag the managed node group for autoscaler auto-discovery.
- Enable Terraform-managed K8s service accounts and storage add-ons in dev.

## Impact

- Dev bootstrap now patches the autoscaler app with the resolved cluster name.
- Autoscaler can discover and scale the node group via ASG tags.
- Dev runs enable storage add-ons and IRSA-managed service accounts.

## Changes

### Added

- Bootstrap patching of autoscaler Helm parameter for `autoDiscovery.clusterName`.
- Autoscaler discovery tags on the EKS node group.

### Changed

- Dev environment enables storage add-ons and Terraform-managed K8s resources.

### Fixed

- Autoscaler discovery for ephemeral cluster names.

### Deprecated

- Not required.

### Removed

- Not required.

### Documented

- Not required.

### Known limitations

- Not required.

## Rollback / Recovery

- Revert PR 78 or disable `enable_k8s_resources`/`enable_storage_addons` in dev tfvars.

## Validation

- Not run.
