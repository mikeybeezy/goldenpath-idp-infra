---
id: CL-0125-build-id-immutability-enforcement
title: 'CL-0125: Build ID Immutability Enforcement via Governance Registry'
type: changelog
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0153-build-id-immutability-enforcement
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ADR-0042-platform-branching-strategy
tags: [governance, ephemeral, build-id, terraform, validation]
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 8.0
supported_until: '2028-01-01'
---

# CL-0125: Build ID Immutability Enforcement via Governance Registry

## Summary
Implemented three-layer enforcement mechanism to prevent accidental reuse of ephemeral cluster `build_id` values, ensuring perpetual immutability by validating against the governance-registry branch.

## Type
**Enhancement** - Added validation infrastructure

## Date
2026-01-13

## Status
✅ **Implemented**

## Problem Statement

Ephemeral EKS clusters use `build_id` (format: `DD-MM-YY-NN`) to uniquely suffix resources and Terraform state keys. Without enforcement, operators could accidentally reuse a build_id, causing:

1. **State Corruption**: Terraform pointing to destroyed resources
2. **Resource Conflicts**: AWS resource name collisions during apply
3. **Audit Trail Loss**: Build timing logs overwritten or conflated
4. **Debugging Confusion**: Multiple builds with identical identifiers

The `governance-registry` branch maintains `environments/development/latest/build_timings.csv` as the authoritative log of all builds. This changelog documents the implementation of automated validation against that registry.

## Solution Implemented

### Three-Layer Enforcement Architecture

#### Layer 1: Format Validation
Terraform variable validation ensures `build_id` matches required format:

```hcl
# envs/dev/variables.tf:50-53
validation {
  condition     = can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id)) || var.build_id == ""
  error_message = "build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)"
}
```

**Timing**: Executes during `terraform validate` and `terraform plan`
**Failure Mode**: Immediate error before any resource planning

#### Layer 2: Registry Duplicate Check
External data source queries governance-registry branch via git:

```hcl
# envs/dev/main.tf:25-50
data "external" "build_id_check" {
  count   = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0
  program = ["bash", "-c", <<-EOT
    # Fetch CSV content from governance-registry branch
    CSV_CONTENT=$(git show "origin/${var.governance_registry_branch}:environments/development/latest/build_timings.csv")

    # Search for duplicate: ,$ENV,$BUILD_ID,
    if echo "$CSV_CONTENT" | grep -q ",$ENV,$BUILD_ID," ; then
      echo '{"exists":"true","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    else
      echo '{"exists":"false","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    fi
  EOT
  ]
}
```

**Timing**: Executes during `terraform plan` (external data sources run during plan phase)
**Failure Mode**: Returns JSON indicating duplicate detection status

#### Layer 3: Lifecycle Precondition
Null resource with precondition fails terraform if duplicate detected:

```hcl
# envs/dev/main.tf:53-74
resource "null_resource" "enforce_build_id_immutability" {
  count = var.cluster_lifecycle == "ephemeral" && var.build_id != "" && !var.allow_build_id_reuse ? 1 : 0

  lifecycle {
    precondition {
      condition     = try(data.external.build_id_check[0].result.exists, "false") == "false"
      error_message = <<-EOT
        BUILD_ID IMMUTABILITY VIOLATION!

        Build ID "${var.build_id}" already exists for environment "${var.environment}".
        Build IDs are immutable and cannot be reused.

        Options:
        1. Use a new build ID (recommended): increment the sequence number
        2. Set allow_build_id_reuse=true to override (NOT recommended for production)

        Existing build record found in: governance-registry branch
        Path: environments/development/latest/build_timings.csv
      EOT
    }
  }
}
```

**Timing**: Precondition evaluated during `terraform plan`
**Failure Mode**: Halt with detailed error message before any AWS API calls

### Configuration Variables

Three new variables added to support the enforcement:

```hcl
# envs/dev/variables.tf

# Enhanced with format validation
variable "build_id" {
  type        = string
  description = "Build ID used to suffix ephemeral resources. Must be unique and immutable."
  default     = ""
  validation {
    condition     = var.cluster_lifecycle == "persistent" || trimspace(var.build_id) != ""
    error_message = "build_id must be set when cluster_lifecycle is ephemeral."
  }
  validation {
    condition     = can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id)) || var.build_id == ""
    error_message = "build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)"
  }
}

# NEW: Override mechanism for exceptional circumstances
variable "allow_build_id_reuse" {
  type        = bool
  description = "Allow reusing an existing build_id (NOT recommended for production)."
  default     = false
}

# NEW: Configurable registry branch
variable "governance_registry_branch" {
  type        = string
  description = "Git branch containing governance registry data (build timings, catalogs, etc.)."
  default     = "governance-registry"
}
```

