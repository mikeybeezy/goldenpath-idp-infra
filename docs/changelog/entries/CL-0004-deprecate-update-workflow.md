<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0004-deprecate-update-workflow
title: '[0.0.4] - 2026-01-02'
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
  - CL-0004-deprecate-update-workflow
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-04
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

## [0.0.4] - 2026-01-02

### Changed

- **CI/CD**: `Apply - Infra Terraform Apply (dev)` workflow now supports resuming/updating ephemeral builds (removed mandatory `new_build=true` check).

### Removed

- **CI/CD**: `Apply - Infra Terraform Update (dev)` workflow has been removed. It is superseded by the improved Apply workflow which handles both creation and updates.
