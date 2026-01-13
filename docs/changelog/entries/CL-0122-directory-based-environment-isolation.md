---
id: CL-0122-directory-based-environment-isolation
title: 'CL-0122: Formalize Directory-Based Environment Isolation Strategy'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - terraform
  - state-management
  - governance
  - cicd
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: documentation-only
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0149
  - ADR-0148
supersedes: []
superseded_by: []
tags:
  - governance
  - architecture
  - decision
inheritance: {}
value_quantification:
  vq_class: ⚫ resilience
  impact_tier: high
  potential_savings_hours: 0.0
supported_until: 2028-01-13
version: '1.0'
breaking_change: false
---

# CL-0122: Formalize Directory-Based Environment Isolation Strategy

Date: 2026-01-13
Owner: platform-team
Scope: terraform, state-management, governance
Related: ADR-0149

## Change Summary

Formalized the decision to maintain **directory-based environment isolation** instead of adopting Terraform workspaces. This affirms the existing practice and provides architectural rationale for future reference.

## What Changed

### Documentation Added
- **ADR-0149**: Architecture decision record documenting directory-based approach
- **Rationale**: Comprehensive analysis of workspaces vs. directories for Golden Path IDP
- **Alternatives**: Evaluated Terraform workspaces, Terragrunt, and Terraform Cloud

### No Code Changes
This is a **documentation-only change** affirming the existing architecture:
```
envs/
├── dev/       ← Separate directory per environment
├── staging/
├── prod/
└── test/
```

## Why This Change

### Context
Platform team evaluated whether Terraform workspaces would provide benefits over current directory-based approach. Key questions:
1. Could workspaces reduce code duplication?
2. Would workspace-based state improve team workflow?
3. Are there safety or governance tradeoffs?

### Decision Drivers

**Safety & Governance (Critical)**
- Directory-based: Explicit context (`cd envs/prod` → obvious)
- Workspaces: Hidden state (`terraform workspace show` → not obvious)
- **Winner**: Directories prevent accidental prod operations

**Schema-Driven Provisioning (Critical)**
- EKS build parser ([scripts/eks_build_parser.py:100](../../scripts/eks_build_parser.py)) generates:
  ```python
  out_path = Path(args.out_dir) / env / f"{cid}.auto.tfvars.json"
  # Output: envs/dev/EKS-0001.auto.tfvars.json
  ```
- Workspaces would require refactoring all governance scripts
- **Winner**: Directories align with Born Governed framework

**IAM Permissions (Critical)**
- Directories: Per-environment S3 paths enable granular IAM
  ```json
  "Resource": "arn:aws:s3:::terraform-state/envs/dev/*"
  ```
- Workspaces: All state files in same bucket prefix (all-or-nothing)
- **Winner**: Directories enable junior dev access to only dev environment

**Per-Environment Flexibility (Important)**
- Directories: Prod can use stable k8s 1.28, dev can test 1.29
- Workspaces: All environments must use same code
- **Winner**: Directories allow environment-specific configurations

**Code DRY (Nice-to-Have)**
- Directories: ~20% duplication in orchestration layer
- Workspaces: Single codebase (100% shared)
- **Mitigation**: Shared modules (`modules/vpc`, `modules/eks`) already solve 80%
- **Acceptance**: 20% duplication acceptable for safety benefits

## Impact Assessment

### Users Affected
- **Platform Engineers**: No workflow changes (affirms current practice)
- **CI/CD**: No changes (already validates per-directory)
- **Schema Generators**: No changes (EKS parser continues working)
- **New Team Members**: Clearer mental model ("directory = environment")

### Systems Affected
- **Terraform State**: Continues using S3 with separate paths
- **Backend Config**: No changes to `backend.tf` files
- **CI Workflows**: No changes to validation pipelines
- **IAM Policies**: Can continue using per-environment S3 permissions

### Risk Profile
- **Production Impact**: None (documentation only)
- **Security Risk**: None (actually improves clarity on security boundaries)
- **Coupling Risk**: None (reduces coupling to workspace abstractions)

## Benefits

