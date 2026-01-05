---
id: CL-0059
title: 'CL-0059: PR #156 – ECR Pipeline Stabilization and Metadata Compliance'
type: changelog
category: changelog
version: 1.0
owner: platform-team
status: released
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
lifecycle:
  supported_until: 2028-12-31
  breaking_change: false
relates_to:
  - ADR-0098
---

# CL-0059: PR #156 – ECR Pipeline Stabilization and Metadata Compliance

## Summary

This change stabilizes the ECR pipeline PR workflow and enforces metadata compliance across the repository. Key improvements include:
- Fixed duplicate `enforcement` keys and comment indentation in policy YAML files.
- Updated PR guardrail workflow to require explicit checklist selections.
- Standardized pre‑commit formatting and YAML linting across all relevant files.
- Added deep‑copy fix in `scripts/standardize_metadata.py`.
- Refactored domain‑based catalog placeholders with proper indentation.
- Updated documentation and ADR (ADR‑0098) to capture the new PR gate standards.

## Impact

All CI checks now pass for PR #156 targeting `development`. The repository now has consistent guardrails and linting, reducing future merge blockers.

## References

- ADR‑0098: Standardized PR Gates for ECR Pipeline
- PR #156: https://github.com/mikeybeezy/goldenpath-idp-backstage/pull/156