## How It Works: Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  terraform plan -var="build_id=13-01-26-01"                     │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Variable Validation                                    │
│  ✓ Validates: build_id matches DD-MM-YY-NN regex                │
│  ✗ Fails: "build_id must match format: DD-MM-YY-NN"             │
└───────────────────┬─────────────────────────────────────────────┘
                    │ format valid
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: External Data Source Execution                        │
│  1. Bash script executes: git show origin/governance-registry   │
│  2. Fetches: environments/development/latest/build_timings.csv  │
│  3. Searches: grep -q ",dev,13-01-26-01,"                       │
│  4. Returns: {"exists":"false","build_id":"13-01-26-01"}        │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Precondition Evaluation                               │
│  • Reads: data.external.build_id_check[0].result.exists          │
│  • Condition: "false" == "false" → PASS                          │
│  ✓ Pass: Continue with terraform plan                           │
│  ✗ Fail: IMMUTABILITY VIOLATION error with remediation options  │
└───────────────────┬─────────────────────────────────────────────┘
                    │ all validations passed
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Infrastructure Planning/Provisioning                            │
│  • VPC, Subnets, EKS Cluster, Node Groups, IAM, etc.            │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: Git → Terraform

```
┌──────────────────────────────────────────────────────────────────┐
│  governance-registry branch (remote)                             │
│  └─ environments/development/latest/build_timings.csv            │
│     └─ Contains all historical build_id records                 │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ git show origin/governance-registry:...
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  External Data Source (Bash Script)                              │
│  • Input: BUILD_ID="13-01-26-01", ENV="dev"                      │
│  • Action: Fetch CSV from git object database                   │
│  • Search: grep for pattern ",dev,13-01-26-01,"                 │
│  • Output: JSON {"exists":"false"|"true",...}                   │
└──────────────────────┬───────────────────────────────────────────┘
                       │ stdout → Terraform
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Terraform Data Resource                                         │
│  data.external.build_id_check[0].result = {                      │
│    "exists": "false",                                            │
│    "build_id": "13-01-26-01",                                    │
│    "environment": "dev"                                          │
│  }                                                               │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Lifecycle Precondition                                          │
│  • Evaluates: exists == "false"                                  │
│  • True → Proceed with apply                                     │
│  • False → Halt with immutability violation error                │
└──────────────────────────────────────────────────────────────────┘
```

### Timing: When Checks Execute

| Phase | Layer 1<br/>Format | Layer 2<br/>Registry | Layer 3<br/>Precondition | Infrastructure<br/>Provisioning |
|-------|-------------------|---------------------|-------------------------|--------------------------------|
| `terraform init` | ❌ | ❌ | ❌ | ❌ |
| `terraform validate` | ✅ | ❌ | ❌ | ❌ |
| `terraform plan` | ✅ | ✅ | ✅ | ❌ |
| `terraform apply` | ✅ | ✅ | ✅ | ✅ (if passed) |

**Key Insight**: All validation completes during the plan phase, before any AWS API calls or resource provisioning.

## Changes

### Governance
- **Added**: `docs/adrs/ADR-0153-build-id-immutability-enforcement.md`

### Infrastructure (Terraform)
- **Module**: `envs/dev/main.tf`
  - Added external data source `build_id_check` (lines 25-50)
  - Added null resource `enforce_build_id_immutability` with lifecycle precondition (lines 53-74)
- **Module**: `envs/dev/variables.tf`
  - Enhanced `build_id` variable with format validation regex (lines 50-53)
  - Added `allow_build_id_reuse` variable (lines 56-60)
  - Added `governance_registry_branch` variable (lines 62-66)

## Capabilities Delivered

### Enforcement
- **Format Validation**: Ensures DD-MM-YY-NN pattern compliance
- **Duplicate Prevention**: Queries governance-registry for existing build_id
- **Fast Feedback**: Fails during plan phase (before AWS resource creation)
- **Clear Remediation**: Error messages explain problem and provide solutions

### Flexibility
- **Override Capability**: `allow_build_id_reuse=true` for exceptional cases
- **Configurable Registry**: `governance_registry_branch` variable
- **Fail-Open for Git Issues**: If registry unavailable, doesn't block emergency deployments

