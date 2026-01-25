<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
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
  - 35_RESOURCE_TAGGING
  - 70_OPERATIONS_README
  - ADR-0007-platform-environment-model
  - CL-0021-doc-taxonomy-refactor
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
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
