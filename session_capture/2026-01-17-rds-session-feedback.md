---
id: RDS_SESSION_FEEDBACK
title: RDS Session Feedback - Agent Review
type: documentation
owner: platform-team
status: active
created: 2026-01-17
reviewer: claude-opus-4-5
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
---

# RDS Session Feedback - Agent Review

**Reviewer:** Claude Opus 4.5 (claude-opus-4-5-20251101)
**Date:** 2026-01-17
**Sessions Reviewed:**
- 2026-01-17T07:15:26Z (codex) - RDS guardrails + schema fixes
- 2026-01-17T07:24:58Z (codex) - RDS guardrail fixes + schema alignment

---

## Diff Review: Original vs Follow-up Session

### Improvements Made (Follow-up Session)

| Issue Raised | Fix Applied | Status |
|--------------|-------------|--------|
| Missing metadata header | Added `# Owner: platform` + `# Relates-To:` | Fixed |
| No workflow_dispatch | Added `workflow_dispatch:` trigger | Fixed |
| Regex escaping bug (`\\s`) | Fixed to `\s` in heredoc | Fixed |
| Redundant path triggers | Removed `envs/*-rds/terraform.tfvars` | Fixed |
| Logic gap (empty sets = drift) | Added `coupled_enabled()` check + skip if either empty | Fixed |
| Size regex won't match tfvars | Updated to `[:=]` and optional quotes | Fixed |
| ADR references missing | Added ADR-0158, ADR-0165, ADR-0166 to README | Fixed |
| Pattern mismatch (no length) | Backstage now uses `^[a-z][a-z0-9_]{2,62}$` | Fixed |

---

## Remaining Issues

### 1. Schema vs Reality Mismatch (Critical)

The schema (`schemas/requests/rds.schema.yaml`) describes a contract-driven architecture that **doesn't exist**:

- Schema says: "CI validates PR against schema (gate)" - No such gate exists
- Schema says: "On merge, parser generates Terraform + ESO manifests" - Parser exists but isn't wired
- `generates:` paths reference `.tmp/generated/` - Nothing creates these
- `enum_from: risk_profile_security_risk` - But Backstage/workflow use `none, low, medium, high, access`

**Recommendation:** Either implement the contract-driven flow or mark schema as "aspirational/draft" to avoid confusion.

### 2. Risk Enum Inconsistency

| Source | Risk Values |
|--------|-------------|
| Schema | `enum_from: risk_profile_security_risk` (undefined) |
| Backstage | `none, low, medium, high, access` |
| Workflow | `none, low, medium, high, access` |

**Recommendation:** Define `risk_profile_security_risk` in `schemas/metadata/enums.yaml` with these exact values.

### 3. Size Approval Guard Path Issue

The guard watches `docs/20-contracts/rds-requests/**` but this directory doesn't exist (git status shows `?? docs/20-contracts/rds-requests/`). The current flow creates entries in `rds-catalog.yaml`, not individual request files.

**Recommendation:** Either:
- Change path to just `docs/20-contracts/resource-catalogs/rds-catalog.yaml`
- Or create the `rds-requests/` directory and update workflow to write there

### 4. E2E Validation (Deferred - Post-Merge)

Both sessions noted "Validation: Not run in this session". The guardrails have never been tested against a real PR.

**Status:** Intentionally deferred until after merge. The guardrail workflows must exist on the target branch (e.g., `development` or `main`) before they can trigger on incoming PRs. This is expected behavior for GitHub Actions `pull_request` triggers.

**Post-Merge Action:** Create a test PR that:
- Adds a `size: large` entry to trigger size guard
- Modifies both coupled and standalone tfvars to trigger drift guard

### 5. Missing Staging/Prod Size Constraint

Schema says `dev_max_size` limits dev to `small`, but workflow validation only enforces this for `dev`. Schema also implies staging should be limited but workflow allows any size for staging.

**Recommendation:** Align workflow validation with schema rules (or update schema to match current workflow).

### 6. Catalog Owner Mismatch

- `rds-catalog.yaml` template in workflow: `owner: "database-team"`
- Schema: `owner: platform-team`
- Backstage: `owner: platform-team`

**Recommendation:** Standardize to `platform-team` everywhere.

---

## Best Practice Recommendations

### 1. Single Source of Truth

The schema should be the canonical source, with Backstage and workflow reading from it (or generated from it). Currently they're maintained separately and drift.

### 2. Test Before Merge

Add a CI job that validates Backstage template enums match workflow enums match schema enums.

### 3. Contract-Driven Aspirations vs Reality

Either:
- Implement the parser + generated artifacts flow described in schema
- Or update schema to reflect the actual current flow (direct tfvars modification)

### 4. Guard Workflow Testing

Add `workflow_call` trigger so guards can be tested in isolation without a real PR.

### 5. Enum Registry

Create `schemas/metadata/enums.yaml` entries for all referenced enums and have CI validate alignment.

---

## Summary

The follow-up session (07:24:58Z) addressed most of the technical bugs I identified. The remaining issues are architectural - the schema describes a contract-driven flow that isn't implemented, creating confusion about what's aspirational vs operational.

**Priority fixes:**
1. Decide: implement contract-driven flow OR update schema to match reality
2. Define risk enum in `schemas/metadata/enums.yaml`
3. Fix size guard path or create `rds-requests/` directory
4. Run E2E test of guardrails (post-merge)

---

**Signed:** Claude Opus 4.5 (claude-opus-4-5-20251101)
**Timestamp:** 2026-01-17T00:30:00Z
**Updated:** 2026-01-17T00:45:00Z - Clarified E2E validation is intentionally post-merge
