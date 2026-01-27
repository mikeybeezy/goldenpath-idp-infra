---
id: CL-0186-certification-tracking-ci
title: 'CL-0186: Add certification tracking to script-certification-gate'
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
schema_version: 1
relates_to:
  - script-certification-gate.yml
  - SCRIPT_CERTIFICATION_MATRIX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: MV/LQ
  impact_tier: low
  potential_savings_hours: 1.0
version: '1.0'
breaking_change: false
---

# CL-0186: Add certification tracking to script-certification-gate

## Summary

Added a metrics recording step to the script-certification-gate workflow to track pass/fail rates for script certification checks.

## Changes

- Added "Record certification metrics" step to `script-certification-gate.yml`
- Step runs on all certification checks (pass or fail)
- Outputs result to GitHub Actions log with `::notice::` annotations
- Provides visibility into certification gate effectiveness

## Metrics Captured

- Timestamp of check
- PR number
- Result (pass/fail)
- GitHub Actions annotations for visibility

## Rationale

Tracking certification pass/fail rates enables:
- Measuring developer compliance velocity
- Identifying scripts needing remediation
- Supporting governance reporting
- Audit trail for certification enforcement

## Files Changed

- `.github/workflows/script-certification-gate.yml` - Added metrics recording step

## Related

- Session: session-2026-01-25-governance-metrics-upgrades
- ADR-0030: CI Role Permissions
