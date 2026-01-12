---
id: value_ledger
title: Value Ledger (VQ)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
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
category: platform
---

# Value Ledger (VQ)

This file documents `value_ledger.json`, the Value Quantification (VQ) ledger.
The ledger records time reclaimed by automation scripts and aggregates the
running total in `total_reclaimed_hours`.

## How it is updated

Automation scripts call `vq_logger.log_heartbeat(...)` to append entries. Each
entry captures:

- timestamp
- script name
- reclaimed_hours

## Primary generators

- `scripts/sync_ecr_catalog.py`

Other scripts may add entries when they implement VQ logging via
`scripts/lib/vq_logger.py`.
