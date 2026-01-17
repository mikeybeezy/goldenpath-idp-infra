---
id: CL-0121-seamless-build-deployment
title: 'CL-0121: Seamless Build Deployment with Build ID Immutability'
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
relates_to:
  - ADR-0148
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0153
  - CL-0121
  - SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT
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
# CL-0121: Seamless Build Deployment with Build ID Immutability

**Status**: Active
**Date**: 2026-01-13
**Type**: Feature Enhancement
**Scope**: Build & Deployment
**Impact**: High

## Summary

Implemented seamless two-phase deployment with build_id immutability enforcement, providing single-command UX while maintaining proven infrastructure/platform separation pattern.

## Changes

### New Deployment Command

**User-facing single command**:
```bash
make deploy ENV=dev BUILD_ID=13-01-26-03
```

Behind the scenes orchestrates:
1. Phase 1: Terraform infrastructure (VPC, EKS, IAM, Service Accounts)
2. Phase 2: Platform bootstrap (ArgoCD, controllers, applications)
3. Phase 3: Verification (kubectl checks)

### Build ID Immutability Enforcement

Added three-layer validation to prevent build_id reuse:

**Layer 1: Format Validation**
- Terraform variable validation
- Regex: `^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$`
- Example: `13-01-26-03` (DD-MM-YY-NN)

**Layer 2: Registry Duplicate Check**
- Queries `governance-registry` branch via git
- Searches `build_timings.csv` for existing build_id
- Executes during `terraform plan`

**Layer 3: Lifecycle Precondition**
- Fails terraform plan if duplicate found
- Provides clear error message with remediation options
- Can be overridden with `allow_build_id_reuse=true` (emergency only)

### Governance Registry Integration

**Location**: `governance-registry` branch
**File**: `environments/development/latest/build_timings.csv`
**Schema**: 12 columns with inventory tracking

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
```

**Tracks**:
- Build timing and duration
- Exit codes (success/failure)
- Infrastructure inventory (resources added/changed/destroyed)
- Log file locations
- Environment and phase metadata

### Makefile Targets

#### User-Facing
- `make deploy` - Seamless deployment (Phase 1 → Phase 2 → Phase 3)

#### Internal (for debugging/advanced users)
- `make _phase1-infrastructure` - Infrastructure only (terraform apply)
- `make _phase2-bootstrap` - Platform bootstrap (shell script with enable_k8s_resources=true)
- `make _phase3-verify` - Verification checks

#### Flags
- `ALLOW_REUSE_BUILD_ID=true` - Override immutability (emergency only, logged)

### Scripts Added

**scripts/record-build-timing.sh**
- Records build metadata to governance-registry CSV
- Extracts timing from log files
- Commits and pushes to governance-registry branch
- Captures exit codes and duration

### Files Modified

#### Terraform
- `envs/dev/main.tf`:
  - Added `data.external.build_id_check` (queries governance-registry)
  - Added `null_resource.enforce_build_id_immutability` (lifecycle precondition)

- `envs/dev/variables.tf`:
  - Added `build_id` variable with format validation
  - Added `allow_build_id_reuse` variable (default: false)
  - Added `governance_registry_branch` variable (default: "governance-registry")

#### Makefile
- Added `deploy` target
- Added `_phase1-infrastructure` target
- Added `_phase2-bootstrap` target
- Added `_phase3-verify` target
- Enhanced `validate-build-id` function

#### Documentation
- `docs/adrs/ADR-0148-seamless-build-deployment-with-immutability.md`
- `docs/85-how-it-works/ci-terraform/SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT.md`
- `README.md` (updated deployment instructions)

## Problem Solved

### Before This Change

**Manual two-phase deployment**:
```bash
# Step 1: Build infrastructure
cd envs/dev
terraform apply

# Step 2: Bootstrap platform
bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh goldenpath-dev-eks eu-west-2

# Issues:
# - Could accidentally reuse build_id (no validation)
# - Forget to run bootstrap phase
# - No audit trail of builds
# - Manual coordination between phases
```

**Previous refactor attempt (eks-single-build-refactor)**:
```bash
# Tried to consolidate everything in one terraform apply
terraform apply

