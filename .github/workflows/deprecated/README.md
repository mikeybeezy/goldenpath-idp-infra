# Deprecated Workflows

This folder contains GitHub Actions workflows that have been superseded by improved
implementations. They are retained for reference and rollback purposes.

## Deprecation Policy

1. Workflows moved here are disabled (renamed to `.yml.disabled`)
2. Each workflow includes a deprecation header explaining the replacement
3. Deprecated workflows are retained for 90 days before deletion
4. If rollback is needed, rename back to `.yml` and move to parent folder

## Best Practices for Workflow Design

### Single Responsibility

Each workflow should have one clear purpose:

- `pr-terraform-plan.yml` - PR validation and plan preview
- `infra-terraform.yml` - Manual multi-environment plan
- `infra-terraform-apply-{env}.yml` - Environment-specific apply

### Avoid Duplication

Before creating a new workflow, check if an existing one can be extended:

- Use `workflow_dispatch` inputs for flexibility
- Use conditional steps (`if:`) for environment-specific logic
- Use reusable workflows for shared steps

### Trigger Patterns

| Pattern | Use Case |
|---------|----------|
| `push` to main | Auto-apply after PR merge |
| `pull_request` | PR validation gates |
| `workflow_dispatch` | Manual operations |
| `workflow_run` | Chained workflows |

### Configuration Resolution

Prefer reading configuration from committed files (e.g., `terraform.tfvars`) over
workflow inputs. This ensures:

- PR review includes the configuration
- Audit trail via git history
- No manual input errors

## Deprecated Workflow Index

| Workflow | Deprecated | Replaced By | Reason |
|----------|------------|-------------|--------|
| `infra-terraform-apply-dev-branch.yml` | 2026-01-15 | `infra-terraform-apply-dev.yml` | Consolidated into main apply workflow with push trigger and tfvars resolution |
| `infra-terraform-dev-pipeline.yml` | 2026-01-15 | `infra-terraform.yml` | Duplicate functionality; main workflow supports all environments |
| `infra-terraform-update-dev.yml` | 2026-01-15 | `infra-terraform-apply-dev.yml` | Update operations consolidated into main apply; k8s resource toggle can be added as input |

## Migration Guide

### From `infra-terraform-apply-dev-branch.yml`

**Before**: Manual dispatch with explicit build_id input

```yaml
workflow_dispatch:
  inputs:
    build_id: "15-01-26-01"
```

**After**: Configure in `envs/dev/terraform.tfvars`, create PR, merge triggers apply

```hcl
cluster_lifecycle = "ephemeral"
build_id          = "15-01-26-01"
```

### From `infra-terraform-dev-pipeline.yml`

**Before**: Separate pipeline workflow for planning

**After**: Use `infra-terraform.yml` with same inputs (env, lifecycle, build_id)

### From `infra-terraform-update-dev.yml`

**Before**: Separate update workflow with `enable_k8s_resources` flag

**After**: Use `infra-terraform-apply-dev.yml` - k8s resources controlled by
`ENABLE_TF_K8S_RESOURCES` environment variable (set in workflow or tfvars)
