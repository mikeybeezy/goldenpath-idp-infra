---
id: ADR-0153-build-id-immutability-enforcement
title: 'ADR-0153: Build ID Immutability Enforcement via Governance Registry'
type: adr
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
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ADR-0042-platform-branching-strategy
supersedes: []
superseded_by: []
tags: [governance, ephemeral, build-id, immutability, terraform]
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 8.0
supported_until: '2028-01-01'
---

# ADR-0153: Build ID Immutability Enforcement via Governance Registry

- **Status:** Accepted
- **Date:** 2026-01-13
- **Owners:** Platform Team
- **Domain:** Platform Core
- **Decision type:** Governance | Operations | Safety

## Context

The platform supports ephemeral cluster lifecycles using `build_id` (format: `DD-MM-YY-NN`) to uniquely suffix resources and Terraform state keys. This enables parallel builds and teardowns without conflicts.

### Problem

Without enforcement, operators can accidentally reuse a `build_id`, causing:

1. **State Corruption**: Terraform state pointing to destroyed resources
2. **Resource Conflicts**: AWS resource name collisions during apply
3. **Audit Trail Loss**: Build timing logs overwritten or conflated
4. **Debugging Confusion**: Multiple builds with identical identifiers

The `governance-registry` branch maintains `environments/development/latest/build_timings.csv` as the authoritative log of all builds.

### Constraints

- Must fail fast before any infrastructure provisioning
- Must reference governance-registry branch (not local code repo)
- Must provide clear error messages with remediation steps
- Must allow override for exceptional circumstances
- Must validate format consistency

## Decision

Implement **three-layer build_id immutability enforcement** using Terraform validation, external data sources, and lifecycle preconditions.

### Architecture

#### Layer 1: Format Validation

- Terraform variable validation ensures `DD-MM-YY-NN` format compliance
- Executes during `terraform validate` and `terraform plan`

#### Layer 2: Registry Duplicate Check

- External data source queries governance-registry via `git show`
- Fetches CSV and searches for existing `,$ENV,$BUILD_ID,` pattern
- Executes during `terraform plan`

#### Layer 3: Lifecycle Precondition

- Null resource with precondition fails terraform if duplicate detected
- Provides clear error message with remediation options
- Executes during `terraform plan` before AWS API calls

### Configuration

Three variables support the enforcement:

```hcl
variable "build_id" {
  type        = string
  description = "Build ID for ephemeral resources. Must be unique and immutable."
  default     = ""
  validation {
    condition     = can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id)) || var.build_id == ""
    error_message = "build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)"
  }
}

variable "allow_build_id_reuse" {
  type        = bool
  description = "Allow reusing an existing build_id (NOT recommended for production)."
  default     = false
}

variable "governance_registry_branch" {
  type        = string
  description = "Git branch containing governance registry data."
  default     = "governance-registry"
}
```

## Scope

- **Applies to**: Ephemeral cluster builds in dev environment (when `cluster_lifecycle="ephemeral"`)
- **Out of scope**: Persistent clusters, non-EKS resources

## Consequences

### Positive

- Impossible to accidentally reuse build_id without explicit override
- Fast feedback during plan phase (before AWS resource creation)
- Clear remediation guidance in error messages
- Authoritative registry in governance-registry branch
- Separation of operational data from infrastructure code
- CI/CD workflows automatically generate unique build_ids

### Tradeoffs / Risks

- Git dependency: Requires `git fetch` to have run (fails open if unavailable)
- Performance: +1-2 seconds to terraform plan time for bash script execution
- Branch coupling: Requires governance-registry branch to exist
- Override temptation: `allow_build_id_reuse` could be misused if not governed

### Operational impact

- Operators must use fresh build_ids for each ephemeral deployment
- CI/CD workflows query registry and auto-increment sequence numbers
- Override requires explicit variable flag (logged for compliance)
- Git fetch should run before terraform plan in CI/CD

## Alternatives considered

### S3 Backend State Locking

**Rejected**: State lock prevents concurrent writes, not sequential reuse of build_id across days.

### DynamoDB Registry Table

**Rejected**: Adds AWS dependency and cost. Git-based registry is zero-cost and already used for other catalogs.

### Local File Check (docs/build-timings.csv)

**Rejected**: Doesn't enforce immutability if operator uses stale code branch. Registry branch is source of truth.

### AWS Parameter Store Registry

**Rejected**: Couples validation to AWS account. Git-based approach works offline and across accounts.

## Implementation

### Files Modified
- `envs/dev/main.tf` (lines 20-74): External data source + null_resource precondition
- `envs/dev/variables.tf` (lines 42-66): build_id validation + new variables

### Testing
```bash
# Test 1: New build_id (should pass)
terraform plan -var="build_id=13-01-26-99"

# Test 2: Existing build_id (should fail)
terraform plan -var="build_id=31-12-25-04"

# Test 3: Invalid format (should fail)
terraform plan -var="build_id=2025-01-13-01"

# Test 4: Override (should pass)
terraform plan -var="build_id=31-12-25-04" -var="allow_build_id_reuse=true"
```

## Follow-ups

- Extend to staging/prod environments with environment-specific CSV paths
- Consider YYYY-MM-DD-NN format for chronological sorting
- Add governance policy workflows to audit `allow_build_id_reuse` usage
- Integrate with automated build timing log appends

## References

- **How It Works**: [Build ID Immutability Enforcement](../how-it-works/BUILD_ID_IMMUTABILITY_ENFORCEMENT.md)
- **Changelog**: [CL-0125: Build ID Immutability Enforcement](../changelog/entries/CL-0125-build-id-immutability-enforcement.md)
- **Related ADRs**:
  - [ADR-0040: Lifecycle-Aware State Keys](ADR-0040-platform-lifecycle-aware-state-keys.md)
  - [ADR-0042: Branching Strategy](ADR-0042-platform-branching-strategy.md)
- **Implementation**:
  - [envs/dev/main.tf](../../envs/dev/main.tf) (lines 20-74)
  - [envs/dev/variables.tf](../../envs/dev/variables.tf) (lines 42-66)
- **Registry**: `origin/governance-registry:environments/development/latest/build_timings.csv`
