---
id: CL-0187-rds-deploy-timing-capture
title: 'CL-0187: Add timing capture for rds-deploy target'
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
  - CL-0169-persistent-cluster-build-timing
  - record-build-timing.sh
  - SCRIPT-0046
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.5
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0187: Add timing capture for rds-deploy target

## Summary

Added full timing capture for the `make rds-deploy` target, which previously only captured timing for the nested `rds-apply` call.

## Changes

- Wrapped `rds-deploy` target with log capture and streaming
- Added `record-build-timing.sh` call at end of target
- Log naming follows pattern: `rds-deploy-<env>-rds-<timestamp>.log`

## Rationale

The `rds-deploy` target includes multiple phases:
- `rds-init` (initialization)
- `rds_secrets_preflight.sh` (secrets validation)
- `rds-apply` (Terraform apply)
- `rds-provision-auto` (database provisioning)

Only `rds-apply` was being timed. Now the full deployment duration is captured for accurate reliability metrics.

## Files Changed

- `Makefile` - Updated rds-deploy target with log capture and timing

## Related

- CL-0169: Persistent cluster build timing capture
- Session: session-2026-01-25-governance-metrics-upgrades
