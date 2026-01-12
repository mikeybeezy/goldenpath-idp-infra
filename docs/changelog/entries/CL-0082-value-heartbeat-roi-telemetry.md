---
id: CL-0082-value-heartbeat-roi-telemetry
title: 'CL-0082: Value Heartbeat ROI Telemetry (Realized Value)'
type: changelog
status: active
owner: platform-team
version: '1.0'
relates_to:
  - ADR-0121
  - vq_logger.py
  - value_ledger.json
supported_until: 2028-01-01
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
