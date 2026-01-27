---
id: PRD-0004-backstage-repo-structure-alignment
title: 'PRD-0004: Backstage Repo Structure Alignment (Spotify-style)'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_PRDS_README
  - PRD-0003-backstage-plugin-scaffold
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0004: Backstage Repo Structure Alignment (Spotify-style)

Status: draft
Owner: platform-team
Date: 2026-01-22

## Problem Statement

The Backstage repository at `/Users/mikesablaze/Documents/relaunch/goldenpath-idp-backstage`
does not follow a standard Backstage repo layout. The app lives under a nested
`goldenpath/` directory, documentation sits in a separate `how-to/` folder, and
build artifacts (for example `node_modules/` and `dist-types/`) are present in
version control. This increases onboarding friction, breaks expected tooling
assumptions, and complicates integration with platform automation.

## Goals

- Align the repo structure to the common Backstage (Spotify-style) layout.
- Make the root of the repo the Backstage app root (packages, plugins, configs).
- Remove tracked build artifacts and prevent reintroduction.
- Consolidate documentation into a standard `docs/` location.

## Non-Goals

- Re-platform or rewrite Backstage plugins.
- Change product behavior, UI, or runtime configuration beyond path updates.
- Introduce new CI/CD workflows outside what is needed to keep builds working.

## Scope

- Repo: `goldenpath-idp-backstage`
- Structure and documentation layout
- Repository hygiene for tracked artifacts

## Requirements

### Functional

- `packages/` and `plugins/` live at repo root.
- `app-config.yaml`, `catalog-info.yaml`, and `backstage.json` live at repo root.
- A `docs/` directory exists and absorbs `how-to/` content.
- No tracked build artifacts remain in Git history for new commits.
- Repo structure remains compatible with the main build pipeline workflow.

### Non-Functional

- `yarn start` works from repo root without path adjustments.
- CI (if present) continues to work after path updates.
- Changes are reversible via git revert.

## Proposed Approach (High-Level)

- Move contents of `goldenpath/` to the repo root.
- Move `how-to/` into `docs/` and update references.
- Remove tracked artifacts (`node_modules/`, `dist-types/`, `.DS_Store`,
  `.yarn/install-state.gz`) and ensure `.gitignore` is enforced at repo root.
- Update any scripts or docs that reference the old `goldenpath/` path.
- Add a lightweight guard (lint or CI check) to prevent committing build outputs.

## Guardrails

- No secret files or environment overrides are added during the restructure.
- Only structure and documentation changes are allowed in this initiative.
- Use explicit approvals for any CI changes.

## Observability / Audit

- Git history for the restructure commit.
- Build logs showing successful `yarn start` from repo root.

## Acceptance Criteria

- `packages/`, `plugins/`, and config files are at repo root.
- Running `yarn start` from root starts Backstage without path tweaks.
- `git status` shows no tracked build artifacts.
- Docs are discoverable under `docs/` and referenced from a root README.
- Main build pipeline passes on the restructured repo.

## Success Metrics

- New developer can run Backstage locally in under 15 minutes.
- Repo tree matches standard Backstage scaffold expectations.
- Zero repeat commits that reintroduce tracked build artifacts.

## Open Questions

- Do we want a CI guard that blocks any `node_modules/` or `dist-types/` changes?
- Should `how-to/` be merged into TechDocs instead of a `docs/` folder?

## References

- `docs/20-contracts/prds/PRD-0003-backstage-plugin-scaffold.md`
- `/Users/mikesablaze/Documents/relaunch/goldenpath-idp-backstage`

### Related Backstage Assets in goldenpath-idp-infra

- `catalog/` - Catalog entities and templates
- `catalog/templates/stateless-app/` - Stateless app Golden Path
- `catalog/templates/stateful-app/` - Stateful app Golden Path
- `catalog/templates/backend-app-rds/` - Backend + RDS Golden Path
- `gitops/helm/backstage/chart/` - Helm chart for deployment
- `gitops/helm/backstage/values/dev.yaml` - Dev environment values
- `gitops/argocd/applications/backstage.yaml` - ArgoCD application
- `docs/changelog/entries/CL-0162-golden-path-templates.md` - Golden Path changelog

---

## Implementation Tasks

- [ ] Create feature branch `refactor/backstage-repo-alignment`
- [ ] Move `goldenpath/*` to repo root
- [ ] Move `how-to/` to `docs/`
- [ ] Update `.gitignore` at root
- [ ] Remove tracked artifacts from git (`git rm --cached`)
- [ ] Update any path references in scripts/configs
- [ ] Add CI guard for build artifacts
- [ ] Test `yarn start` from root
- [ ] Create PR and get approval

---

## Comments and Feedback
When providing feedback, leave a comment and timestamp your comment.

- **Claude / 2026-01-22**: Review feedback below.

### Open Questions Resolution

