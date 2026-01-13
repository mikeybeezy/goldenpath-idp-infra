---
id: ADR-0149-directory-based-environment-isolation
title: 'ADR-0149: Directory-Based Environment Isolation Over Terraform Workspaces'
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 3
schema_version: 1
relates_to:
  - ADR-0148
  - EKS-0001
supersedes: []
superseded_by: []
tags:
  - terraform
  - state-management
  - governance
  - safety
inheritance: {}
value_quantification:
  vq_class: ⚫ resilience
  impact_tier: high
  potential_savings_hours: 0.0
supported_until: 2027-01-13
version: 1.0
breaking_change: false
---

# ADR-0149: Directory-Based Environment Isolation Over Terraform Workspaces

Filename: `ADR-0149-directory-based-environment-isolation.md`

- **Status:** Accepted
- **Date:** 2026-01-13
- **Owners:** platform-team
- **Domain:** Platform
- **Decision type:** Architecture | Operations | Governance
- **Related:** ADR-0148, Schema-driven EKS provisioning, Born Governed framework

---

## Context

Golden Path IDP manages multiple environments (dev, staging, prod) with Terraform. The platform must decide between two state management approaches:

1. **Directory-based isolation** (current): Each environment has its own directory with separate state files
2. **Terraform workspaces**: Single directory with workspace-based state isolation

### Current Architecture

```
envs/
├── dev/
│   ├── backend.tf
│   ├── main.tf
│   └── terraform.tfvars
├── staging/
│   ├── backend.tf
│   ├── main.tf
│   └── terraform.tfvars
└── prod/
    ├── backend.tf
    ├── main.tf
    └── terraform.tfvars
```

Each environment has:
- Separate S3 state file paths
- Independent DynamoDB lock table entries
- Environment-specific tfvars files
- Isolated Terraform execution context

### Why This Decision Exists Now

1. **Schema-driven provisioning** ([scripts/eks_build_parser.py:100](scripts/eks_build_parser.py:100)) generates environment-specific tfvars:
   ```python
   out_path = Path(args.out_dir) / env / f"{cid}.auto.tfvars.json"
   # Output: envs/dev/EKS-0001.auto.tfvars.json
   ```

2. **Born Governed principles** require explicit environment boundaries and audit trails

3. **Team requested clarity** on whether Terraform workspaces offer advantages over current approach

4. **Safety concerns** about accidental cross-environment operations (e.g., `terraform destroy` in wrong workspace)

### Constraints

- Multi-team platform with varying permission levels (junior devs restricted to dev environment)
- Production safety is paramount (no accidental prod changes)
- Schema-driven infrastructure provisioning must remain simple
- CI/CD validates Terraform across all environments independently
- State file corruption in one environment must not affect others

---

## Decision

**We will maintain directory-based environment isolation and NOT adopt Terraform workspaces for environment management.**

Each environment (dev, staging, test, prod) will continue to:
- Have its own directory under `envs/`
- Maintain separate state files in S3 with distinct paths
- Use environment-specific backend configurations
- Support independent Terraform operations without workspace selection

---

## Scope

### This Decision Applies To

- All environment-level Terraform configurations (`envs/dev`, `envs/staging`, `envs/prod`, `envs/test`)
- State file organization in S3 backend
- CI/CD workflows validating Terraform configurations
- Schema-driven provisioning scripts (EKS build parser, service generators)
- IAM policies controlling state file access

### This Decision Does NOT Apply To

- **Feature branch testing**: Workspaces MAY be used for short-lived feature testing within a single environment
- **Multi-region deployments**: Workspaces MAY be used for deploying same environment to multiple regions (e.g., `prod-us-east-1`, `prod-eu-west-2`)
- **Module development**: Workspace usage in local module testing is acceptable
- **Shared modules**: `modules/` directory uses backend-less Terraform (no state management decision needed)

---

## Consequences

### Positive

1. **Explicit Safety**
   - Current directory (`pwd`) shows which environment you're deploying to
   - No risk of `terraform workspace select` accidents
   - File paths in PRs make environment changes obvious
   - Example: `git diff envs/prod/main.tf` → clearly shows prod change

2. **Per-Environment IAM Permissions**
   - S3 state files isolated by path: `s3://terraform-state/envs/dev/*` vs `s3://terraform-state/envs/prod/*`
   - Junior engineers can access dev state without prod access
   - Granular IAM policies per environment:
     ```json
     {
       "Effect": "Allow",
       "Action": ["s3:GetObject", "s3:PutObject"],
       "Resource": "arn:aws:s3:::terraform-state/envs/dev/*"
     }
     ```

