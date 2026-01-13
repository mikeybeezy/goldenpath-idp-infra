---
id: CL-0123-enhanced-build-telemetry
title: 'CL-0123: Enhanced Build Telemetry'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---

# CL-0123: Enhanced Build Telemetry

## Overview
Upgraded the platform build logging system to capture **Resource Churn** metrics. This allows for better correlation between build duration and build magnitude.

## Changes

### Governance
- Added `docs/adrs/ADR-0150-enhanced-build-telemetry.md`

### Scripts
- **Modified**: `scripts/generate-build-log.sh`
  - Added logic to parse `Apply complete! Resources: X added, Y changed, Z destroyed.`
  - Updated CSV writing logic to append resource counts.

### Data
- **Modified**: `docs/build-timings.csv`
  - Added columns: `added`, `changed`, `destroyed`.

## Verification
- Verified by running a sample terraform apply and ensuring the CSV populates correctly with non-zero resource counts.
