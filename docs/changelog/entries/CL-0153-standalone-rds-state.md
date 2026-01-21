---
id: CL-0153
title: Standalone RDS State for Persistent Clusters
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - envs/dev/terraform.tfvars
  - envs/dev-rds/terraform.tfvars
  - QUICK_REFERENCE.md
  - docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md
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
  - persistent
  - teardown
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

# Standalone RDS State for Persistent Clusters

## Summary

Persistent clusters now rely on the standalone RDS state (`envs/<env>-rds/`) to
avoid accidental RDS deletion during `terraform destroy`. The platform state
(`envs/<env>/`) no longer creates RDS by default.

## Why

RDS resources in the same Terraform state as EKS/VPC are always destroyed when
that state is destroyed. Teardown safety flags only affect extra cleanup steps,
not `terraform destroy`. Separating RDS into its own state enforces durability
and prevents unintended deletion.

## Changes

- `envs/dev/terraform.tfvars`: `rds_config.enabled=false` to prevent coupled RDS.
- Standalone RDS remains managed in `envs/dev-rds/` via `make rds-apply`.
- Runbook + Quick Reference updated to make the split explicit.

## Operator Notes

- To build persistent clusters: run `make deploy-persistent ENV=dev`, then
  `make rds-apply ENV=dev` + `make rds-provision-auto ENV=dev` as needed.
- To delete RDS: follow `RB-0030-rds-break-glass-deletion.md` and use
  `make rds-destroy-break-glass ENV=<env> CONFIRM_DESTROY_DATABASE_PERMANENTLY=YES`.

## Files Changed

| File | Change |
|------|--------|
| `envs/dev/terraform.tfvars` | Disabled coupled RDS for persistent cluster state |
| `QUICK_REFERENCE.md` | Added standalone RDS guidance and warnings |
| `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md` | Clarified RDS coupling impact |
