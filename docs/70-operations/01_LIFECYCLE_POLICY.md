---
id: 01_LIFECYCLE_POLICY
title: Lifecycle & Upgrade Policy
type: policy
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0007
  - 35_RESOURCE_TAGGING
category: compliance
supported_until: 2028-01-01
version: 1.0
breaking_change: false
---

# Lifecycle & Upgrade Policy

A placeholder for deprecation and upgrade rules.

## Upgrade Policy

- How often do we upgrade EKS? TBD.

## Deprecation Policy

- How much notice do we give? TBD.
