---
id: CL-0082-value-heartbeat-roi-telemetry
title: 'CL-0082: Value Heartbeat ROI Telemetry (Realized Value)'
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
relates_to:
  - ADR-0121
  - CL-0082
  - value_ledger.json
  - vq_logger.py
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
---
# CL-0082: Value Heartbeat ROI Telemetry (Realized Value)

## Summary
Transitioned the VQ (Value Quantification) framework from static "Potential Value" tags to live "Realized Value" metrics by instrumenting successful automation runs.

## Changes
- **Implemented** `scripts/lib/vq_logger.py`: A lightweight telemetry engine that records successful script executions.
- **Created** `.goldenpath/value_ledger.json`: A persistent, internal storage for cumulative reclaimed hours.
- **Integrated** Heartbeats into `validate_metadata.py` and `standardize_metadata.py`.
- **Enhanced** `bin/governance pulse`: Now displays total reclaimed hours in the mission summary.
- **Embedded** ROI into `PLATFORM_HEALTH.md`: Realized value is now visible alongside V1 Readiness.

## Impact
- Provides live, auditable proof of platform efficiency.
- Replaces "Potential ROI" with "Realized ROI" in management reporting.
- Current Baseline: **3.0 Hours** reclaimed through core governance loops.
