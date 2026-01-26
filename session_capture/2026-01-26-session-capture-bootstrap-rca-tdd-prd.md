---
id: 2026-01-26-session-capture-bootstrap-rca-tdd-prd
title: Bootstrap RCA, TDD Gate Fix, PRD-0007 Review
type: documentation
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
  - ADR-0182-tdd-philosophy
  - PRD-0007-platform-test-health-dashboard
  - GOV-0016-testing-stack-matrix
---

# Session Capture: Bootstrap RCA, TDD Gate Fix, PRD-0007 Review

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-26
**Timestamp:** 2026-01-26T21:00:00Z
**Branch:** feature/tdd-foundation

## Scope

- Root cause analysis of ArgoCD destruction during v4 bootstrap
- Fix TDD gate workflow bugs in backstage repo
- Review and update PRD-0007 Platform Test Health Dashboard

## Work Summary

### 1. Bootstrap v4 Root Cause Analysis

**Finding:** v4 bootstrap at 16:40 succeeded - ArgoCD was deployed correctly. A subsequent terraform apply at 18:33 with `apply_kubernetes_addons=false` destroyed ArgoCD.

**Root Cause:** After RDS provisioning failed (hostname malformation issue), debug scripts were run that inadvertently triggered a terraform apply with wrong flags, destroying ArgoCD.

**Key Insight:** The `apply_kubernetes_addons=false` default in terraform.tfvars is intentional for v3 bootstrap. v4 bootstrap passes `-var="apply_kubernetes_addons=true"` via the script. Manual terraform applies without this flag will destroy ArgoCD.

**Resolution:** v4 bootstrap is sound. The chaos came from manual intervention post-RDS failure. The `rds_provision_k8s.sh` fix keeps RDS provisioning isolated from terraform state.

### 2. TDD Gate Workflow Fixes (backstage repo)

**Issues Fixed:**
1. Added `|| true` to grep pipeline (line 44) - prevents failure on empty results
2. Refactored PR comment body to use array join - avoids YAML parsing issues
3. Updated ADR link to use full GitHub URL instead of relative path

**Commit:** `0bad042` - fix: TDD gate workflow bugs

**File:** `.github/workflows/tdd-gate.yml`

### 3. PRD-0007 Platform Test Health Dashboard Review

**Inconsistency Found:** Original PRD had conflicting statements about failure behavior:
- "Should collection fail if no metrics found?" marked resolved as "Yes"
- "Should missing metrics be warning-only for V1?" still open

**Clarification:** "Collection failure" (script crashes) vs "missing metrics" (no tests ran) are distinct:
- Collection failure → hard-fail (something is broken)
- Missing metrics → warning for V1, hard-fail for V1.1 (gradual enforcement)

**Architecture Decision:** Both repos write independently to `governance-registry/test-metrics/{repo}.json`. Aggregation happens at read-time. This keeps repos decoupled and self-contained.

**Schema Enhancements Added:**
- `branch` field (for future per-branch rollups)
- `ci_run_id` field (traceability)
- `threshold_met` field (quick pass/fail indicator)
- Nested `frameworks[]` array for multi-framework support per repo

## Files Modified

| File | Repo | Change |
|------|------|--------|
| `.github/workflows/tdd-gate.yml` | backstage | Bug fixes (grep, PR comment, ADR link) |
| `docs/20-contracts/prds/PRD-0007-platform-test-health-dashboard.md` | infra | Resolved questions, schema, feedback |

## Commits Created

| Commit | Repo | Message |
|--------|------|---------|
| `0bad042` | backstage | fix: TDD gate workflow bugs |

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Both repos write test metrics independently | Decoupled, self-contained; aggregation is read-time concern |
| Warning-only for missing metrics in V1 | Allows graceful rollout; aligns with non-blocking guardrail |
| Collection script failure hard-fails | Something is broken, should not silently pass |

## Follow-up Items

- [ ] Push TDD gate fix to backstage origin
- [ ] Commit PRD-0007 updates
- [ ] Clean cluster rebuild with v4 bootstrap after teardown completes
- [ ] Implement Phase 1 of PRD-0007 (collector script + schema)

## Teardown Status

Cluster teardown in progress - stuck on LoadBalancer service cleanup (~15min wait remaining).
