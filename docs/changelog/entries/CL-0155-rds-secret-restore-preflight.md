<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0155
title: RDS Secret Restore Preflight
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - Makefile
  - QUICK_REFERENCE.md
  - docs/70-operations/runbooks/RB-0034-persistent-cluster-deployment.md
  - chat_fil.txt
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - CL-0154-persistent-deploy-rds-automation
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - rds
  - secrets
  - automation
  - preflight
inheritance: {}
supported_until: 2028-01-20
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: low
  potential_savings_hours: 1.0
date: 2026-01-20
author: platform-team
---

# RDS Secret Restore Preflight

## Summary

`rds-deploy` now restores any Secrets Manager entries that are scheduled for
deletion and adopts existing secrets into state before attempting a create.
This removes the seven-day recovery window blocker and avoids
`ResourceExistsException` when secrets already exist.

## Changes

- Added `RESTORE_SECRETS` preflight to `make rds-deploy` (default: true).
- Preflight also imports existing secrets into Terraform state when needed.
- Added `RESTORE_SECRETS=false` override for cases where restore is undesired.
- Documented the behavior in quick reference and runbook guidance.

## Files Changed

| File | Change |
|------|--------|
| `Makefile` | Restore preflight in `rds-deploy` |
| `QUICK_REFERENCE.md` | Added `RESTORE_SECRETS` usage |
| `docs/70-operations/runbooks/RB-0034-persistent-cluster-deployment.md` | Added preflight note |
| `chat_fil.txt` | Added quick usage example |
