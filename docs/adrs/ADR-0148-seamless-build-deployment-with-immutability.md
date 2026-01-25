---
id: ADR-0148-seamless-build-deployment-with-immutability
title: 'ADR-0148: Seamless Build Deployment with Build ID Immutability'
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0007-platform-environment-model
  - ADR-0063-platform-terraform-helm-bootstrap
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0153
  - ADR-0154
  - ADR-0155-ci-governance-registry-fetch
  - ADR-0156-platform-ci-build-timing-capture
  - BRIDGE_ANALYSIS
  - BUG_FIXES_SUMMARY
  - CL-0121-seamless-build-deployment
  - CL-0125
  - CL-0126-ci-governance-registry-fetch
  - EC-0001-knative-integration
  - EC-0006-competitor-analysis-tap
  - EC-0007-kpack-buildpacks-integration
  - SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

## ADR-0148: Seamless Build Deployment with Build ID Immutability

**Status**: Accepted
**Date**: 2026-01-13
**Supersedes**: [ADR-0153](./ADR-0153-build-id-immutability-enforcement.md) (from eks-single-build-refactor branch, not merged)

## Context

The platform requires a deployment process that:

1. **Enforces build_id immutability** to prevent accidental reuse causing state corruption
2. **Provides seamless UX** - single command deploys entire platform
3. **Maintains two-phase separation** - infrastructure (Terraform) and platform (shell scripts)
4. **Tracks all builds** in governance-registry for audit and analytics
5. **Avoids circular dependencies** between Terraform resources

### Previous Attempt: ADR-0153 (Not Merged)

A previous refactor (eks-single-build-refactor branch) attempted to consolidate everything into a single Terraform apply using a `kubernetes_addons` module. This approach:

- Introduced circular dependency issues (module ↔ service accounts)
- Mixed infrastructure and platform concerns in one apply
- Created complex dependency chains prone to race conditions
- Introduced valuable build_id immutability enforcement
- Documented governance registry pattern

**Decision**: Keep the proven two-phase pattern from development branch, but add build_id immutability enforcement.

## Decision

Implement **seamless two-phase deployment with build_id immutability** by:

1. Maintaining the original two-phase pattern (infrastructure → bootstrap)
2. Adding three-layer build_id validation before Terraform apply
3. Creating unified `make deploy` command that orchestrates both phases
4. Recording all builds to governance-registry branch for audit trail
5. Providing single-command UX while preserving phase separation

## Architecture

### Two-Phase Deployment Flow

```text
make deploy ENV=dev BUILD_ID=13-01-26-03
    ↓
┌─────────────────────────────────────────┐
│ Makefile Orchestration Layer           │
│ (User sees one seamless transaction)   │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    ↓                 ↓
┌───────────┐   ┌──────────────┐
│ Phase 1   │   │  Phase 2     │
│ Terraform │──→│  Bootstrap   │
│ (Infra)   │   │  (Platform)  │
└───────────┘   └──────────────┘
```

#### Phase 1: Infrastructure (Terraform)

**Scope**: AWS resources only

- VPC, Subnets, Security Groups
- EKS Cluster
- IAM Roles (cluster, nodes, IRSA)
- Service Accounts (with IRSA annotations)

**Command**: `make _phase1-infrastructure`

**Terraform Variables**:

- `enable_k8s_resources=true` (creates service accounts)
- `apply_kubernetes_addons=false` (prevents Helm releases)

**Key characteristic**: No Helm releases, no ArgoCD Applications (controlled by `apply_kubernetes_addons` variable)

#### Phase 2: Platform Bootstrap (Shell Script)

**Scope**: Kubernetes platform controllers and applications

- Create namespaces (kubectl)
- Deploy ArgoCD (Helm)
- Deploy AWS Load Balancer Controller (Helm)
- Deploy Metrics Server (Helm)
- Deploy ArgoCD Applications (kubectl apply)
- Wait for sync and verify

**Command**: `make _phase2-bootstrap`

**Key characteristic**: Uses bash script with clear stage boundaries and retry logic

### Build ID Immutability (Three Layers)

#### Layer 1: Format Validation (terraform validate)

```hcl
variable "build_id" {
  validation {
    condition     = can(regex("^[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$", var.build_id)) || var.build_id == ""
    error_message = "build_id must match format: DD-MM-YY-NN"
  }
}
```

#### Layer 2: Registry Duplicate Check (terraform plan)

```hcl
data "external" "build_id_check" {
  program = ["bash", "-c", <<-EOT
    BUILD_ID="${var.build_id}"
    ENV="${var.environment}"
    CSV_CONTENT=$(git show "origin/governance-registry:environments/development/latest/build_timings.csv")

    if echo "$CSV_CONTENT" | grep -q ",$ENV,$BUILD_ID,"; then
      echo '{"exists":"true"}'
    else
      echo '{"exists":"false"}'
    fi
  EOT
  ]
}
```

#### Layer 3: Lifecycle Precondition (terraform plan)

```hcl
resource "null_resource" "enforce_build_id_immutability" {
  lifecycle {
    precondition {
      condition     = !var.allow_build_id_reuse ? data.external.build_id_check[0].result.exists == "false" : true
      error_message = "Build ID already exists. Use new build_id or set allow_build_id_reuse=true"
    }
  }
}
```

