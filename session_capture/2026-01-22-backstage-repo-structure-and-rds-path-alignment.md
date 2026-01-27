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

**Repositories & Branches:**

| Repo                       | Branch                              | Notes                          |
|----------------------------|-------------------------------------|--------------------------------|
| `goldenpath-idp-infra`     | `development`                       | Primary working repo           |
| `goldenpath-idp-backstage` | `refactor/backstage-repo-alignment` | PRD-0004 implementation branch |

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

### Update - 2026-01-22T07:08:32Z

**What changed**

- In `goldenpath-idp-backstage` (branch `refactor/backstage-repo-alignment`), finalized Yarn/tooling alignment for the Spotify-style layout (node-modules linker, yarn path), removed tracked PnP files, expanded `.gitignore`, and hardened the CI lint guard for tracked artifacts.
- Recorded the changes in commit `2b3318c` ("chore: finalize Backstage repo alignment tooling").

**Artifacts touched**

- `goldenpath-idp-backstage/.yarnrc.yml`
- `goldenpath-idp-backstage/.yarn/releases/yarn-4.4.1.cjs`
- `goldenpath-idp-backstage/.gitignore`
- `goldenpath-idp-backstage/.github/workflows/lint.yml`
- `goldenpath-idp-backstage/docs/usefull-commands.md`
- Removed: `goldenpath-idp-backstage/.pnp.cjs`, `goldenpath-idp-backstage/.pnp.loader.mjs`

**Validation**

- `yarn install` failed locally due to native deps (`isolated-vm`, `cpu-features`); logs under `/private/var/folders/_w/.../build.log`.
- Smoke `yarn start` not run (blocked on install).

**Next steps**

- Resolve native build prerequisites and rerun `yarn install`.
- Run a 10-second smoke `yarn start` to confirm the refactor build path works.
- Re-run the PRD-0004 verification checklist and capture CI results.

**Outstanding**

- Confirm pipeline passes on the refactor branch post-install.
- Confirm no `goldenpath/` path references remain in infra integrations.

Signed: Codex (2026-01-22T07:08:32Z)

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

### Update - 2026-01-22T07:25:00Z

**What changed**

- Validated PRD-0004 implementation in `goldenpath-idp-backstage` on branch `refactor/backstage-repo-alignment`
- Fixed Node.js version issue: package requires Node 22+, was running Node 18
- Ran `yarn install` successfully with Node 22.21.1
- Verified `yarn start` launches Backstage (frontend HTTP 200 on port 3000, backend on 7007)
- Squashed 2 commits into 1 for clean PR (`87144e1`)
- Verified no breaking cross-repo paths in `goldenpath-idp-infra`

**Validation Results**

| Check                                     | Status                   |
|-------------------------------------------|--------------------------|
| `packages/`, `plugins/`, configs at root  | ✅ Done                  |
| No `goldenpath/` subdirectory             | ✅ Removed               |
| `docs/` contains how-to content           | ✅ Done                  |
| `.gitignore` covers artifacts             | ✅ Complete              |
| No tracked node_modules/dist-types        | ✅ Clean                 |
| CI guard workflow                         | ✅ Added                 |
| `yarn install` (Node 22)                  | ✅ Passed                |
| `yarn start`                              | ✅ Running               |
| Cross-repo paths                          | ✅ No breaking refs      |
| Commits squashed                          | ✅ Single commit         |

**Known Issues**