# Issues:
# - Circular dependencies (module ↔ service accounts)
# - Complex dependency chains
# - Poor error messages (terraform vs kubectl)
# - All-or-nothing (can't retry just bootstrap)
```

### After This Change

**Single seamless command**:
```bash
make deploy ENV=dev BUILD_ID=13-01-26-03

# Benefits:
# ✅ Build ID validated against governance-registry
# ✅ Three-layer immutability enforcement
# ✅ Phases run automatically in sequence
# ✅ Clear error messages (bash + kubectl)
# ✅ Can retry phases independently for debugging
# ✅ Full audit trail in governance-registry
# ✅ Single command UX with phase separation benefits
```

## Migration Impact

### Existing Clusters

**No impact** - existing clusters continue to work. This affects new deployments only.

### New Deployments

**Before**:
```bash
cd envs/dev
terraform apply
bash ../../bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
```

**After**:
```bash
make deploy ENV=dev BUILD_ID=13-01-26-03
```

### Build ID Format

**Must follow format**: `DD-MM-YY-NN`

**Examples**:
- ✅ `13-01-26-01` (13th day, January, 2026, sequence 01)
- ✅ `13-01-26-02` (13th day, January, 2026, sequence 02)
- `13-1-26-1` (missing leading zeros)
- `2026-01-13-01` (wrong order)

### Governance Registry Setup

**First-time setup**:
```bash
# Create governance-registry branch if doesn't exist
git checkout -b governance-registry
mkdir -p environments/development/latest
cat > environments/development/latest/build_timings.csv <<EOF
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
EOF
git add environments/development/latest/build_timings.csv
git commit -m "chore(registry): initialize build timings CSV"
git push origin governance-registry
```

## Testing

### Test Scenarios Validated

1. **Fresh build_id**: ✅ Deploys successfully
2. **Duplicate build_id**: ✅ Fails with clear error message
3. **Override flag**: ✅ Allows reuse with warning
4. **Invalid format**: ✅ Fails at variable validation
5. **Phase 1 failure**: ✅ Phase 2 doesn't run
6. **Phase 2 failure**: ✅ Can retry without rebuilding infrastructure
7. **Registry unavailable**: ✅ Warning but continues (fail-open)

### Test Commands

```bash
# Test fresh build
make deploy ENV=dev BUILD_ID=13-01-26-04

# Test duplicate (should fail)
make deploy ENV=dev BUILD_ID=13-01-26-04

# Test override
make deploy ENV=dev BUILD_ID=13-01-26-04 ALLOW_REUSE_BUILD_ID=true

# Test invalid format (should fail)
make deploy ENV=dev BUILD_ID=2026-01-13-01

# Test phase retry
make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-04
```

## Analytics Enabled

With governance-registry tracking, you can now query:

**Total infrastructure growth**:
```bash
git show origin/governance-registry:environments/development/latest/build_timings.csv | \
  awk -F',' 'NR>1 {total+=$9} END {print "Total resources:", total}'
```

**Build success rate**:
```bash
git show origin/governance-registry:environments/development/latest/build_timings.csv | \
  awk -F',' 'NR>1 {total++; if($7==0) success++} END {print "Success rate:", (success/total)*100"%"}'
```

**Average build duration**:
```bash
git show origin/governance-registry:environments/development/latest/build_timings.csv | \
  awk -F',' 'NR>1 && $3=="terraform-apply" {sum+=$6; count++} END {print "Avg:", sum/count, "seconds"}'
```

## Rollback Plan

If issues arise, rollback to previous pattern:

```bash
# Checkout development branch
git checkout development

# Use old commands
cd envs/dev
terraform apply
bash ../../bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
```

## Future Enhancements

Potential improvements for future iterations:

1. **GitHub Actions Integration**: Automated deployment workflows
2. **Slack Notifications**: Alert on build completion/failure
3. **Cost Tracking**: Correlate build_id with AWS costs
4. **Backstage Integration**: Display build history in IDP UI
5. **Auto-increment**: Automatically generate next build_id
6. **Multi-environment**: Extend to staging/prod with different policies

## Related

- ADR: [ADR-0148](../adrs/ADR-0148-seamless-build-deployment-with-immutability.md)
- Supersedes: ADR-0153 (eks-single-build-refactor, not merged)
- Pattern: Two-phase deployment (development branch proven pattern)
