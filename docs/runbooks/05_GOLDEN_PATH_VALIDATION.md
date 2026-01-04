---
id: 05_GOLDEN_PATH_VALIDATION
title: 'Runbook: Golden Path Validation'
type: runbook
category: runbooks
version: 1.0
owner: platform-team
status: active
dependencies:
  - module:terraform
  - module:kubernetes
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: rerun-validation
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - BOOTSTRAP_README
  - TEARDOWN_README
  - 39_GOLDEN_PATH_VALIDATION
  - CI_WORKFLOWS
---

# Runbook: Golden Path Validation

## Purpose

Run a controlled end-to-end validation for the PR → apply → bootstrap → teardown
flow and confirm no orphaned AWS resources remain.

## When to run

- After changes to CI workflows or bootstrap/teardown scripts.
- Before declaring the platform stable.

## Inputs

- Environment: `dev`
- Lifecycle: `ephemeral`
- New `build_id` (dd-mm-yy-NN)

## Steps

### 1) PR plan

- Update `envs/dev/terraform.tfvars` with a new `build_id`.
- Open a PR and wait for **PR Terraform Plan**.
- Confirm the PR comment includes a plan summary and a full plan section.

### 2) Apply

Run `Infra Terraform Apply (dev)` with:

- `lifecycle=ephemeral`
- `build_id=<new id>`
- `new_build=true`
- `confirm_apply=apply`

Expected: apply guard accepts the PR plan for the merged PR head SHA.

### 3) Bootstrap

Run `ci-bootstrap.yml` with the same `build_id` and:

- `config_source=repo`
- `confirm_irsa_apply=true`
- `bootstrap_only=false`
- `scale_down_after_bootstrap=false`

Expected: bootstrap completes and IRSA service accounts are applied.

### 4) Teardown

Run `ci-teardown.yml` with the same `build_id` and:

- `cleanup_mode=delete`
- `force_delete_lbs=true` (default)

Expected: teardown completes without subnet dependency violations.

### 5) Verify no orphans

```bash
aws eks list-clusters --region eu-west-2 --output table
aws ec2 describe-network-interfaces --region eu-west-2 \
  --filters Name=tag:BuildId,Values=<build_id> \
  --query 'NetworkInterfaces[].{Id:NetworkInterfaceId,Status:Status,Type:InterfaceType,Desc:Description}' \
  --output table
```

Expected: no cluster for the build and no tagged ENIs remain.

## If something fails

- **Apply guard says no plan found:** ensure the PR plan completed on the PR
  head SHA and the merged commit references that PR.
- **Teardown stuck on subnets:** check for LB ENIs and confirm cluster-scoped
  LB deletion is enabled.
- **State mismatch:** verify `build_id` and `cluster_lifecycle` are identical
  across plan, apply, bootstrap, and teardown.

## Exit criteria

- All CI workflows complete successfully.
- No BuildId-tagged resources remain.
