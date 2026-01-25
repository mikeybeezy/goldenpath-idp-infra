<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0165
title: Terraform Validation Fix for Non-Dev Environments
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - envs/test/main.tf
  - envs/staging/main.tf
  - envs/prod/main.tf
  - prompt-templates/PROMPT-0002-pre-commit-pre-merge-checks.txt
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - CL-0151-standalone-rds-state
  - ADR-0158-platform-standalone-rds-bounded-context
supersedes: []
superseded_by: []
tags:
  - terraform
  - ci
  - governance
  - validation
inheritance: {}
supported_until: 2028-01-22
value_quantification:
  vq_class: HV/HQ
  impact_tier: medium
  potential_savings_hours: 5.0
date: 2026-01-22
author: platform-team
---

# Terraform Validation Fix for Non-Dev Environments

## Summary

Fixed terraform validation errors in test, staging, and prod environments caused by outdated IAM module references. Also updated PROMPT-0002 to include terraform validation guidance to prevent similar issues.

## Problem

After commit `7e26b734` (2026-01-20) refactored the IAM module to remove `cluster_role_name` and `node_group_role_name` variables, only `envs/dev/main.tf` was updated. The test, staging, and prod environments still referenced these removed arguments, causing `terraform validate` to fail.

The `ci-terraform-lint.yml` workflow caught these errors but was not configured as a required status check, allowing PRs to merge despite failures.

## Root Cause

* IAM module refactored to move EKS cluster/node IAM roles to the EKS module
* Only dev environment was updated in the original commit
* Test, staging, prod environments were forgotten
* CI workflow ran but wasn't blocking

## Changes Made

### Environment Fixes

Removed deprecated arguments from IAM module calls in:

* `envs/test/main.tf`
* `envs/staging/main.tf`
* `envs/prod/main.tf`

```hcl
# Removed:
cluster_role_name    = "${var.iam_config.cluster_role_name}${local.role_suffix}"
node_group_role_name = "${var.iam_config.node_group_role_name}${local.role_suffix}"

# Added comment:
# NOTE: cluster_role_name and node_group_role_name removed.
# EKS cluster and node group IAM roles are created by the EKS module.
```

### PROMPT-0002 Updates

Added terraform validation section to prevent future issues:

* New "TERRAFORM VALIDATION" section with multi-env validate loop
* Added `ci-terraform-lint.yml` to blocking checks table
* Added terraform validate to quick commands
* Added terraform validation errors to common issues table

## Verification

All environments now pass terraform validate:

```bash
for env in dev test staging prod; do
  terraform -chdir=envs/$env init -backend=false -input=false
  terraform -chdir=envs/$env validate
done
# Result: Success for all environments
```

## Impact

* `ci-terraform-lint.yml` will now pass on PRs to main
* Agents following PROMPT-0002 will validate all environments before committing
* Prevents similar module interface drift in the future

## Recommendation

Add `ci-terraform-lint.yml` as a required status check in GitHub branch protection to prevent bypassing validation failures.