### Governance Registry Integration

**Branch**: `governance-registry`
**Location**: `environments/development/latest/build_timings.csv`
**Schema**: 12 columns including inventory tracking

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
```

**Recording happens**:

- After Phase 1 completes (terraform-apply phase)
- After Phase 2 completes (bootstrap phase)
- After teardown (teardown phase)

## Consequences

### Positive

1. **Seamless UX**: Users run one command (`make deploy`), platform handles orchestration
2. **No Circular Dependencies**: Infrastructure and platform remain separate
3. **Better Error Messages**: Shell scripts provide clear kubectl/helm errors
4. **Retry Logic**: Can retry individual phases without full rebuild
5. **Build ID Protection**: Three-layer enforcement prevents accidental reuse
6. **Full Audit Trail**: Every build recorded with inventory data
7. **Proven Pattern**: Uses battle-tested development branch architecture
8. **Analytics Ready**: CSV format enables capacity planning and FinOps queries

### Tradeoffs

1. **Two Commands**: Internally runs two phases (but transparent to user)
2. **Shell Script Dependency**: Requires bash, kubectl, helm (already required)
3. **Git Fetch Required**: Must fetch governance-registry branch before validate
4. **Override Available**: Emergency escape hatch with `allow_build_id_reuse` (logged)

### Operational Impact

**Before**:

```bash
# Manual two-phase with no protection
terraform apply
bash bootstrap-v3.sh

# Risk: Could accidentally reuse build_id
# Risk: Forget to run bootstrap
# Risk: No audit trail
```

**After**:

```bash
# Single command with protection
make deploy ENV=dev BUILD_ID=13-01-26-03

# Protection: Build ID validated against registry
# Protection: Phases run in sequence automatically
# Protection: All builds recorded for audit
```

## Alternatives Considered

### Consolidated Terraform Apply (Rejected)

**Approach**: Put everything in one `terraform apply` with `kubernetes_addons` module.

**Rejected because**:

- Circular dependency issues (module ↔ service accounts)
- Poor error messages for Helm/kubectl failures
- All-or-nothing deployment (can't retry bootstrap without infra rebuild)
- Complex dependency chains prone to race conditions

### Separate Terraform Workspaces (Rejected)

**Approach**: Two separate Terraform configurations (infra/, platform/).

**Rejected because**:

- Adds complexity of managing two state files
- Requires passing outputs between workspaces
- Makes single-command UX harder to achieve

### Pure Shell Script (Rejected)

**Approach**: Do everything with kubectl/helm, no Terraform.

**Rejected because**:

- Lose Terraform state management for AWS resources
- Lose Terraform plan preview
- Lose declarative infrastructure-as-code benefits

## Implementation

### Files Modified

#### Core Infrastructure

- `envs/dev/main.tf`:
  - Add build_id validation (data.external + null_resource)
  - Update `kubernetes_addons` module condition to include `apply_kubernetes_addons` variable
- `envs/dev/variables.tf`:
  - Add build_id, allow_build_id_reuse, governance_registry_branch variables
  - Add `apply_kubernetes_addons` variable to control Helm release deployment phase

#### Makefile

- Add `deploy` target (user-facing unified command)
- Add `_phase1-infrastructure` target (internal: terraform apply with enable_k8s_resources=true, apply_kubernetes_addons=false)
- Add `_phase2-bootstrap` target (internal: run bootstrap script with ENABLE_TF_K8S_RESOURCES=false)
- Add `_phase3-verify` target (internal: kubectl verification)

#### Scripts

- `scripts/record-build-timing.sh`: Record build to governance-registry CSV

#### Documentation

- `docs/adrs/ADR-0148-seamless-build-deployment-with-immutability.md` (this file)
- `docs/changelog/entries/CL-0121-seamless-build-deployment.md`
- `docs/85-how-it-works/ci-terraform/SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT.md` (detailed mechanics)

### Deployment Commands

**Primary (User-facing)**:

```bash
make deploy ENV=dev BUILD_ID=13-01-26-03
```

**Internal (Phase separation, can be run independently for debugging)**:

```bash
make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-03
make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-03
make _phase3-verify ENV=dev
```

**Override (Emergency only)**:

```bash
make deploy ENV=dev BUILD_ID=13-01-26-03 ALLOW_REUSE_BUILD_ID=true
```

### Verification

After deployment:

```bash
# Check governance registry
git show origin/governance-registry:environments/development/latest/build_timings.csv | tail -1

# Check infrastructure
kubectl get nodes
aws eks describe-cluster --name goldenpath-dev-eks-13-01-26-03

# Check platform
kubectl -n argocd get applications
kubectl -n kube-system get pods
```

## Related

- Supersedes: [ADR-0153](./ADR-0153-build-id-immutability-enforcement.md) (eks-single-build-refactor, not merged)
- Related: [ADR-0007](./ADR-0007-platform-environment-model.md) (environment model)
- Related: [ADR-0063](./ADR-0063-platform-terraform-helm-bootstrap.md) (bootstrap pattern)
- Changelog: [CL-0121](../changelog/entries/CL-0121-seamless-build-deployment.md)

## References

- Bootstrap script: `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh`
- Makefile: `Makefile` (lines 100-200, deploy target)
- Governance registry: `governance-registry` branch
