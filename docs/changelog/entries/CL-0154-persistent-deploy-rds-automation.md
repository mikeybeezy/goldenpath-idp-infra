<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0154
title: Persistent Deploy Auto-Runs Standalone RDS
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - Makefile
  - envs/dev-rds/terraform.tfvars
  - QUICK_REFERENCE.md
  - docs/70-operations/runbooks/RB-0034-persistent-cluster-deployment.md
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - CL-0153-standalone-rds-state
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - rds
  - persistent
  - deployment
  - automation
inheritance: {}
supported_until: 2028-01-20
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: medium
  potential_savings_hours: 2.0
date: 2026-01-20
author: platform-team
---

# Persistent Deploy Auto-Runs Standalone RDS

## Summary

Persistent cluster deployment now auto-runs the standalone RDS workflow to keep
the platform database durable without manual steps.

## Changes

- Added `make rds-deploy ENV=<env>` wrapper (init + apply + provision).
- `make deploy-persistent` now runs `rds-deploy` by default.
- Added `CREATE_RDS=false` to skip RDS creation when desired.
- RDS apply now honors auto-approve for non-interactive runs.
- Updated dev RDS tfvars to the persistent VPC name.

## Files Changed

| File | Change |
|------|--------|
| `Makefile` | Added `rds-deploy` and wired into `deploy-persistent` |
| `envs/dev-rds/terraform.tfvars` | Set `vpc_name` to `goldenpath-dev-vpc` |
| `QUICK_REFERENCE.md` | Documented `rds-deploy` and `CREATE_RDS` |
| `docs/70-operations/runbooks/RB-0034-persistent-cluster-deployment.md` | Updated flow |
