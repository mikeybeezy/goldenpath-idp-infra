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
relates_to: [ADR-0040-platform-lifecycle-aware-state-keys, ADR-0042-platform-branching-strategy]
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

## Proposer
Platform Team

## Status
Accepted

## Context

The platform supports both persistent and ephemeral cluster lifecycles. Ephemeral clusters use a `build_id` (format: `DD-MM-YY-NN`) to uniquely suffix resources and state keys, enabling parallel builds and teardowns without conflicts.

### Problem Statement

Without enforcement, operators could accidentally reuse a `build_id`, causing:

1. **State Corruption**: Terraform state pointing to destroyed resources
2. **Resource Conflicts**: AWS resource name collisions during apply
3. **Audit Trail Loss**: Build timing logs overwritten or conflated
4. **Debugging Confusion**: Multiple builds with identical identifiers in logs and metrics

The governance-registry branch maintains `environments/development/latest/build_timings.csv` as the authoritative log of all builds. This CSV is the source of truth for determining if a build_id has been used.

### Design Constraints

- Must fail fast before any infrastructure provisioning
- Must reference governance-registry branch (not local code repo)
- Must provide clear error messages with remediation steps
- Must allow override for exceptional circumstances (testing, recovery)
- Must validate format consistency (`DD-MM-YY-NN`)

## Decision

We implement **perpetual build_id immutability** using a three-layer enforcement mechanism:

### Layer 1: Format Validation
Terraform variable validation ensures build_id matches the required format:
```hcl
validation {
  condition     = can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id)) || var.build_id == ""
  error_message = "build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)"
}
```

### Layer 2: Registry Duplicate Check
External data source queries the governance-registry branch via `git show`:
```hcl
data "external" "build_id_check" {
  count   = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0
  program = ["bash", "-c", <<-EOT
    # Fetch CSV from governance-registry branch
    CSV_CONTENT=$(git show "origin/${var.governance_registry_branch}:environments/development/latest/build_timings.csv")

    # Check for duplicate: ,$ENV,$BUILD_ID,
    if echo "$CSV_CONTENT" | grep -q ",$ENV,$BUILD_ID," ; then
      echo '{"exists":"true"}'
    else
      echo '{"exists":"false"}'
    fi
  EOT
  ]
}
```

