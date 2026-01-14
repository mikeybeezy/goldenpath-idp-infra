---
id: ADR-0149-simplified-resource-lifecycle-separation
title: 'ADR-0149: Simplified Resource Lifecycle Separation for Ephemeral Builds'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0007-platform-environment-model
  - ADR-0032-platform-eks-access-model
  - ADR-0060-platform-ephemeral-update-workflow
  - ADR-0143-secret-request-contract
  - ADR-0148-seamless-build-deployment-with-immutability
supersedes:
  - ADR-0148-seamless-build-deployment-with-immutability
superseded_by: []
tags:
  - ephemeral-clusters
  - resource-lifecycle
  - developer-experience
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: high
  potential_savings_hours: 20.0
supported_until: 2028-01-14
version: '1.0'
breaking_change: false
---

# ADR-0149: Simplified Resource Lifecycle Separation for Ephemeral Builds

- **Status:** Active
- **Date:** 2026-01-13 (Updated)
- **Owners:** Platform Team
- **Domain:** Platform Core
- **Decision type:** Architecture | Operations | Developer Experience
- **Supersedes:** [ADR-0148](./ADR-0148-seamless-build-deployment-with-immutability.md)

---

## Context

ADR-0148 successfully implemented seamless build deployment with build_id immutability. However, during implementation testing, we discovered **resource lifecycle scope mismatches** that caused collision errors:

### The Core Problem

Ephemeral cluster builds were failing because terraform tried to manage resources with **three different lifecycle scopes** in a single workspace:

| Resource Type | Actual Scope | Build Behavior | Problem |
|--------------|--------------|----------------|---------|
| **EKS Cluster** | Cluster-scoped | Creates with build_id suffix | ✅ Correct |
| **VPC/Subnets** | Cluster-scoped | Creates with build_id suffix | ✅ Correct |
| **EKS Access Entry** | User-scoped | Tried to recreate each build | ❌ Collision - user already has entry |
| **ECR Repositories** | Account-scoped | Tried to recreate each build | ❌ Collision - repos persist |
| **Secrets Manager** | Platform-scoped | Tried to recreate each build | ❌ Collision - managed via Backstage |

### Collision Errors Encountered

```
Error: ResourceInUseException: The specified access entry resource
is already in use on this cluster.
arn:aws:iam::593517239005:user/michaelnouriel

Error: RepositoryAlreadyExistsException: The repository with name
'new-wp-reg-2' already exists in the registry with id '593517239005'

Error: You can't create this secret because a secret with this name
is already scheduled for deletion.
```

### Initial Solution Attempted (Rejected)

We initially added conditional variables to make resources optional:

```hcl
# REJECTED APPROACH
variable "create_eks_access_entry" {
  type    = bool
  default = false
}

resource "aws_eks_access_entry" "terraform_admin" {
  count = var.create_eks_access_entry ? 1 : 0  # Manual toggle
  # ...
}
```

**Why This Was Rejected:**

1. **Cognitive Load**: Developers had to decide "Do I need create_eks_access_entry=true?"
2. **Silent Failure**: If developer forgot to set it, cluster worked but they had no kubectl access
3. **Complex Code**: Added conditionals, array indexing, and depends_on complications
4. **Poor Developer Experience**: Violated "make it simple to do the right thing" principle

The boolean toggle **technically solved the collision** but **created worse problems** for developer experience.

---

## Decision

We will **separate resources by lifecycle scope** and **keep the developer experience simple**:

### 1. Remove Account-Scoped Resources from Cluster Terraform

**ECR Repositories** and **Secrets Manager** are **commented out** in `envs/dev/terraform.tfvars`:

```hcl
# Registry Catalog
# NOTE: ECR repositories are account-scoped and persist across ephemeral builds.
# They should be managed separately, not recreated per cluster.
ecr_repositories = {
  # All repositories commented out
}

# Secret Catalog
# NOTE: Secrets Manager is a platform service managed through Backstage SecretRequest workflow.
# Secrets are environment-scoped, NOT cluster-scoped.
# DO NOT manage secrets through EKS terraform - use the SecretRequest workflow instead.
# See: docs/adrs/ADR-0143-secret-request-contract.md
app_secrets = {
  # All secrets commented out
}
```

**Rationale:**
- ECR repos are account-level resources shared across all clusters
- Secrets Manager is a platform service managed via Backstage (ADR-0143)
- Neither should be recreated for each ephemeral cluster build

### 2. Keep Access Entry Simple (No Conditional Logic)

**EKS Access Entry** remains **unconditional** - always attempts to create:

```hcl
# SIMPLE APPROACH (Chosen)
resource "aws_eks_access_entry" "terraform_admin" {
  cluster_name  = module.eks[0].cluster_name
  principal_arn = data.aws_caller_identity.current.arn
  type          = "STANDARD"
  # No count, no conditionals
}
```

**Why This is Better:**

