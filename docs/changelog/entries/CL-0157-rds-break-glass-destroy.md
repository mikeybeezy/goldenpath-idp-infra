---
id: CL-0157
title: RDS Break-Glass Destroy Target
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - Makefile
  - docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md
  - docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md
  - docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md
  - QUICK_REFERENCE.md
  - docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md
  - docs/00-foundations/product/CAPABILITY_LEDGER.md
  - docs/extend-capabilities/EC-0011-break-glass-rds-destroy.md
  - session_capture/2026-01-20-persistent-cluster-deployment.md
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - RB-0030-rds-break-glass-deletion
  - RB-0033-persistent-cluster-teardown
  - CL-0156-rds-allow-delete-target
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - rds
  - teardown
  - break-glass
  - terraform
inheritance: {}
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: medium
  potential_savings_hours: 2.0
supported_until: 2028-01-20
date: 2026-01-20
author: platform-team
---

# RDS Break-Glass Destroy Target

## Summary

Added a confirmation-gated `rds-destroy-break-glass` target that disables deletion
protection and destroys standalone RDS via Terraform.

## Changes

- Added `rds-destroy-break-glass` Makefile target (confirmation-gated + logged).
- Target temporarily flips `prevent_destroy` during the break-glass destroy.
- Updated runbooks and reference docs to document the break-glass flow.

## Files Changed

| File | Change |
|------|--------|
| `Makefile` | Added `rds-destroy-break-glass` target |
| `docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md` | Documented break-glass destroy flow |
| `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md` | Added optional standalone RDS destroy step |
| `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md` | Updated deletion procedure language |
| `QUICK_REFERENCE.md` | Added break-glass commands |
| `docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md` | Updated deletion posture |
| `docs/00-foundations/product/CAPABILITY_LEDGER.md` | Updated deletion protection language |
| `docs/extend-capabilities/EC-0011-break-glass-rds-destroy.md` | Marked implemented + aligned design |
| `session_capture/2026-01-20-persistent-cluster-deployment.md` | Added break-glass update log |