### Layer 3: Lifecycle Precondition
Null resource with precondition fails terraform plan/apply if duplicate detected:
```hcl
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

### Override Mechanism
Variable `allow_build_id_reuse` (default: `false`) provides escape hatch:
```hcl
variable "allow_build_id_reuse" {
  type        = bool
  description = "Allow reusing an existing build_id (NOT recommended for production)."
  default     = false
}
```

### Configuration
Variable `governance_registry_branch` makes branch name configurable:
```hcl
variable "governance_registry_branch" {
  type        = string
  description = "Git branch containing governance registry data."
  default     = "governance-registry"
}
```

## How It Works: Detailed Mechanics

### Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  terraform plan/apply                                            │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Variable Validation                                    │
│  ✓ Check: build_id matches DD-MM-YY-NN format                   │
│  ✗ Fail: Invalid format → Error before plan                     │
└───────────────────┬─────────────────────────────────────────────┘
                    │ format valid
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: External Data Source Execution                        │
│  1. Execute bash script during terraform plan phase             │
│  2. Run: git show origin/governance-registry:...csv             │
│  3. Grep for pattern: ,$ENV,$BUILD_ID,                          │
│  4. Return JSON: {"exists": "true"|"false"}                     │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Lifecycle Precondition Evaluation                     │
│  Condition: data.external.build_id_check[0].result.exists == "false"│
│  ✓ Pass (exists=false): Continue with terraform plan/apply      │
│  ✗ Fail (exists=true): Halt with IMMUTABILITY VIOLATION error   │
└───────────────────┬─────────────────────────────────────────────┘
                    │ validation passed
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Infrastructure Provisioning                                     │
│  • VPC, Subnets, Route Tables                                   │
│  • EKS Cluster & Node Groups                                    │
│  • IAM Roles & Policies                                         │
│  • VPC Endpoints                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: Git to Terraform

```
┌──────────────────────────────────────────────────────────────────┐
│  governance-registry branch (remote)                             │
│  └─ environments/development/latest/build_timings.csv            │
│     start_time,end_time,phase,env,build_id,duration,exit_code   │
│     ...                                                          │
│     2026-01-01T04:01:57Z,...,teardown,dev,31-12-25-04,700,0     │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ git show origin/governance-registry:...
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  External Data Source (Bash Script)                              │
│  • Receives: BUILD_ID="13-01-26-01", ENV="dev"                   │
│  • Fetches: CSV content from git object database                │
│  • Searches: grep -q ",dev,13-01-26-01,"                        │
│  • Returns: {"exists":"false","build_id":"13-01-26-01",...}     │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       │ JSON output via stdout
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
                       │ precondition evaluation
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Null Resource Lifecycle Precondition                            │
│  • Reads: data.external.build_id_check[0].result.exists          │
│  • Evaluates: "false" == "false" → PASS                          │
│  • Action: Allow terraform to continue                          │
└──────────────────────────────────────────────────────────────────┘
```

### Timing: When Checks Execute

| Phase | Layer 1 | Layer 2 | Layer 3 | Infrastructure |
|-------|---------|---------|---------|----------------|
| `terraform init` | ❌ | ❌ | ❌ | ❌ |
| `terraform validate` | ✅ | ❌ | ❌ | ❌ |
| `terraform plan` | ✅ | ✅ | ✅ | ❌ |
| `terraform apply` | ✅ | ✅ | ✅ | ✅ (if passed) |

**Key Insight**: All validation happens during the plan phase, before any AWS API calls or resource creation.

### Error Scenarios

#### Scenario 1: Duplicate build_id Detected
```bash
$ terraform plan -var="build_id=31-12-25-04"

Error: Resource precondition failed
│
│   on main.tf line 57, in resource "null_resource" "enforce_build_id_immutability":
│   57:       condition     = try(data.external.build_id_check[0].result.exists, "false") == "false"
│     ├────────────────
│     │ data.external.build_id_check[0].result.exists is "true"
│
│ BUILD_ID IMMUTABILITY VIOLATION!
│
│ Build ID "31-12-25-04" already exists for environment "dev".
│ Build IDs are immutable and cannot be reused.
│
│ Options:
│ 1. Use a new build ID (recommended): increment the sequence number
│ 2. Set allow_build_id_reuse=true to override (NOT recommended for production)
│
│ Existing build record found in: governance-registry branch
│ Path: environments/development/latest/build_timings.csv
```

#### Scenario 2: Invalid Format
```bash
$ terraform plan -var="build_id=2025-01-13-01"

Error: Invalid value for variable
│
│   on variables.tf line 51:
│   51: variable "build_id" {
│     ├────────────────
│     │ var.build_id is "2025-01-13-01"
│
│ build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)
```

#### Scenario 3: Registry Not Fetched
```bash
# If user hasn't run git fetch recently
$ terraform plan -var="build_id=13-01-26-99"

# External data source returns:
{"exists":"false","error":"Registry CSV not found or git fetch needed"}

# Terraform proceeds (fail-open behavior for git connectivity issues)
# This is intentional: prevents broken git from blocking emergency deployments
```

### Override Workflow (Testing/Recovery Only)

```bash
# Step 1: Set override variable
$ terraform plan -var="build_id=31-12-25-04" -var="allow_build_id_reuse=true"

# Validation is bypassed (count = 0, null_resource not created)
# Plan succeeds

# Step 2: Apply with override
$ terraform apply -var="build_id=31-12-25-04" -var="allow_build_id_reuse=true"

