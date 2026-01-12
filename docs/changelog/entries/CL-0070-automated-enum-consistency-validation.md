---
id: CL-0070-automated-enum-consistency-validation
title: Automated Enum Consistency Validation
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
  - ADR-0114
  - CL-0069
date: 2026-01-06
supported_until: 2028-01-06
breaking_change: false
---

# CL-0070: Automated Enum Consistency Validation

## Summary
Implemented the `validate_enums.py` engine to automate the enforcement of platform-wide metadata enums.

## Changes
- **ADR-0114**: Standardized the decision to use schema-driven validation for metadata fields.
- **scripts/validate_enums.py**: Created the validation engine that scans Markdown and YAML files for drift against `schemas/metadata/enums.yaml`.
- **CI Readiness**: Prepared the script for integration into GitHub Actions as a mandatory Quality Gate.

## Verification
- Verified script execution across `docs/`, `envs/`, and `idp-tooling/`.
- Confirmed error reporting for non-standard enum values.
