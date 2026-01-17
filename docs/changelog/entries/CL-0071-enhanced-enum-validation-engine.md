---
id: CL-0071-enhanced-enum-validation-engine
title: Enhanced Enum Validation Engine
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
  observability_tier: silver
schema_version: 1
relates_to:
  - ADR-0115-enhanced-enum-validation-engine
  - CL-0070-automated-enum-consistency-validation
  - CL-0071-enhanced-enum-validation-engine
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-06
version: 1.0
date: 2026-01-06
breaking_change: false
---
# CL-0071: Enhanced Enum Validation Engine

## Summary
Upgraded the `validate_enums.py` engine to support recursive dot-path validation and CI-optimized scanning.

## Changes
- **Dot-Path Support**: Added logic to validate nested metadata objects (e.g., `risk_profile.production_impact`).
- **Flexible Mappings**: Transitioned to aKind/Path/Enum mapping model for easier rule extensibility.
- **CI Optimization**: Added positional argument support to enable "Changed Files Only" validation in PR workflows.
- **Governance**: Documented the shift in **ADR-0115**.

## Verification
- Verified script correctly traverses nested dictionary paths.
- Confirmed integration readiness with `ci-metadata-validation.yml`.
