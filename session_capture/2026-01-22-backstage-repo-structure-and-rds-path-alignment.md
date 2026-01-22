---
id: 2026-01-22-backstage-repo-structure-and-rds-path-alignment
title: Backstage Repo Structure PRD + RDS Secret Path Alignment
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - session_summary_template
---
# Backstage Repo Structure PRD + RDS Secret Path Alignment

## Session metadata

**Agent:** Codex
**Date:** 2026-01-22
**Timestamp:** 2026-01-22T05:06:54Z
**Branch:** development

## Scope

- Create a PRD for aligning the Backstage repo to a Spotify-style layout.
- Align documented/templated RDS secret paths to the canonical path.
- Fix `rds-allow-delete` to avoid invalid identifiers from Terraform outputs.

## Work Summary

- Authored PRD-0004 covering Backstage repo structure alignment and pipeline compatibility.
- Updated RDS secret path references to `goldenpath/{env}/{dbname}/postgres` across docs/templates and generator/tests.
- Hardened `rds-allow-delete` identifier resolution to avoid control characters.

## Artifacts Touched (links)

### Modified

- `docs/20-contracts/prds/00_INDEX.md`
- `docs/20-contracts/prds/README.md`
- `scripts/rds_request_parser.py`
- `tests/scripts/test_script_0034.py`
- `docs/85-how-it-works/self-service/BACKEND_APP_RDS_REQUEST_FLOW.md`
- `docs/85-how-it-works/self-service/GOLDEN_PATH_OVERVIEW.md`
- `docs/85-how-it-works/self-service/CONTRACT_DRIVEN_ARCHITECTURE.md`
- `docs/changelog/entries/CL-0162-golden-path-templates.md`
- `session_capture/2026-01-21-scaffold-golden-paths.md`
- `gitops/kustomize/overlays/dev/apps/backstage_db/externalsecrets/RDS-0001.yaml`
- `Makefile`

### Added

- `session_capture/2026-01-22-backstage-repo-structure-and-rds-path-alignment.md`
- `docs/20-contracts/prds/PRD-0004-backstage-repo-structure-alignment.md`

### Referenced / Executed

- `session_capture/session_capture_template.md`

## Validation

- `rg -n "rds/{env}" -S docs session_capture gitops scripts tests` (no matches)
- `pytest -q tests/scripts/test_script_0034.py` (failed: no usable temp directory)

## Current State / Follow-ups

- Re-run `pytest -q tests/scripts/test_script_0034.py` once a writable `TMPDIR` exists.
- Confirm `make rds-allow-delete` now resolves identifiers cleanly in dev.
- Review/approve PRD-0004 and decide on the repo restructure plan.

Signed: Codex (2026-01-22T05:06:54Z)

---

## Updates (append as you go)

### Update - 2026-01-22T05:06:54Z

**What changed**
- Added PRD-0004 for Backstage repo structure alignment and pipeline compatibility.
- Aligned RDS secret path references to the canonical `goldenpath/{env}/{dbname}/postgres`.
- Hardened `rds-allow-delete` to avoid invalid identifiers.

**Artifacts touched**
- `docs/20-contracts/prds/PRD-0004-backstage-repo-structure-alignment.md`
- `docs/20-contracts/prds/00_INDEX.md`
- `docs/20-contracts/prds/README.md`
- `scripts/rds_request_parser.py`
- `tests/scripts/test_script_0034.py`
- `docs/85-how-it-works/self-service/BACKEND_APP_RDS_REQUEST_FLOW.md`
- `docs/85-how-it-works/self-service/GOLDEN_PATH_OVERVIEW.md`
- `docs/85-how-it-works/self-service/CONTRACT_DRIVEN_ARCHITECTURE.md`
- `docs/changelog/entries/CL-0162-golden-path-templates.md`
- `session_capture/2026-01-21-scaffold-golden-paths.md`
- `gitops/kustomize/overlays/dev/apps/backstage_db/externalsecrets/RDS-0001.yaml`
- `Makefile`

**Validation**
- `rg -n "rds/{env}" -S docs session_capture gitops scripts tests` (no matches)
- `pytest -q tests/scripts/test_script_0034.py` (failed: no usable temp directory)

**Next steps**
- Re-run tests once TMPDIR is available.
- Validate `make rds-allow-delete` in dev.

**Outstanding**
- Decide on repo restructure execution plan.
- Confirm automated pipeline compatibility after move.

Signed: Codex (2026-01-22T05:06:54Z)

### Update - 2026-01-22T05:51:14Z

**What changed**
- Documented snapshot collision handling in the RDS break-glass runbook.

**Artifacts touched**
- `docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md`

**Validation**
- Not run (doc update only).

**Next steps**
- Re-run break-glass teardown if needed.

**Outstanding**
- Re-run tests once TMPDIR is available.

Signed: Codex (2026-01-22T05:51:14Z)

### Update - 2026-01-22T14:30:00Z

**What changed**

- Reviewed PRD-0004 and added comprehensive feedback
- Created Definition of Done covering full Backstage ecosystem integration
- Answered open questions (CI guard: yes, TechDocs: defer to docs/)
- Created prompt-templates directory for AI agent implementation prompts
- Added PROMPT-0001 implementation prompt for PRD-0004
- Added PROMPT-0000 template for standardized prompt format
- Added README for prompt-templates directory
- Discussed Helm vs Kustomize trade-offs (staying with Helm)
- Discussed prompt IP and AI auto-execution risks

**Artifacts touched**

- `docs/20-contracts/prds/PRD-0004-backstage-repo-structure-alignment.md` (updated with DoD, feedback)
- `prompt-templates/PROMPT-0000-template.txt` (new)
- `prompt-templates/PROMPT-0001-prd-0004-backstage-repo-alignment.txt` (new)
- `prompt-templates/README.md` (new)

**Validation**

- PRD-0004 includes full Definition of Done checklist
- Prompt template includes warning header to prevent auto-execution

**Next steps**

- Wait for Codex feedback on PRD-0004
- Execute PRD-0004 using PROMPT-0001 when ready
- Review Backstage restructure PR

**Outstanding**

- Backstage repo restructure execution pending approval
- Custom Backstage image build (future work)

Signed: Claude (2026-01-22T14:30:00Z)