3. **Schema-Driven Architecture Alignment**
   - EKS build parser naturally maps to directories: `env → envs/{env}/`
   - Cluster request schemas ([docs/catalogs/clusters/platform/dev/EKS-0001.yaml](docs/catalogs/clusters/platform/dev/EKS-0001.yaml:11)) specify environment
   - Generated tfvars land in correct directory automatically
   - No workspace name logic needed in governance scripts

4. **Per-Environment Flexibility**
   - Prod can use stable Kubernetes 1.28, dev can test 1.29
   - Different module versions per environment
   - Environment-specific resource configurations without conditionals
   - Example:
     ```hcl
     # envs/dev/main.tf
     bootstrap_mode = true  # Fast bring-up for dev

     # envs/prod/main.tf
     bootstrap_mode = false # Production sizing
     ```

5. **Disaster Recovery Isolation**
   - Corrupted prod state doesn't affect dev/staging
   - S3 versioning protects each state file independently
   - Can restore prod from backup without touching other environments

6. **Clear CI/CD Validation**
   - Current workflow ([.github/workflows/ci-terraform-lint.yml:33](/.github/workflows/ci-terraform-lint.yml:33)):
     ```bash
     find . -type f -name "*.tf" | while read dir; do
       terraform init -backend=false
       terraform validate
     done
     ```
   - Each directory validated independently
   - No workspace selection logic in CI

7. **Audit Trail Clarity**
   - Git history shows which environment files changed
   - Terraform plan outputs clearly labeled by directory context
   - Observability: logs naturally tagged with directory path

### Tradeoffs / Risks

1. **Code Duplication**
   - Each `envs/*/main.tf` has similar structure
   - Changes must be applied to multiple directories
   - **Mitigation**: Shared modules (`modules/vpc`, `modules/eks`) contain 80% of logic
   - **Acceptance**: 20% duplication in orchestration layer is acceptable for safety

2. **Backend Configuration Overhead**
   - Each environment requires backend initialization
   - Must pass `-backend-config` or maintain `.tfbackend` files
   - **Mitigation**: Scriptable with wrapper scripts if needed

3. **More Files to Manage**
   - 4 environments × N files = more total files
   - **Mitigation**: Healer script ([scripts/standardize_metadata.py](scripts/standardize_metadata.py:1)) already standardizes metadata across directories
   - **Acceptance**: File count is not a concern with proper tooling

4. **Potential for Environment Drift**
   - Environments can diverge if changes applied inconsistently
   - **Mitigation**:
     - Schema-driven provisioning enforces consistency
     - CI validates all environments on every PR
     - Shared modules ensure infrastructure logic stays synchronized

### Operational Impact

**For Platform Engineers:**
- Continue using `cd envs/{env}` workflow
- No workspace commands to remember
- Clear context from directory location

**For CI/CD:**
- No changes required (already validates per-directory)
- State file paths remain stable

**For Schema-Driven Provisioning:**
- No changes to EKS build parser or other generators
- Environment mapping continues to work naturally

**For New Team Members:**
- Simpler mental model: "directory = environment"
- No hidden state to track (workspace name)
- Intuitive `cd` commands instead of workspace selection

---

## Alternatives Considered

### Alternative 1: Terraform Workspaces

**Approach**: Single `envs/` directory with workspace-based state isolation

**Structure**:
```
envs/
├── main.tf (shared)
├── variables.tf
└── terraform.tfstate.d/
    ├── dev/
    ├── staging/
    └── prod/
```

**Workflow**:
```bash
cd envs/
terraform workspace select dev
terraform apply

terraform workspace select prod
terraform apply
```

**Why Rejected**:

1. **Human Error Risk** (Critical)
   - Workspace selection is hidden state
   - Risk of `terraform destroy` in wrong workspace
   - No directory-level safety net
   - Quote from HashiCorp docs: "Workspaces are not suitable for system decomposition or deployments requiring separate credentials and access controls"

2. **Breaks Schema-Driven Provisioning**
   - EKS parser outputs to `envs/{env}/`, requires refactor
   - Would need workspace-aware logic in all governance scripts
   - Complicates Born Governed framework

3. **Loss of Per-Environment Flexibility**
   - All environments must use same code
   - Can't have different module versions (prod stable, dev latest)
   - Conditionals required for environment-specific resources