**Q1: CI guard for `node_modules/` / `dist-types/`?**

- **Recommendation: Yes.** Add a simple CI check. Low effort, prevents recurrence.

```yaml
# .github/workflows/lint.yml
- name: Check for tracked artifacts
  run: |
    if git ls-files | grep -E 'node_modules/|dist-types/'; then
      echo "ERROR: Build artifacts should not be tracked"
      exit 1
    fi
```

**Q2: Merge `how-to/` into TechDocs instead of `docs/`?**

- **Decision: Use `docs/` for now.** TechDocs requires additional setup (mkdocs.yml, CI publishing). Keep it simple. TechDocs migration is deferred to the roadmap.

### Additional Recommendations

| Gap | Suggestion |
| --- | ---------- |
| **Migration steps** | Add explicit commands (git mv, rm, etc.) to avoid ambiguity |
| **Rollback plan** | Clarify commit strategy: single squash commit recommended for clean revert |
| **Branch strategy** | Use feature branch with PR, not direct to main |
| **Downstream impact** | Verify nothing in `goldenpath-idp-infra` references old paths (CI workflows, ArgoCD apps) |

### Artifact Handling Clarification

The PRD says "No tracked build artifacts remain in Git history for new commits" - clarify:
- **Recommended: Option A** - Use `git rm --cached` (artifacts gone from working tree, still in old history)
- History rewrite with `git filter-branch` or BFG is overkill for this

### Additional Success Metric

Add: "CI pipeline passes on restructured repo within first PR"

---

## Definition of Done

### Code & Structure

- [ ] `packages/`, `plugins/`, and `app-config.yaml` exist at repo root
- [ ] No `goldenpath/` subdirectory remains (contents moved)
- [ ] `docs/` directory contains all content from `how-to/`
- [ ] `.gitignore` at root includes `node_modules/`, `dist-types/`, `.DS_Store`, `.yarn/install-state.gz`
- [ ] `git ls-files | grep -E 'node_modules|dist-types'` returns empty

### Functional Verification

- [ ] `yarn install` succeeds from repo root
- [ ] `yarn start` launches Backstage from repo root
- [ ] `yarn build` completes without errors
- [ ] App loads in browser at `localhost:3000`

### Integration with goldenpath-idp-infra

- [ ] **Catalog Location** - `catalog/all.yaml` resolves correctly
- [ ] **Templates** - Golden Path templates register in Backstage:
  - `stateless-app/template.yaml`
  - `stateful-app/template.yaml`
  - `backend-app-rds/template.yaml`
- [ ] **Scaffolder Actions** - Custom actions work (`fetch:plain`, `publish:github:pull-request`, `github:actions:dispatch`)
- [ ] **Helm Chart** - `gitops/helm/backstage/chart` values paths are compatible
- [ ] **ArgoCD App** - Multi-source app in `gitops/argocd/applications/backstage.yaml` still syncs

### Backstage Runtime Verification

- [ ] Catalog loads entities from `goldenpath-idp-infra` repo
- [ ] Software Templates appear in "Create" menu
- [ ] Template parameters render correctly
- [ ] Scaffolder can execute a dry-run of each template
- [ ] GitHub integration (token) works for PR creation

### Custom Image Build Path

- [ ] `Dockerfile` (if present) builds from new root structure
- [ ] ECR push workflow (if present) still works
- [ ] Image tag strategy documented for custom builds

### Configuration Compatibility

- [ ] `app-config.yaml` references correct catalog URLs
- [ ] `app-config.production.yaml` (if exists) paths updated
- [ ] Environment variable substitutions (`${CATALOG_LOCATION}`, etc.) still resolve

### Cross-Repo Dependencies

| Repo | Check |
| --- | ---------- |
| `goldenpath-idp-infra` | No hardcoded `goldenpath/` paths in workflows or configs |
| `hello-goldenpath-idp` | Scaffolded app template paths still valid |
| ArgoCD | Backstage app source refs unchanged |

### CI/CD

- [ ] CI pipeline passes on PR
- [ ] Artifact guard check added (blocks `node_modules/`/`dist-types/` commits)
- [ ] No broken references to old `goldenpath/` paths in workflows

### Documentation

- [ ] Root `README.md` updated with correct paths and quickstart
- [ ] All internal doc links reference `docs/` (not `how-to/`)
- [ ] `catalog-info.yaml` paths are correct
- [ ] Template authoring guide updated (if paths changed)
- [ ] Links from `goldenpath-idp-infra` docs to Backstage repo updated

### Review & Merge

- [ ] PR created from feature branch
- [ ] At least one approval received
- [ ] PR squash-merged for clean revert capability
- [ ] No downstream breakage in `goldenpath-idp-infra` (verified)

### Post-Merge

- [ ] PRD-0004 status updated to `complete`
- [ ] Changelog entry created (CL-0163 or next available)
- [ ] Backstage deployed to dev cluster and verified working
