---
id: SESSION_CAPTURE_2026_01_20_PERSISTENT
title: Persistent Cluster Deployment - Terraform Validation Fix
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - QUICK_REFERENCE
  - IMPLEMENTATION_SEQUENCE
  - ADR-0165-rds-user-db-provisioning-automation
---

# Session Capture: Persistent Cluster Deployment - Terraform Validation Fix

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-20
**Timestamp:** 2026-01-20T12:45:00Z
**Branch:** development

## Scope

- Fix Terraform validation blocking persistent cluster deployment
- Enable `build_id = "persistent"` for persistent cluster lifecycle
- Resolve "maze" complexity around ephemeral vs persistent deployment commands

## Work Summary

- Identified root cause: `build_id` variable validation in `envs/dev/variables.tf` enforced `DD-MM-YY-NN` format even for persistent clusters
- Updated validation logic to allow `"persistent"` value when `cluster_lifecycle = "persistent"`
- Confirmed `terraform.tfvars` correctly configured for persistent deployment

## Problem Statement

### Context

User attempted to deploy a persistent cluster using:

```bash
make deploy-persistent ENV=dev
```

### Error

```
Error: Invalid value for variable
  on terraform.tfvars line 8:
     8: build_id = "persistent"

build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01).
This was checked by the validation rule at variables.tf:50,3-13.
```

### Root Cause

The `build_id` variable in `envs/dev/variables.tf` had two validations:
1. Line 47: Correctly allowed empty `build_id` for persistent clusters
2. Line 50-52: **Bug** - Required `DD-MM-YY-NN` format OR empty string, but did NOT allow `"persistent"` as a valid value

```hcl
# Original (buggy) validation
validation {
  condition     = can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id)) || var.build_id == ""
  error_message = "build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)."
}
```

## Artifacts Touched (links)

### Modified

- `envs/dev/variables.tf` - Fixed `build_id` validation to allow `"persistent"` value

### Referenced / Executed

- `envs/dev/terraform.tfvars` - Confirmed correct persistent configuration
- `QUICK_REFERENCE.md` - Validated persistent cluster commands
- `Makefile` - Verified `deploy-persistent` target exists

## Solution

Updated `envs/dev/variables.tf` lines 42-60 to allow three valid states:

```hcl
variable "build_id" {
  type        = string
  description = "Build ID used to suffix ephemeral resources. Must be unique and immutable. Format: DD-MM-YY-NN (e.g., 13-01-26-01). Use 'persistent' for persistent clusters."
  default     = ""
  validation {
    condition     = var.cluster_lifecycle == "persistent" || trimspace(var.build_id) != ""
    error_message = "build_id must be set when cluster_lifecycle is ephemeral."
  }
  validation {
    condition = (
      var.cluster_lifecycle == "persistent" && var.build_id == "persistent"
    ) || (
      can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id))
    ) || (
      var.build_id == ""
    )
    error_message = "build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01) for ephemeral clusters, or 'persistent' for persistent clusters."
  }
}
```

### Validation Logic

| cluster_lifecycle | build_id | Valid? |
|-------------------|----------|--------|
| `persistent` | `"persistent"` | ✅ Yes |
| `ephemeral` | `"20-01-26-01"` | ✅ Yes |
| `ephemeral` | `""` | ❌ No (must be set) |
| `ephemeral` | `"persistent"` | ❌ No (must match DD-MM-YY-NN) |
| `persistent` | `""` | ✅ Yes (default) |

## Validation

- `terraform -chdir=envs/dev validate` (expected: Success after fix)

## Current State / Follow-ups

- Fix applied to `envs/dev/variables.tf`
- User can now run `make deploy-persistent ENV=dev`
- Consider applying same fix to other environment directories if they exist (`envs/staging/`, `envs/prod/`)

**Outstanding**

- Run `make deploy-persistent ENV=dev` to confirm fix works end-to-end
- Monitor deployment for any additional blockers

Signed: Claude Opus 4.5 (2026-01-20T12:45:00Z)

---

## Update — 2026-01-20T12:55:00Z

### Breaking Change Analysis

Verified that the Terraform validation fix introduces **no breaking changes**.

#### Analysis Summary

**Persistent Path (Fixed)**
- `deploy-persistent` target does NOT call `_check-build-id` Makefile validation
- Explicitly passes `-var="cluster_lifecycle=persistent"` to Terraform
- Does not require `DD-MM-YY-NN` format

**Ephemeral Path (Unchanged)**
- Makefile `_check-build-id` target (lines 50-64) still enforces `DD-MM-YY-NN`
- CI workflows pass timestamped BUILD_IDs via `TF_VAR_build_id`
- No changes to ephemeral behavior

#### Validation Matrix

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| `make deploy-persistent ENV=dev` with `build_id="persistent"` | ❌ TF validation fails | ✅ Works |
| `make deploy ENV=dev BUILD_ID=20-01-26-01` | ✅ Works | ✅ Works |
| CI with `TF_VAR_build_id=20-01-26-01` | ✅ Works | ✅ Works |

#### Key Files Verified

- `Makefile` lines 820-908: Persistent targets bypass BUILD_ID validation
- `Makefile` lines 50-64: Ephemeral `_check-build-id` unchanged
- `.github/workflows/ci-bootstrap.yml`: Uses timestamped IDs only

**Outstanding**

- Deploy persistent cluster to confirm end-to-end

Signed: Claude Opus 4.5 (2026-01-20T12:55:00Z)

---

## Update — 2026-01-20T13:16:36Z

### Decision: Safe defaults for persistent teardown

Persistent teardown now defaults to Teardown V4 with safety flags to avoid accidental RDS or Secrets deletion.

**Changes applied**
- `Makefile`: `teardown-persistent` now uses `goldenpath-idp-teardown-v4.sh`
- Defaults set:
  - `DELETE_RDS_INSTANCES=false`
  - `RDS_SKIP_FINAL_SNAPSHOT=false`
  - `DELETE_SECRETS=false`

**Implications**
- Persistent teardown requires explicit opt-in to delete RDS or Secrets.
- Ephemeral behavior remains unchanged (still uses BUILD_ID paths and existing teardown flow).

Signed: Codex (2026-01-20T13:16:36Z)