4. **IAM Permission Limitations**
   - All state files in same bucket prefix
   - Can't grant dev-only access to junior engineers
   - All-or-nothing permissions model

5. **CI/CD Complexity**
   - Must manage workspace selection in CI
   - State locking conflicts between environments

**When Workspaces ARE Appropriate**:
- Short-lived feature branch testing (`terraform workspace new feature-eks-1.30`)
- Multi-region deployments of same environment (`prod-us-east-1`, `prod-eu-west-2`)
- Single-team projects without strict environment isolation

### Alternative 2: Terragrunt

**Approach**: Use Terragrunt for DRY configuration with directory isolation

**Structure**:
```
envs/
├── terragrunt.hcl (root)
├── dev/
│   └── terragrunt.hcl
├── staging/
│   └── terragrunt.hcl
└── prod/
    └── terragrunt.hcl
```

**Why Not Chosen (But Considered for Future)**:
- Adds external dependency (Terragrunt)
- Team must learn new tooling
- Current shared modules already solve 80% of duplication
- Complexity not justified for current scale

**Future Reconsideration Trigger**:
- If environments grow beyond 4-5
- If orchestration duplication becomes painful (>40% duplicate code)
- If advanced features needed (dependency ordering, before/after hooks)

### Alternative 3: Monorepo with Terraform Cloud Workspaces

**Approach**: Terraform Cloud manages workspaces with VCS-driven workflows

**Why Rejected**:
- Introduces external dependency (Terraform Cloud)
- State no longer self-hosted in S3
- Cost implications for multi-workspace usage
- Golden Path principle: Own your state

---

## Follow-ups

### Immediate (Week 1)

- [x] Create ADR-0149 documenting decision
- [ ] Update platform documentation to reference this ADR when discussing state management
- [ ] Add comment in `envs/dev/backend.tf` referencing ADR-0149

### Short-term (Month 1)

- [ ] Document workspace acceptable use cases in runbook (feature testing, multi-region)
- [ ] Create training material: "Why we use directories not workspaces"
- [ ] Add pre-commit hook warning if someone creates workspaces in `envs/*` directories

### Long-term (Quarter 1)

- [ ] Monitor for environment drift (automated comparison script)
- [ ] If duplication pain increases, revisit Terragrunt (see Alternative 2)
- [ ] Add to onboarding docs: "Golden Path environment management"

---

## Notes

### Assumptions

1. **Current scale is manageable**: 4 environments with shared modules keeps duplication low
2. **Safety over DRY**: Preventing prod accidents is more valuable than eliminating code duplication
3. **Team composition**: Mix of junior and senior engineers requires clear permission boundaries
4. **Schema-driven architecture**: Born Governed framework is core principle, not negotiable

### Future Reconsideration Triggers

**Revisit this decision if**:

1. Environments exceed 6-7 (duplication becomes unmanageable)
2. Orchestration code duplication exceeds 40%
3. Team unanimously requests workspace-based flow
4. Terraform introduces workspace IAM permissions (unlikely)
5. Schema-driven provisioning architecture changes fundamentally

**Do NOT reconsider based on**:
- Individual preference for workspace commands
- "Industry best practices" blog posts (context-dependent)
- Perceived "cleanliness" of single directory (safety trumps aesthetics)

### Known Unknowns

- **Multi-region expansion**: If Golden Path deploys to multiple regions, may need workspace strategy within each environment directory (e.g., `envs/prod/` with `us-east-1` and `eu-west-2` workspaces)
- **Environment proliferation**: If ephemeral environments become long-lived, may need hybrid approach

### References

- [Terraform Workspaces Documentation](https://developer.hashicorp.com/terraform/language/state/workspaces)
- [When to Use Terraform Workspaces](https://developer.hashicorp.com/terraform/cli/workspaces#when-to-use-multiple-workspaces)
- HashiCorp Warning: "Workspaces are not suitable for system decomposition or deployments requiring separate credentials and access controls"
- [ADR-0148: EKS Single-Build Refactor](ADR-0148-eks-single-build-refactor.md)
- [Schema-driven EKS provisioning](../../scripts/eks_build_parser.py)

### Related Discussions

- Platform team discussion on 2026-01-13: Terraform workspace evaluation
- Schema-driven architecture alignment with directory structure
- IAM permission granularity requirements

---

**Approval**: Platform team consensus 2026-01-13
**Implementation**: Already in place (affirming existing practice)
**Review Date**: 2027-01-13 (annual review)
