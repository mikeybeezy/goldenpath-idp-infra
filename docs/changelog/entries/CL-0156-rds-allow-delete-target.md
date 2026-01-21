---
id: CL-0156
title: RDS Deletion Protection Toggle Target
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - Makefile
  - docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md
  - QUICK_REFERENCE.md
  - chat_fil.txt
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - RB-0030-rds-break-glass-deletion
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - rds
  - teardown
  - break-glass
inheritance: {}
supported_until: 2028-01-20
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: medium
  potential_savings_hours: 1.0
date: 2026-01-20
author: platform-team
---

# RDS Deletion Protection Toggle Target

## Summary

Added a `make rds-allow-delete` target to disable deletion protection on the
standalone RDS instance during break-glass teardown.

## Changes

- Added `rds-allow-delete` in the Makefile with confirmation gating.
- Documented the target in the persistent teardown runbook and quick reference.

## Files Changed

| File | Change |
|------|--------|
| `Makefile` | Added `rds-allow-delete` |
| `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md` | Added break-glass step |
| `QUICK_REFERENCE.md` | Added usage example |
| `chat_fil.txt` | Added quick usage example |
