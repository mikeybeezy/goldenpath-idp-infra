<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0185-maturity-snapshots-value-ledger
title: 'CL-0185: Add maturity snapshots to value ledger'
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
  - generate_script_matrix.py
  - value_ledger.json
  - PLATFORM_HEALTH
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: MV/MQ
  impact_tier: medium
  potential_savings_hours: 2.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0185: Add maturity snapshots to value ledger

## Summary

Enhanced `generate_script_matrix.py` to write script maturity distribution snapshots to the value ledger, enabling historical tracking of script certification progress.

## Changes

- Added `write_maturity_snapshot()` function to `generate_script_matrix.py`
- Snapshots include: timestamp, total scripts, maturity distribution (M0/M1/M2/M3), certification rate
- Keeps last 30 snapshots for trend analysis
- Added maturity distribution display to PLATFORM_HEALTH.md via `get_maturity_snapshots()` in `platform_health.py`

## Value Ledger Schema Addition

```json
{
  "maturity_snapshots": [
    {
      "timestamp": "2026-01-25T10:00:00Z",
      "total_scripts": 56,
      "maturity_distribution": {"M0": 0, "M1": 4, "M2": 51, "M3": 1},
      "certification_rate": 1.8
    }
  ]
}
```

## Rationale

Governance metrics tracking requires historical data to:
- Measure certification velocity over time
- Identify maturity level trends
- Support V1 readiness calculations
- Provide evidence for audit compliance

## Files Changed

- `scripts/generate_script_matrix.py` - Added maturity snapshot writing
- `scripts/platform_health.py` - Added maturity snapshot reading and display

## Related

- Session: session-2026-01-25-governance-metrics-upgrades
- Capability Ledger Section 21: Born Governed Script Automation
