---
id: CL-0124-enforce-makefile-usage
title: 'CL-0124: Enforce Makefile Usage'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
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
supported_until: '2028-01-01'
---

# CL-0124: Enforce Makefile Usage

## Overview
Implemented a guardrail to prevent direct execution of `terraform apply` commands, ensuring all deployments go through the standardized `Makefile` workflow for telemetry and safety. Introduced a "Break-Glass" variable for emergency bypass.

## Changes

### Governance
- Added `docs/adrs/ADR-0151-enforce-makefile-usage.md`
- Added `docs/70-operations/runbooks/RB-0030-break-glass-protocol.md`

### Infrastructure (Terraform)
- **Module**: `envs/dev`
  - Added `variable "is_secure_flow"` (default: false).
  - Added `variable "break_glass"` (default: false).
  - Added `resource "null_resource" "governance_check"` to fail execution if neither variable is true.

### Automation (Makefile)
- **Modified**: `Makefile`
  - Updated `deploy-cluster` and `terraform-apply` targets to pass `-var="is_secure_flow=true"`.

## Verification
- Validated that `terraform apply` fails by default.
- Validated that `make deploy ENV=dev` succeeds.
- Validated that `terraform apply -var="break_glass=true"` succeeds (Break-Glass).
