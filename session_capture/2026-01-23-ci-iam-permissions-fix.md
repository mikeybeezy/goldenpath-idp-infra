---
id: 2026-01-23-ci-iam-permissions-fix
title: CI IAM Permissions Fix and Secrets Manager Count Dependency
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0177-ci-iam-comprehensive-permissions
  - ADR-0030-platform-precreated-iam-policies
  - 33_IAM_ROLES_AND_POLICIES
---
# Session Capture: CI IAM Permissions Fix and Secrets Manager Count Dependency

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-22 to 2026-01-23
**Timestamp:** 2026-01-23T06:00:00Z
**Branch:** development (goldenpath-idp-infra)

## Scope

- Fix Terraform count dependency error blocking ephemeral builds
- Add comprehensive CI IAM policy with proper resource scoping
- Create ADR-0177 superseding ADR-0030
- Tighten IAM policy from overly permissive wildcards

## Work Summary

- Diagnosed `invalid count argument` error in secrets manager module
- Root cause: `count` depended on `secret_arn` (apply-time) instead of plan-time value
- Added `will_have_secret` local variable for plan-time determination
- Identified CI IAM permissions gap causing AccessDenied errors
- Created comprehensive IAM policy with resource scoping
- Tightened policy after user feedback about overly open permissions

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Terraform count dependency error | `secret_arn` is computed at apply time | Added `will_have_secret` plan-time local |
| CI AccessDenied for iam:CreatePolicy | ADR-0030 restricted permissions | ADR-0177 grants scoped permissions |
| CI AccessDenied for secretsmanager:CreateSecret | Missing Secrets Manager perms | Added to policy with `goldenpath/*` scope |
| Overly permissive IAM policy | Initial policy used `*` for many services | Tightened with tag conditions and ARN patterns |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fix count dependency | Add `will_have_secret` local | Plan-time determinable, doesn't break existing logic |
| IAM policy approach | Comprehensive with scoping | Balance between least-privilege and CI reliability |
| Supersede ADR-0030 | Create ADR-0177 | ADR-0030's approach unsustainable as codebase evolved |
| Resource scoping | `goldenpath-*` prefix + tags | Limits blast radius while allowing Terraform to manage resources |

## Artifacts Touched (links)

### Modified

- `modules/aws_secrets_manager/main.tf` - Added `will_have_secret` local, fixed count
- `docs/adrs/ADR-0030-platform-precreated-iam-policies.md` - Marked as superseded
- `docs/60-security/33_IAM_ROLES_AND_POLICIES.md` - Updated with new policy reference

### Added

- `docs/10-governance/policies/iam/github-actions-terraform-full.json` - Comprehensive CI policy
- `docs/adrs/ADR-0177-ci-iam-comprehensive-permissions.md` - New ADR
- `session_capture/2026-01-23-ci-iam-permissions-fix.md` - This file

## Validation

- Terraform validate passes for all environments (dev, test, staging, prod)
- Pre-commit hooks pass
- IAM policy reviewed and tightened per user feedback

## Current State / Follow-ups

- PR #275 created from development to main
- User needs to apply IAM policy in AWS console
- After policy applied, trigger new ephemeral build with build_id `22-01-26-02`

**Recommended follow-ups:**
- V1.1: Create bootstrap Terraform to manage CI permissions in code
- Add CI permission drift detection
- Document required permissions per Terraform module

Signed: Claude Opus 4.5 (2026-01-23T06:00:00Z)
