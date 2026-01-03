# CI Workflows Index (Living)

Doc contract:
- Purpose: Index CI workflows with owners, inputs, and runbooks.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md

This index lists every CI workflow, what it does, and where to find the
runbook/docs. Keep this file updated to avoid workflow sprawl.

ASCII map (quick glance):

```text
CI Workflows (GitHub Actions)

├─ Guardrails / Policy (PR)
│  ├─ Policy - Branch Policy Guard
│  ├─ Policy - Changelog Policy
│  ├─ Quality - Doc Freshness Check
│  ├─ Docs - Metadata Validation
│  ├─ Quality - Pre-commit checks
│  ├─ Quality - YAML Lint
│  └─ Quality - Super Linter (Markdown)
│
├─ Terraform Plan
│  ├─ Plan - PR Terraform Plan
│  ├─ Plan - Infra Terraform Checks
│  └─ Plan - Infra Terraform Plan Pipeline
│
├─ Terraform Apply
│  ├─ Apply - Infra Terraform Apply (dev)
│  ├─ Apply - Infra Terraform Update (dev)
│  ├─ Apply - Infra Terraform Apply (test)
│  ├─ Apply - Infra Terraform Apply (staging)
│  └─ Apply - Infra Terraform Apply (prod)
│
├─ Bootstrap / Tooling
│  ├─ Bootstrap - CI Bootstrap (Stub)
│  └─ Bootstrap - CI Backstage (Stub)
│
└─ Teardown / Recovery
   ├─ Ops - CI Teardown
   ├─ Ops - CI Orphan Cleanup
   ├─ Ops - CI Force Unlock
   └─ Ops - CI Managed LB Cleanup
```

---

## Policy

### Policy - Branch Policy Guard
- Trigger: pull_request → main
- Owner: platform
- Inputs: none
- Purpose: enforce development → main only
- Runbook: `docs/adrs/ADR-0028-platform-dev-branch-gate.md`

### Policy - Changelog Policy
- Trigger: pull_request (label/edited/sync)
- Owner: platform
- Inputs: none
- Purpose: require changelog entry when label set
- Runbook: `docs/changelog/README.md`

## Quality

### Quality - Doc Freshness Check
- Trigger: pull_request docs/**; push main docs/**
- Owner: platform
- Inputs: none
- Purpose: warning-only doc freshness validation
- Runbook: `docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md`

### Docs - Metadata Validation
- Trigger: pull_request docs/**, scripts/validate-metadata.py
- Owner: platform
- Inputs: none
- Purpose: validate metadata frontmatter and references in docs
- Runbook: `docs/90-doc-system/METADATA_VALIDATION_GUIDE.md`

### Quality - Pre-commit checks
- Trigger: pull_request
- Owner: platform
- Inputs: none
- Purpose: run repo pre-commit hooks
- Runbook: `CONTRIBUTING.md`

### Quality - YAML Lint
- Trigger: pull_request on .github/workflows/**
- Owner: platform
- Inputs: none
- Purpose: lint workflow YAML
- Runbook: `CONTRIBUTING.md`

### Quality - Super Linter (Markdown)
- Trigger: pull_request docs/**; push main docs/**
- Owner: platform
- Inputs: none
- Purpose: markdown lint (currently disabled)
- Runbook: `docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md`

## Plan

### Plan - PR Terraform Plan
- Trigger: pull_request (tf/tfvars)
- Owner: platform
- Inputs: none (reads envs/dev/terraform.tfvars)
- Purpose: plan and comment on PR
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`, `docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md`

### Plan - Infra Terraform Checks
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, lifecycle, build_id, new_build, require_state
- Purpose: fmt/validate/plan on demand
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

### Plan - Infra Terraform Plan Pipeline
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, lifecycle, build_id, new_build, require_state, region
- Purpose: simplified manual plan flow
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

## Apply

### Apply - Infra Terraform Apply (dev)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: confirm_apply, lifecycle, build_id, new_build
- Purpose: apply dev infra with plan gate
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

### Apply - Infra Terraform Update (dev)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: confirm_apply, build_id
- Purpose: apply dev updates to an existing ephemeral cluster (plan gate + state must exist)
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

### Apply - Infra Terraform Apply (test)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: confirm_apply, lifecycle, build_id, new_build
- Purpose: apply test infra with plan gate
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

### Apply - Infra Terraform Apply (staging)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: confirm_apply, lifecycle, build_id, new_build
- Purpose: apply staging infra with plan gate
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

### Apply - Infra Terraform Apply (prod)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: confirm_apply, lifecycle, build_id, new_build
- Purpose: apply prod infra with plan gate
- Runbook: `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

## Bootstrap

### Bootstrap - CI Bootstrap (Stub)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, region, cluster_name, lifecycle, config_source, tfvars_b64, build_id,
  bootstrap_only, new_build, confirm_irsa_apply, node_instance_type, min_ready_nodes,
  skip_argo_sync_wait, skip_cert_manager_validation, compact_output
- Purpose: bootstrap cluster tooling (stub)
- Runbook: `docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md`, `docs/40-delivery/17_BUILD_RUN_FLAGS.md`

### Bootstrap - CI Backstage (Stub)
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, image_tag
- Purpose: build/push/deploy Backstage (stub)
- Runbook: `docs/00-foundations/18_BACKSTAGE_MVP.md`

## Ops / Recovery

### Ops - CI Teardown
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, region, cluster_name, build_id, lifecycle, teardown_version,
  cleanup_mode, force_delete_lbs, force_delete_lb_finalizers, etc.
- Purpose: teardown (v1/v2) with cleanup + metrics
- Runbook: `docs/runbooks/09_CI_TEARDOWN_RECOVERY_V2.md`

### Ops - CI Orphan Cleanup
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, build_id, region
- Purpose: delete BuildId-tagged orphans
- Runbook: `docs/runbooks/ORPHAN_CLEANUP.md`

### Ops - CI Force Unlock
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, region, lifecycle, build_id, lock_id, confirm_unlock
- Purpose: break-glass Terraform unlock
- Runbook: `docs/runbooks/07_TF_STATE_FORCE_UNLOCK.md`

### Ops - CI Managed LB Cleanup
- Trigger: workflow_dispatch
- Owner: platform
- Inputs: env, region, cluster_name, build_id, lifecycle, stack_tag,
  dry_run, confirm_delete, delete_cluster_tagged_sgs
- Purpose: delete LBC-managed LBs/ENIs/SGs when cluster is gone
- Runbook: `docs/runbooks/08_MANAGED_LB_CLEANUP.md`