1. **Simple Developer Experience**: Just run `make deploy ENV=dev BUILD_ID=XX-XX-XX-XX`
2. **Explicit Errors**: If access entry exists, error is loud and informative
3. **Safe Failure**: Error message tells you "already exists" but cluster still works
4. **No Hidden State**: Developer doesn't need to remember if they created it before
5. **No Cognitive Load**: No new variables to learn or flags to set

**Handling the Collision Error:**

When developer sees:
```
Error: ResourceInUseException: access entry already in use
```

**This means:**
- ✅ You already have kubectl access from a previous build
- ✅ The cluster was created successfully
- ✅ Everything works normally
- ℹ️  This is informative, not a blocker

**The error is acceptable because:**
- It's explicit (not silent)
- It's safe (cluster works, access exists)
- It's rare (only happens on second+ build)
- It's self-documenting (tells you what's already there)

---

## Architecture

### Resource Lifecycle Scopes

```
┌─────────────────────────────────────────────────────────────┐
│ AWS Account: 593517239005                                    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Account-Scoped Resources (Created Once)                │ │
│  │ - ECR Repositories (new-wp-reg-2, test-app-dev, etc.) │ │
│  │ - Base IAM Policies                                    │ │
│  │                                                         │ │
│  │ Future: Separate terraform workspace                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Environment-Scoped Resources (dev, staging, prod)      │ │
│  │                                                         │ │
│  │  Platform Services:                                    │ │
│  │  - Secrets Manager (via Backstage SecretRequest)       │ │
│  │  - User Access Entries (per-user, not per-cluster)    │ │
│  │                                                         │ │
│  │  Future: Separate terraform workspace                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Cluster-Scoped Resources (ephemeral builds)            │ │
│  │                                                         │ │
│  │  Build ID: 13-01-26-99                                 │ │
│  │  - VPC (goldenpath-dev-vpc-13-01-26-99)               │ │
│  │  - EKS Cluster (goldenpath-dev-eks-13-01-26-99)       │ │
│  │  - Node Groups                                         │ │
│  │  - Service Accounts (IRSA)                            │ │
│  │  - IAM Roles (cluster-specific)                       │ │
│  │                                                         │ │
│  │  Current: envs/dev/main.tf                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Simplified Deployment Flow

```bash
$ make deploy ENV=dev BUILD_ID=13-01-26-99

Phase 1: Infrastructure (Terraform)
  ✅ Creates: VPC, EKS, Node Groups, Service Accounts
  ⚠️  Tries: Access entry (may error if exists - safe)
  ❌ Skips: ECR repos (commented out)
  ❌ Skips: Secrets (commented out)

Phase 2: Platform Bootstrap (Shell Script)
  ✅ Validates: Service accounts exist
  ✅ Installs: ArgoCD, LB Controller, etc.

Phase 3: Verification
  ✅ Checks: All systems operational
```

---

## Consequences

### Positive

1. **Simple Developer Experience**
   - Single command: `make deploy ENV=dev BUILD_ID=XX-XX-XX-XX`
   - No conditional variables to set
   - No silent failures
   - Errors are explicit and informative

2. **Clear Resource Boundaries**
   - Account-scoped: Commented out (future: separate workspace)
   - Environment-scoped: Access entries (acceptable collision error)
   - Cluster-scoped: VPC, EKS, service accounts

3. **Maintainable Code**
   - No complex conditionals
   - No array indexing
   - No hidden state
   - Straightforward terraform

4. **Self-Documenting**
   - Collision errors tell you "resource already exists"
   - Comments in terraform.tfvars explain why resources are commented out
   - References to relevant ADRs (ADR-0143 for secrets)

### Tradeoffs

1. **Access Entry Collision Error**
   - **Impact:** Error message in logs on second+ build
   - **Mitigation:** Error is safe and self-explanatory
   - **Future:** Move to separate workspace when tightening security

2. **ECR/Secrets Not in Terraform**
   - **Impact:** Must manage separately
   - **Mitigation:** ECR is account-level (created once), Secrets via Backstage (ADR-0143)
   - **Benefit:** Respects architectural boundaries

3. **Manual Cleanup**
   - **Impact:** Commented-out resources still exist in AWS
   - **Mitigation:** Document cleanup procedures
   - **Future:** Lifecycle policies, separate workspaces

### Operational Impact

**For Developers:**
- Simple: Just run `make deploy ENV=dev BUILD_ID=XX-XX-XX-XX`
- Clear errors if collision (but safe to continue)
- No new concepts to learn

**For Platform Team:**
- ECR repos: Manage separately (create once per account)
- Secrets: Managed via Backstage SecretRequest workflow (ADR-0143)
- Access entries: Can move to separate workspace later

---

## Alternatives Considered

### Alternative A: Conditional Variables (Rejected)

**Approach:**
```hcl
variable "create_eks_access_entry" {
  type    = bool
  default = false
}