# WARNING: This should ONLY be used for:
# - Local testing/development
# - Disaster recovery scenarios
# - Documented exceptions with team approval
```

### Integration with Build Automation

CI/CD workflows automatically increment build_id and append to registry:

```yaml
# Example: .github/workflows/ci-bootstrap.yml
- name: Generate Build ID
  run: |
    # Format: DD-MM-YY-NN (day-month-year-sequence)
    DATE_PREFIX=$(date -u +"%d-%m-%y")

    # Query latest sequence number from registry
    LAST_SEQ=$(git show origin/governance-registry:environments/development/latest/build_timings.csv | \
      grep ",dev,$DATE_PREFIX-" | \
      tail -1 | \
      awk -F'-' '{print $4}' | \
      awk -F',' '{print $1}')

    NEXT_SEQ=$(printf "%02d" $((10#${LAST_SEQ:-0} + 1)))
    BUILD_ID="${DATE_PREFIX}-${NEXT_SEQ}"

    echo "BUILD_ID=$BUILD_ID" >> $GITHUB_ENV

- name: Terraform Apply
  run: |
    terraform apply -var="build_id=$BUILD_ID" -auto-approve

- name: Record Build Timing
  run: |
    # Append to governance-registry branch
    echo "$START_TIME,$END_TIME,bootstrap,dev,$BUILD_ID,$DURATION,0" >> build_timings.csv
    git checkout governance-registry
    cp build_timings.csv environments/development/latest/
    git commit -m "govreg: development @ $(git rev-parse HEAD)"
    git push origin governance-registry
```

## Consequences

### Positive
- **Prevention**: Impossible to accidentally reuse build_id without explicit override
- **Fast Feedback**: Fails during plan phase, before any AWS resources created
- **Clear Remediation**: Error messages explain problem and provide solutions
- **Audit Trail**: Every build_id logged in governance-registry
- **Separation of Concerns**: Operational data (CSV) separate from infrastructure code
- **CI/CD Safe**: Automated workflows generate unique build_ids

### Negative
- **Git Dependency**: Requires git fetch to have run (fails open if unavailable)
- **External Dependency**: Bash script execution adds ~1-2 seconds to plan time
- **Branch Coupling**: Requires governance-registry branch to exist
- **Override Temptation**: allow_build_id_reuse could be misused if not governed

### Neutral
- **Plan Phase Only**: Validation doesn't run during apply if plan is saved
- **Local Testing**: Developers must fetch registry branch before planning
- **Format Rigidity**: DD-MM-YY-NN format is not internationally sortable (use YYYY-MM-DD-NN for chronological sorting in future)

## Alternatives Considered

### 1. S3 Backend State Locking
**Rejected**: State lock only prevents concurrent writes, doesn't prevent sequential reuse of build_id across days.

### 2. DynamoDB Registry Table
**Rejected**: Adds AWS dependency and cost. Git-based registry is zero-cost and already used for other catalogs.

### 3. Local File Check (docs/build-timings.csv)
**Rejected**: Doesn't enforce immutability if operator uses stale code branch. Registry branch is source of truth.

### 4. AWS Parameter Store Registry
**Rejected**: Couples validation to AWS account. Git-based approach works offline and across accounts.

## Implementation

### Files Modified
- `envs/dev/main.tf` (lines 20-74): External data source + null_resource precondition
- `envs/dev/variables.tf` (lines 42-66): build_id validation + new variables

### Variables Added
| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `build_id` | string | "" | Unique ephemeral cluster identifier (DD-MM-YY-NN) |
| `allow_build_id_reuse` | bool | false | Override to allow duplicate build_id |
| `governance_registry_branch` | string | "governance-registry" | Git branch containing build_timings.csv |

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

## References
- [ADR-0040: Lifecycle-Aware State Keys](ADR-0040-platform-lifecycle-aware-state-keys.md)
- [ADR-0042: Branching Strategy](ADR-0042-platform-branching-strategy.md)
- Governance Registry: `origin/governance-registry:environments/development/latest/build_timings.csv`
- Implementation: `envs/dev/main.tf`, `envs/dev/variables.tf`

## Metadata
- **Authored**: 2026-01-13
- **Implemented**: 2026-01-13
- **Maturity**: 2 (Proven in dev, pending staging validation)
- **Risk**: Low (fail-safe validation, no infrastructure changes)
- **Cost Impact**: None (git-based, no AWS resources)
