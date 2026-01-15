---
id: test-plan
title: Governance Registry Mirror - Feature Test Plan
type: test-suite
---

# Governance Registry Mirror - Feature Test Plan

**Test ID:** FT-GOVREG-001
**Feature:** Governance Registry Mirror Pattern
**Version:** 1.0
**Created:** 2026-01-12
**Owner:** Platform Team
**Test Type:** Feature Test

---

## Test Planning

- [x] **What are we testing?** Governance Registry Mirror - First Pulse Generation
- [x] **Why are we testing it?** To verify ADR-0145 implementation works end-to-end
- [x] **What's the success criteria?**
  - Platform health report generated with required metadata
  - Report committed to `governance-registry` branch
  - Both `latest/` and `history/` updated atomically
  - Validator passes (no integrity violations)
- [x] **What's the failure criteria?**
  - Missing required metadata fields
  - Validator rejects commit
  - Non-atomic update (latest without history)
  - Manual intervention required
- [x] **Dependencies:**
  - `governance-registry` branch exists
  - `governance-registry-writer.yml` workflow exists
  - `validate_govreg.py` script functional
  - `govreg.schema.yaml` schema defined
- [x] **Environment:** `development` branch → `governance-registry` (remote)
- [x] **Test type:** Feature Test (End-to-End)
- [x] **Estimated time:** 15 minutes
- [x] **Risk level:** Medium (tests new architectural pattern)

---

## Test Scope

### In Scope
1. Manual trigger of `governance-registry-writer.yml`
2. Platform health report generation
3. Metadata injection (chain-of-custody headers)
4. Atomic commit (latest + history)
5. Validator enforcement

### Out of Scope
- Automated triggers (will test in FT-GOVREG-002)
- PR comment notifications (future enhancement)
- Multiple concurrent updates (future test)

---

## Test Environment

### Prerequisites
```bash
# Branch structure
- development (source branch)
- governance-registry (target branch, orphan)

# Required files in development
- .github/workflows/governance-registry-writer.yml
- .github/workflows/govreg-validate.yml
- scripts/validate_govreg.py
- scripts/platform_health.py
- schemas/governance/govreg.schema.yaml
```

### Environment State
- Git commit: `c3f670d` (schema-driven validator)
- All changes pushed to `origin/development`
- `governance-registry` branch initialized with folder structure

---

## Test Data

### Expected Metadata Header
```yaml
---
type: governance-report
env: development
generated_at: <UTC_TIMESTAMP>
source:
  branch: development
  sha: <GIT_SHA>
pipeline:
  workflow: governance-registry-writer.yml
  run_id: <RUN_ID>
integrity:
  derived_only: true
---
```

### Expected Folder Structure
```
governance-registry/
└── environments/
    └── development/
        ├── latest/
        │   └── PLATFORM_HEALTH.md (updated)
        └── history/
            └── <date>-<sha>/
                └── PLATFORM_HEALTH.md (new)
```

---

## Test Steps

### Step 1: Trigger Workflow
**Action:** Manually trigger `governance-registry-writer.yml` from GitHub Actions UI
**Expected:** Workflow runs successfully
**Validation:** Check GitHub Actions run status

### Step 2: Verify Report Generation
**Action:** Check workflow logs for "Generate governance artifacts" step
**Expected:** `PLATFORM_HEALTH.md` created in workspace
**Validation:** Logs show file creation

### Step 3: Verify Metadata Injection
**Action:** Inspect generated `PLATFORM_HEALTH.md` in workflow artifacts
**Expected:** Contains all required frontmatter fields
**Validation:** All fields from `govreg.schema.yaml` present

### Step 4: Verify Atomic Commit
**Action:** Check `governance-registry` branch history
**Expected:** Single commit updating both `latest/` and `history/`
**Validation:** `git log --stat` shows both paths in one commit

### Step 5: Verify Validator Enforcement
**Action:** Check `govreg-validate.yml` workflow run
**Expected:** Validation passes (green check)
**Validation:** Workflow completes without errors

### Step 6: Verify Chain of Custody
**Action:** Compare `source.sha` in report with triggering commit
**Expected:** SHA matches the development branch commit
**Validation:** Manual inspection of frontmatter

---

## Success Criteria (Checklist)

- [ ] Workflow triggered successfully
- [ ] Report generated with content
- [ ] All required metadata fields present
- [ ] `latest/PLATFORM_HEALTH.md` updated
- [ ] `history/<date>-<sha>/PLATFORM_HEALTH.md` created
- [ ] Single atomic commit (not two separate commits)
- [ ] Validator workflow passes
- [ ] No manual git operations required

---

## Rollback Plan

If test fails:
1. Identify failure point from workflow logs
2. Fix issue in `development` branch
3. Re-run test
4. If `governance-registry` corrupted, reset branch:
   ```bash
   git push origin --delete governance-registry
   # Re-initialize from development
   ```

---

## Related Documentation

- **ADR-0145:** [Governance Registry Mirror Pattern](/docs/adrs/ADR-0145-governance-registry-mirror.md)
- **RB-0028:** [Registry Operations Runbook](/docs/70-operations/runbooks/RB-0028-governance-registry-operations.md)
- **How-it-Works:** [Governance Registry Mirror](/85-how-it-works/governance/GOVERNANCE_REGISTRY_MIRROR.md)

---

## Test Schedule

**Planned Execution:** 2026-01-12 (Today)
**Expected Duration:** 15 minutes
**Test Record:** `tests/feature-tests/governance-registry-mirror/test-record-20260112.md`

---

**Test Plan Approved:** Ready for execution
**Next Step:** Execute test and document results