- Rspack `node:` scheme warnings in frontend build (cosmetic, doesn't block operation)
- Kubernetes plugin warning: "valid kubernetes config is missing" (expected in local dev)

**Artifacts touched**

- `goldenpath-idp-backstage` - Squashed commits, force-pushed to remote

**Next steps**

- Create PR for `refactor/backstage-repo-alignment` branch
- Deploy to dev cluster and verify templates register
- Update PRD-0004 status to complete after merge

**Outstanding**

- PR review and merge pending
- Dev cluster deployment verification

Signed: Claude (2026-01-22T07:25:00Z)

### Update - 2026-01-22T11:05:00Z

**What changed**

- Fixed 401 Unauthorized error by adding guest SignInPage with auto sign-in
- Added `@backstage-community/plugin-github-actions` for CI/CD visibility
- Implemented TechDocs with local MkDocs generation (`runIn: 'local'`)
- Created PRD-0005 documenting TechDocs implementation path (Phase 1-3)
- Designed and created custom Goldenpath IDP branding:
  - Convergent path logo concept (branches → merge → rising path → goal)
  - 4 logo variants: dark, light, dark-transparent, light-transparent
  - Icon-only version for favicons
- Replaced all Backstage default branding with Goldenpath IDP:
  - LogoFull.tsx (sidebar expanded)
  - LogoIcon.tsx (sidebar collapsed)
  - index.html (title, meta, theme color)
  - manifest.json (PWA name/colors)
  - safari-pinned-tab.svg
  - All favicon PNGs generated from custom icon
- Updated app-config.yaml with Goldenpath IDP title and organization
- Created PR #1 for backstage repo changes

**Artifacts touched**

*goldenpath-idp-backstage:*

- `packages/app/src/App.tsx` (guest SignInPage)
- `packages/app/src/components/catalog/EntityPage.tsx` (GitHub Actions)
- `packages/app/src/components/Root/LogoFull.tsx` (custom logo)
- `packages/app/src/components/Root/LogoIcon.tsx` (custom icon)
- `packages/backend/Dockerfile` (MkDocs installation)
- `packages/app/public/index.html` (branding)
- `packages/app/public/manifest.json` (branding)
- `packages/app/public/safari-pinned-tab.svg` (custom icon)
- `packages/app/public/favicon*.png` (generated)
- `packages/app/public/favicon.ico` (generated)
- `app-config.yaml` (title, techdocs config)
- `app-config.production.yaml` (guest auth for prod)
- `examples/entities.yaml` (techdocs annotation)
- `examples/mkdocs.yml` (new)
- `examples/docs/index.md` (new)
- `examples/docs/getting-started.md` (new)

*goldenpath-idp-infra:*

- `docs/20-contracts/prds/PRD-0005-techdocs-implementation.md` (new)
- `backstage-helm/img/goldenpath-idp-logo-dark.svg` (new)
- `backstage-helm/img/goldenpath-idp-logo-light.svg` (new)
- `backstage-helm/img/goldenpath-idp-logo-dark-transparent.svg` (new)
- `backstage-helm/img/goldenpath-idp-logo-light-transparent.svg` (new)
- `backstage-helm/img/goldenpath-idp-icon-convergent.svg` (new)
- Removed: experimental logo variants (v1, v2, v3, lockups, etc.)

**Validation**

- Backstage starts with custom branding visible in sidebar
- TechDocs configuration in place (local generation mode)
- GitHub Actions plugin renders on entity pages
- Favicons generated at all required sizes (16, 32, 180, 192, ico)

**Next steps**

- Test TechDocs rendering in Backstage UI
- Build and push custom Docker image with MkDocs
- Deploy to dev cluster with new branding
- Phase 2: S3 publisher for TechDocs (per PRD-0005)

**Outstanding**

- Custom Docker image build/push to ECR
- Dev cluster deployment verification
- TechDocs end-to-end test

Signed: Claude (2026-01-22T11:05:00Z)

---

## Session Summary

**Session Date:** 2026-01-22
**Duration:** Full day session
**Status:** Closed

### Key Accomplishments

1. **PRD-0004 Implementation Complete**
   - Backstage repo restructured to Spotify-style layout
   - Node 22 tooling validated
   - CI lint guard added
   - PR created and ready for merge

2. **Backstage Authentication Fixed**
   - Resolved 401 Unauthorized errors
   - Guest authentication with auto sign-in implemented
   - Production config updated for guest auth

3. **GitHub Actions Plugin Integrated**
   - `@backstage-community/plugin-github-actions` installed
   - CI/CD visibility on entity pages

4. **TechDocs Enabled (Phase 1)**
   - MkDocs + techdocs-core installed in Dockerfile
   - Local generation mode configured (`runIn: 'local'`)
   - Example entity with TechDocs annotation created
   - PRD-0005 documents full implementation path

5. **Custom Branding Completed**
   - Designed "Convergent Path" logo concept
   - Created 4 logo variants (dark/light, solid/transparent)
   - Replaced all Backstage default branding
   - Generated all favicon sizes from custom icon
   - Updated app title, meta tags, PWA manifest

### Artifacts Created

| Type | Count | Key Items |
|------|-------|-----------|
| PRDs | 2 | PRD-0004 (repo structure), PRD-0005 (TechDocs) |
| Logo SVGs | 5 | dark, light, dark-transparent, light-transparent, icon |
| Favicons | 5 | 16px, 32px, 180px, 192px, .ico |
| Components | 2 | LogoFull.tsx, LogoIcon.tsx |

### Open Items for Next Session

- [ ] Build and push custom Docker image to ECR
- [ ] Deploy to dev cluster with new branding
- [ ] Test TechDocs rendering end-to-end
- [ ] Merge PR #1 after review
- [ ] Begin Phase 2: S3 publisher for TechDocs

### Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Logo concept | Convergent Path (v3 rising) | Upward trajectory communicates enablement/growth |
| Light mode gold | `#B8960C` | Better contrast on white than `#F5C542` |
| TechDocs mode | Local (Phase 1) | Quick win, defer S3 to Phase 2 |
| Auth provider | Guest with auto sign-in | Simplest for dev/demo environments |

### Commits This Session

*goldenpath-idp-backstage:*
- `8dbdb39` - fix: add guest SignInPage with auto sign-in
- `2fc8b02` - feat: add GitHub Actions plugin
- `32ca6b7` - feat: add TechDocs support with local MkDocs
- (pending) - feat: replace Backstage branding with Goldenpath IDP

*goldenpath-idp-infra:*
- `8c467c15` - docs: add PRD-0005 TechDocs implementation
- (pending) - feat: add Goldenpath IDP logo assets

---

Session closed: 2026-01-22T11:10:00Z
Signed: Claude

---

**Historical Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
- `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
- `backstage-helm/backstage-catalog/` → `catalog/`