### Safety
- Explicit environment context from directory location
- No risk of `terraform workspace select` accidents
- File paths in PRs clearly show environment changes

### Governance
- IAM permissions granular at environment level
- Audit trail clear from git history
- Schema-driven provisioning remains simple

### Operations
- CI/CD validation stays simple (per-directory)
- State corruption isolated to single environment
- Disaster recovery per-environment

### Developer Experience
- Intuitive workflow: `cd envs/dev` → "I'm in dev"
- No hidden state to track (workspace name)
- Junior engineers restricted to dev directory (S3 IAM)

## Tradeoffs Accepted

### Code Duplication
- Each `envs/*/main.tf` has similar structure (~20% duplication)
- **Mitigation**: Shared modules contain 80% of logic
- **Acceptance**: Safety > DRY principle

### Backend Configuration
- Each environment requires separate backend init
- **Mitigation**: Scriptable if needed
- **Acceptance**: Minor operational overhead

## Migration Impact

### No Migration Required
This change affirms existing architecture. **No migration needed.**

### If Workspaces Existed (Hypothetical)
If team had been using workspaces, migration would involve:
1. Creating `envs/{dev,staging,prod}` directories
2. Splitting single `main.tf` into per-environment files
3. Migrating state files to separate S3 paths
4. Updating EKS build parser and governance scripts
5. Updating CI/CD pipelines

**Estimated effort**: 2-3 weeks (not applicable)

## Rollback Plan

**Not applicable** - This is a documentation-only change affirming existing practice.

If team later decides to adopt workspaces:
1. Create new ADR superseding ADR-0149
2. Document migration plan in new ADR
3. Update this changelog entry with superseded status

## Testing & Validation

### Validation Performed
- ✅ Current directory structure reviewed
- ✅ Schema-driven provisioning tested with directory approach
- ✅ CI/CD pipelines validated with per-directory structure
- ✅ IAM permissions confirmed working with separate S3 paths
- ✅ Team workflow documented and confirmed

### No Testing Required
Documentation-only change, no code modified.

## Follow-up Actions

### Immediate
- [x] Create ADR-0149
- [x] Create CL-0122
- [ ] Add comment in `envs/dev/backend.tf` referencing ADR-0149

### Short-term (Month 1)
- [ ] Document workspace acceptable use cases (feature testing, multi-region)
- [ ] Add to onboarding docs: "Golden Path environment management"
- [ ] Create training material on directory vs. workspace rationale

### Long-term (Quarter 1)
- [ ] Add pre-commit hook warning if workspaces created in `envs/*`
- [ ] Monitor for environment drift (automated comparison)
- [ ] Review ADR-0149 annually

## References

- [ADR-0149: Directory-Based Environment Isolation](../adrs/ADR-0149-directory-based-environment-isolation.md)
- [Terraform Workspaces Documentation](https://developer.hashicorp.com/terraform/language/state/workspaces)
- HashiCorp Warning: "Workspaces are not suitable for system decomposition or deployments requiring separate credentials"
- [ADR-0148: EKS Single-Build Refactor](../adrs/ADR-0148-eks-single-build-refactor.md)

## Version History

- **v1.0** (2026-01-13): Initial documentation of directory-based decision

## Notes

### When to Reconsider
Revisit ADR-0149 if:
- Environments exceed 6-7 (duplication becomes unmanageable)
- Orchestration code duplication exceeds 40%
- Schema-driven provisioning architecture changes fundamentally
- Terraform adds workspace-level IAM permissions (unlikely)

### Acceptable Workspace Usage
Workspaces ARE appropriate for:
- **Feature testing**: `terraform workspace new feature-eks-1.30` (short-lived)
- **Multi-region**: `prod-us-east-1`, `prod-eu-west-2` (within same environment)
- **Module development**: Local testing (no production impact)

Workspaces are NOT appropriate for:
- **Environment isolation**: dev/staging/prod (use directories)
- **Multi-team platforms**: Require separate credentials (use directories)
- **Long-lived environments**: Risk of accidental operations (use directories)

---

**Changelog Type**: Architecture Decision
**Breaking Change**: No
**Rollback Required**: No
**Documentation Only**: Yes
