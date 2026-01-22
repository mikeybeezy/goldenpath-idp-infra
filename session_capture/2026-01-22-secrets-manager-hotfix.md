---
id: 2026-01-22-secrets-manager-hotfix
title: Secrets Manager Count Dependency Hotfix
type: hotfix
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - modules/aws_secrets_manager
---
# Session Capture: Secrets Manager Count Dependency Hotfix

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-22
**Timestamp:** 2026-01-22T21:20:00Z
**Branch:** hotfix/secrets-manager-count-fix

## Scope

- Fix Terraform count dependency error in aws_secrets_manager module

## Work Summary

- Identified root cause: `count = local.should_create_policy && local.secret_arn != null ? 1 : 0`
- `local.secret_arn` depends on apply-time value when creating new secrets
- Added `local.will_have_secret` as plan-time determinable alternative
- Changed count to use plan-time check

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Invalid count argument error | count depends on secret_arn which is computed at apply time | Use will_have_secret (plan-time determinable) |

## Artifacts Touched

### Modified

- `modules/aws_secrets_manager/main.tf` - Added will_have_secret local, updated count

## Validation

- `terraform validate` passes for envs/dev

Signed: Claude Opus 4.5 (2026-01-22T21:20:00Z)