resource "aws_eks_access_entry" "terraform_admin" {
  count = var.create_eks_access_entry ? 1 : 0
}
```

**Pros:**
- No collision errors

**Cons:**
- Developer must decide: "Do I set this to true or false?"
- Silent failure if developer forgets (cluster works, no kubectl access)
- Complex code with conditionals and array indexing
- Poor developer experience

**Decision:** Rejected - complexity outweighs benefit

### Alternative B: Auto-Detection (Too Complex)

**Approach:**
```hcl
data "aws_eks_access_entry" "existing" {
  # Check if exists
}

locals {
  should_create = data.aws_eks_access_entry.existing == null
}

resource "aws_eks_access_entry" "terraform_admin" {
  count = local.should_create ? 1 : 0
}
```

**Pros:**
- Automatic, no manual decisions
- No collision errors

**Cons:**
- More complex code
- More failure modes (what if query fails?)
- Premature optimization for cosmetic problem

**Decision:** Rejected - over-engineering

### Alternative C: Separate Terraform Workspaces (Future)

**Approach:**
```
terraform/
  account/          # ECR, base IAM (once per account)
  platform-access/  # Access entries (once per environment)
  cluster/          # VPC, EKS (per build_id)
```

**Pros:**
- Clean lifecycle separation
- No collisions ever
- Clear boundaries

**Cons:**
- Requires restructuring
- More operational overhead
- Can wait until security hardening phase

**Decision:** Deferred - good future improvement but not needed now

---

## Implementation

### Files Modified

**envs/dev/terraform.tfvars:**
```hcl
# Commented out account-scoped resources
ecr_repositories = {}  # All entries commented with explanation
app_secrets = {}        # All entries commented with ADR-0143 reference
```

**envs/dev/main.tf:**
```hcl
# Access entry remains simple - no conditionals
resource "aws_eks_access_entry" "terraform_admin" {
  cluster_name  = module.eks[0].cluster_name
  principal_arn = data.aws_caller_identity.current.arn
  type          = "STANDARD"
  # No count, always attempts creation
}
```

**No changes to:**
- envs/dev/variables.tf (no new variables added)
- Makefile (deploy command unchanged)
- Bootstrap scripts (unchanged)

---

## Related Documentation

- **[ADR-0007](./ADR-0007-platform-environment-model.md)**: Environment model (ephemeral vs persistent)
- **[ADR-0032](./ADR-0032-platform-eks-access-model.md)**: EKS access model (bootstrap vs steady-state)
- **[ADR-0143](./ADR-0143-secret-request-contract.md)**: Secret request contract (Backstage workflow)
- **[ADR-0148](./ADR-0148-seamless-build-deployment-with-immutability.md)**: Previous implementation (superseded)

---

## Follow-ups

### Short-term (Accepted as-is)
- Document collision error handling in runbook
- Add examples to README for first-time vs subsequent builds

### Medium-term (When Tightening Security)
- Move access entries to separate terraform workspace
- Implement least-privilege access model (ADR-0032)
- Create one-time setup script for environment-scoped resources

### Long-term (When Scaling)
- Separate terraform workspaces for each lifecycle scope
- Automated cleanup policies for ephemeral resources
- Cost attribution per build_id via governance-registry

---

## Notes

**Key Insight:**
> "The best solution is the simplest one that works. A collision error that's explicit and safe is better than complex code that prevents it."

**Developer Experience Principle:**
> "Make it easy to do the right thing. If a developer has to make a decision, they might make the wrong one. If the system makes the decision and tells you what it did, that's better."

**Collision Errors Are Acceptable When:**
- They're explicit (not silent)
- They're safe (system works despite error)
- They're informative (tell you what's already there)
- They're rare (only on second+ occurrence)
- Alternative solutions add more complexity than they remove

---

## Status History

- **2026-01-13 (Initial)**: Created to supersede ADR-0148
- **2026-01-13 (Revision)**: Updated to document simplified approach after rejecting conditional variables

---

## Supersession Details

**This ADR supersedes [ADR-0148](./ADR-0148-seamless-build-deployment-with-immutability.md)** with the following refinements:

**What's Preserved from ADR-0148:**
- ✅ Two-phase deployment pattern
- ✅ Build ID immutability enforcement
- ✅ Governance registry integration
- ✅ Seamless `make deploy` command
- ✅ Service accounts in Phase 1
- ✅ `apply_kubernetes_addons` gate

**What's Changed from ADR-0148:**
- 🔄 Access entry handling: From "may need conditional" to "simple, always create"
- 🔄 ECR repositories: Now explicitly commented out (not managed per cluster)
- 🔄 Secrets Manager: Now explicitly commented out (use Backstage workflow)
- 🔄 Developer experience: Prioritized simplicity over preventing collision errors

**Rationale for Supersession:**
ADR-0148 was correct about the architecture but didn't account for resource lifecycle scope mismatches. This ADR completes the implementation by clarifying resource boundaries and choosing simplicity over complexity for developer experience.