### Integration
- **Separation of Concerns**: Operational data in governance-registry, not code repo
- **CI/CD Compatible**: Automated workflows generate unique build_ids
- **Audit Trail**: All build_ids logged in governance-registry branch

## Validation

### Test Scenarios

#### ✅ Test 1: New build_id (should pass)
```bash
$ terraform plan -var="build_id=13-01-26-99"
# Plan succeeds, no build record found in registry
```

#### ❌ Test 2: Existing build_id (should fail)
```bash
$ terraform plan -var="build_id=31-12-25-04"

Error: Resource precondition failed
│ BUILD_ID IMMUTABILITY VIOLATION!
│ Build ID "31-12-25-04" already exists for environment "dev".
```

#### ❌ Test 3: Invalid format (should fail)
```bash
$ terraform plan -var="build_id=2025-01-13-01"

Error: Invalid value for variable
│ build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)
```

#### ✅ Test 4: Override (should pass)
```bash
$ terraform plan -var="build_id=31-12-25-04" -var="allow_build_id_reuse=true"
# Plan succeeds (override active)
```

### Performance Impact
- **Plan Time**: +1-2 seconds (external data source git show execution)
- **Apply Time**: No additional overhead (validation in plan phase)
- **Network**: No network calls (git operates on local object database)

## Impact Assessment

### Positive Consequences
- ✅ **Prevention**: Impossible to accidentally reuse build_id without explicit override
- ✅ **Fast Feedback**: Fails during plan phase, before any AWS API calls
- ✅ **Clear Remediation**: Error messages guide operators to correct actions
- ✅ **Audit Trail**: Governance-registry maintains authoritative log
- ✅ **Separation of Concerns**: Operational data separate from infrastructure code
- ✅ **CI/CD Safe**: Automated workflows generate unique build_ids

### Negative Consequences
- ⚠️ **Git Dependency**: Requires `git fetch` to have run (fails open if unavailable)
- ⚠️ **Execution Overhead**: +1-2 seconds to plan time for bash script execution
- ⚠️ **Branch Coupling**: Requires governance-registry branch to exist

### Mitigation Strategies
1. **Git Fetch**: CI/CD workflows always fetch governance-registry before planning
2. **Fail-Open**: If CSV unavailable, validation passes (emergency deployments not blocked)
3. **Override**: `allow_build_id_reuse=true` available for documented exceptions

## Rollback Plan

If issues arise, rollback is straightforward:

```bash
# Revert the two commits
git revert 974e6c63  # Governance registry refactor
git revert 3aa08ada  # Initial immutability enforcement

# Or delete the resources from main.tf
terraform plan  # Will show removal of null_resource and data source
terraform apply # Removes validation resources
```

**Risk**: Low (validation resources don't provision AWS infrastructure)

## Future Enhancements

### Potential Improvements
1. **Format Evolution**: Consider YYYY-MM-DD-NN for chronological sorting
2. **Multi-Environment**: Extend to staging/prod with environment-specific CSV paths
3. **API Alternative**: Optionally use DynamoDB or Parameter Store as registry backend
4. **Metadata Enrichment**: Store additional build metadata (git commit, user, duration)

### Related Work
- Integrate with CI build timing logs (already appending to governance-registry)
- Extend to other immutable identifiers (ECR tags, AMI IDs)
- Add governance policy workflows to enforce best practices

## References
- **ADR**: [ADR-0153: Build ID Immutability Enforcement](../adrs/ADR-0153-build-id-immutability-enforcement.md)
- **Related ADRs**:
  - [ADR-0040: Lifecycle-Aware State Keys](../adrs/ADR-0040-platform-lifecycle-aware-state-keys.md)
  - [ADR-0042: Branching Strategy](../adrs/ADR-0042-platform-branching-strategy.md)
- **Implementation**:
  - [envs/dev/main.tf](../../envs/dev/main.tf) (lines 20-74)
  - [envs/dev/variables.tf](../../envs/dev/variables.tf) (lines 42-66)
- **Registry**: `origin/governance-registry:environments/development/latest/build_timings.csv`

## Metadata
- **Authored**: 2026-01-13
- **Implemented**: 2026-01-13
- **Commits**:
  - `3aa08ada` - Initial immutability enforcement implementation
  - `974e6c63` - Refactor to use governance-registry branch
- **Maturity**: 2 (Proven in dev environment)
- **Risk**: Low (validation only, no infrastructure changes)
- **Cost Impact**: None (git-based, no AWS resources)
- **Performance**: +1-2 seconds to terraform plan time
