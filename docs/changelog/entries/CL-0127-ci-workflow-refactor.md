---
id: CL-0127
title: CI Workflow Refactor and Bootstrap Integration
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
  - ADR-0155-ci-governance-registry-fetch
  - CI_TERRAFORM_WORKFLOWS
  - CL-0127
  - DOCS_85-HOW-IT-WORKS_README
  - HOW_IT_WORKS_INDEX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-15
date: 2026-01-15
author: platform-team
breaking_change: false
---

## Summary

Refactored CI Terraform workflows to include automatic bootstrap after infrastructure apply, deprecated redundant workflows, and consolidated how-it-works documentation.

## Changes

### Apply Workflow Enhancement

**Problem**: The `infra-terraform-apply-dev.yml` workflow only ran Terraform apply. Bootstrap (Kong, ArgoCD, Cert-Manager) was not executed, leaving clusters without platform services.

**Solution**: Added post-apply steps to the workflow:

1. **EKS Access Setup** - Creates access entry for CI runner after cluster exists
2. **Bootstrap Execution** - Runs `make bootstrap` to install platform services

```yaml
# New steps added after terraform apply:
- name: Setup EKS access for runner
  run: |
    aws eks create-access-entry ...
    aws eks update-kubeconfig ...

- name: Run bootstrap
  run: |
    make bootstrap ENV=dev BUILD_ID=${BUILD_ID}
```

### Workflow Deprecation

Deprecated 3 redundant workflows to `.github/workflows/deprecated/`:

| Deprecated Workflow | Replaced By |
|---------------------|-------------|
| `infra-terraform-dev-pipeline.yml` | `infra-terraform.yml` |
| `infra-terraform-apply-dev-branch.yml` | `infra-terraform-apply-dev.yml` |
| `infra-terraform-update-dev.yml` | `infra-terraform-apply-dev.yml` |

### Documentation Consolidation

Consolidated how-it-works documentation into `docs/85-how-it-works/`:

```text
docs/85-how-it-works/
├── ci-terraform/           # CI workflow documentation
├── governance/             # Platform governance mechanics
├── secrets-flow/           # Secret management flows
└── self-service/           # Self-service provisioning
```

Added new `CI_TERRAFORM_WORKFLOWS.md` with ASCII/mermaid diagrams explaining:
- Workflow architecture and relationships
- Build ID validation flow
- State key strategy
- Troubleshooting guide

## Files Changed

### Workflows
- `.github/workflows/infra-terraform-apply-dev.yml` - Added bootstrap integration
- `.github/workflows/deprecated/` - Created deprecation folder with README

### Documentation
- `docs/85-how-it-works/` - New consolidated structure
- `docs/85-how-it-works/ci-terraform/CI_TERRAFORM_WORKFLOWS.md` - New
- `docs/85-how-it-works/README.md` - New index

### References Updated
- 17 files updated with new documentation paths

## Testing

- `make fmt` - Passed
- `make validate` - Passed
- `pre-commit run --all-files` - Passed

## Rollback

```bash
git revert <commit-sha>
```

No data migration required. Deprecated workflows remain available in `deprecated/` folder for 90 days.
