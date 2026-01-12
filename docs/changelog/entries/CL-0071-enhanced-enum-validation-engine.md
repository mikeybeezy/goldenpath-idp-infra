---
id: CL-0071-enhanced-enum-validation-engine
title: Enhanced Enum Validation Engine
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
version: 1.0
lifecycle: active
relates_to:
  - ADR-0115
  - CL-0070
date: 2026-01-06
supported_until: 2028-01-06
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
