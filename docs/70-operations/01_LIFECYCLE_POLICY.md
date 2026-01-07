---
id: 01_LIFECYCLE_POLICY
title: Lifecycle & Upgrade Policy
type: policy
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0007
  - 35_RESOURCE_TAGGING
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: compliance
status: active
version: 1.0
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# Lifecycle & Upgrade Policy

A placeholder for deprecation and upgrade rules.

## Upgrade Policy

- How often do we upgrade EKS? TBD.

## Deprecation Policy

- How much notice do we give? TBD.
