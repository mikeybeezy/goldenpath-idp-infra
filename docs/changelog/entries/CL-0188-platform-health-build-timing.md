<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0188-platform-health-build-timing
title: 'CL-0188: Add build timing metrics to platform health dashboard'
type: changelog
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - platform_health.py
  - PLATFORM_HEALTH
  - governance-registry
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: MV/MQ
  impact_tier: medium
  potential_savings_hours: 1.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0188: Add build timing metrics to platform health dashboard

## Summary

Integrated build timing data from the governance-registry branch into the PLATFORM_HEALTH.md dashboard, providing visibility into deployment durations.

## Changes

- Added `get_build_timing_stats()` function to `platform_health.py`
- Function reads CSV from `governance-registry:environments/development/latest/build_timings.csv`
- Added "Build Timing Metrics" section to dashboard output
- Displays phase averages with sample counts

## Dashboard Output

```markdown
## Build Timing Metrics

- **Last Updated**: `2026-01-24T15:12:39Z`
- **Source**: `governance-registry:environments/development/latest/build_timings.csv`

| Phase | Avg Duration | Sample Count |
| :--- | :--- | :--- |
| `bootstrap-persistent` | 16m 36s | 5 |
| `teardown-persistent` | 9m 12s | 8 |
| `rds-apply` | 0s | 1 |
```

## Rationale

The platform health dashboard aggregates governance metrics but was missing build timing data. This integration:
- Provides single-pane visibility into deployment performance
- Enables tracking of timing trends over time
- Supports SLO monitoring for deployment durations

## Files Changed

- `scripts/platform_health.py` - Added get_build_timing_stats() and Build Timing Metrics section

## Related

- CL-0169: Persistent cluster build timing capture
- Session: session-2026-01-25-governance-metrics-upgrades
