---
id: 70_OPERATIONS_README
title: Operations Documentation
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_LIFECYCLE_POLICY
  - 06_REBUILD_SEQUENCE
  - 10_INFRA_FAILURE_MODES
  - 15_TEARDOWN_AND_CLEANUP
  - 20_TOOLING_APPS_MATRIX
  - 32_TERRAFORM_STATE_AND_LOCKING
  - 36_STATE_KEY_STRATEGY
  - 40-delivery
  - 40_COST_VISIBILITY
  - 80-runbooks
supersedes: []
superseded_by: []
tags:
  - operations
  - index
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.5
supported_until: 2028-01-15
version: 1.0
breaking_change: false
---
## Operations Documentation

This directory contains operational documentation for running and maintaining the Goldenpath IDP platform.

## Contents

|Document|Description|
|----------|-------------|
|[01_LIFECYCLE_POLICY](./01_LIFECYCLE_POLICY.md)|Deprecation and upgrade policies for platform components|
|[06_REBUILD_SEQUENCE](./06_REBUILD_SEQUENCE.md)|Steps to rebuild the platform from scratch|
|[10_INFRA_FAILURE_MODES](./10_INFRA_FAILURE_MODES.md)|Common infrastructure failures and recovery procedures|
|[15_TEARDOWN_AND_CLEANUP](./15_TEARDOWN_AND_CLEANUP.md)|Cluster teardown procedures and orphan resource cleanup|
|[20_TOOLING_APPS_MATRIX](./20_TOOLING_APPS_MATRIX.md)|Configuration requirements for all platform tooling apps|
|[32_TERRAFORM_STATE_AND_LOCKING](./32_TERRAFORM_STATE_AND_LOCKING.md)|Terraform state management and lock handling|
|[36_STATE_KEY_STRATEGY](./36_STATE_KEY_STRATEGY.md)|State key naming conventions for ephemeral/persistent builds|
|[40_COST_VISIBILITY](./40_COST_VISIBILITY.md)|Cost tracking and resource tagging for billing|

## Key Operational Concepts

### Build Lifecycle

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Terraform  │────►│  Bootstrap  │────►│  Tooling    │
│   Apply     │     │  (K8s+Argo) │     │   Apps      │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Orphan    │◄────│  Terraform  │◄────│  Teardown   │
│   Cleanup   │     │   Destroy   │     │   Script    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Ephemeral vs Persistent Clusters

- **Ephemeral**: Short-lived clusters with isolated state (`envs/dev/builds/{build_id}/terraform.tfstate`)
- **Persistent**: Long-running clusters with shared state (`envs/dev/terraform.tfstate`)

See [36_STATE_KEY_STRATEGY](./36_STATE_KEY_STRATEGY.md) for details.

### Tooling Apps Stack

The platform deploys these core applications via Argo CD:

|Layer|Apps|
|-------|------|
|Foundation|external-secrets, cert-manager|
|Identity|keycloak|
|Gateway|kong|
|Portal|backstage|
|Observability|prometheus, grafana, loki, fluent-bit|

See [20_TOOLING_APPS_MATRIX](./20_TOOLING_APPS_MATRIX.md) for configuration requirements.

## Related Documentation

- **Runbooks**: [docs/80-runbooks/](../80-runbooks/) - Step-by-step procedures for common tasks
- **Delivery**: [docs/40-delivery/](../40-delivery/) - CI/CD and deployment workflows
- **ADRs**: [docs/adrs/](../adrs/) - Architecture Decision Records
- **How It Works**: [docs/85-how-it-works/](../85-how-it-works/) - Technical deep-dives

## Quick Links

- [Teardown a cluster](./15_TEARDOWN_AND_CLEANUP.md)
- [Unlock stuck Terraform state](./32_TERRAFORM_STATE_AND_LOCKING.md)
- [Configure tooling apps](./20_TOOLING_APPS_MATRIX.md)
- [Recover from failures](./10_INFRA_FAILURE_MODES.md)
