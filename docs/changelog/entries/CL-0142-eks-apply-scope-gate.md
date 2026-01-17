---
id: CL-0142
title: EKS Apply Scope Gate
type: changelog
status: active
date: 2026-01-17
author: platform-team
category: ci-workflow
relates_to:
  - ADR-0028-platform-dev-branch-gate
  - infra-terraform-apply-dev
  - PR_GUARDRAILS_INDEX
---

# CL-0142: EKS Apply Scope Gate

## Summary

Added scope-based gating to the `infra-terraform-apply-dev.yml` workflow to prevent accidental EKS cluster rebuilds when merging PRs that contain terraform changes.

## Problem

When PR #252 (RDS provisioning automation) was merged to main, it included changes to `envs/dev/main.tf` and `modules/aws_secrets_manager/`. The workflow trigger path matching caused an unintended full infrastructure apply, recreating an EKS cluster and consuming vCPU quota.

## Solution

Implemented a scope check job that:

1. Detects if EKS-related files changed (`modules/aws_eks/**`, `envs/dev/main.tf`)
2. If EKS files changed: **plan only**, requires manual `workflow_dispatch` to apply
3. If only RDS/other modules changed: **auto-apply proceeds**

## Behavior Matrix

| Trigger | EKS Files Changed | Result |
|---------|-------------------|--------|
| Push to main | No | Auto-apply |
| Push to main | Yes | Plan only, manual apply required |
| workflow_dispatch | N/A | Apply with confirmation |

## Files Changed

- `.github/workflows/infra-terraform-apply-dev.yml` - Added scope check job

## Benefits

- RDS standalone changes can auto-deploy via PR merge
- EKS changes require explicit manual trigger
- Backstage RDS scaffolder works automatically
- Prevents accidental cluster rebuilds
