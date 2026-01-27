---
id: 2026-01-22-argocd-plugin-integration
title: ArgoCD Backstage Plugin Integration
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
  - CL-0164-argocd-backstage-plugin
  - ADR-0171-platform-application-packaging-strategy
  - ADR-0172-cd-promotion-strategy-with-approval-gates
---
# Session Capture: ArgoCD Backstage Plugin Integration

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-22
**Timestamp:** 2026-01-22T15:00:00Z
**Branch:** development (goldenpath-idp-infra), refactor/backstage-repo-alignment (goldenpath-idp-backstage)

## Scope

* Research and evaluate ArgoCD Backstage plugin options
* Integrate chosen plugin with Backstage frontend and backend
* Configure ArgoCD connection settings for local and production
* Update Golden Path scaffold templates with DRY annotations
* Document plugin selection rationale in changelog

## Work Summary

* Researched three ArgoCD plugin options: Roadie, Red Hat, and Janus IDP
* Selected Roadie plugin for standalone architecture and maturity
* Installed frontend plugin `@roadiehq/backstage-plugin-argo-cd`
* Installed backend plugin `@roadiehq/backstage-plugin-argo-cd-backend`
* Added ArgoCD overview card to entity pages (conditional on annotation)
* Added ArgoCD history tab for service/website entities
* Configured app-config.yaml and app-config.production.yaml
* Added ArgoCD environment variables to docker-compose.yml
* Updated all 3 Golden Path scaffold templates with DRY annotations
* Created changelog entry CL-0164 with selection rationale
* Created PR #3 for goldenpath-idp-backstage

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Backend crash on startup | Missing ARGOCD_URL environment variable | Added placeholder env vars to docker-compose.yml |
| Plugin not visible on entities | Missing argocd/app-name annotation | Updated scaffold templates with DRY annotations |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ArgoCD plugin vendor | Roadie | Standalone architecture (no K8s plugin dependency), 3+ years maturity, ~15k weekly npm downloads vs ~2k for Red Hat |
| Annotation strategy | DRY via scaffold templates | New services auto-inherit annotations without manual configuration |
| ArgoCD instance name | "dev" | Matches environment naming convention |
| Token auth vs password | Token-based | More secure, recommended for production |

## Artifacts Touched (links)

### Modified

*goldenpath-idp-backstage:*
* `packages/app/src/components/catalog/EntityPage.tsx` - ArgoCD components
* `packages/backend/src/index.ts` - Backend plugin registration
* `packages/app/package.json` - Frontend plugin dependency
* `packages/backend/package.json` - Backend plugin dependency
* `yarn.lock` - Dependency lockfile
* `app-config.yaml` - ArgoCD configuration
* `app-config.production.yaml` - Production ArgoCD config with token auth
* `docker-compose.yml` - ArgoCD environment variables

*goldenpath-idp-infra:*
* `backstage-helm/backstage-catalog/templates/stateless-app/skeleton/catalog-info.yaml` - ArgoCD/K8s annotations
* `backstage-helm/backstage-catalog/templates/stateful-app/skeleton/catalog-info.yaml` - ArgoCD/K8s annotations
* `backstage-helm/backstage-catalog/templates/backend-app-rds/skeleton/catalog-info.yaml` - ArgoCD/K8s annotations

### Added

*goldenpath-idp-infra:*
* `docs/changelog/entries/CL-0164-argocd-backstage-plugin.md` - Changelog with rationale

### Referenced / Executed

* `yarn add @roadiehq/backstage-plugin-argo-cd` (frontend)
* `yarn add @roadiehq/backstage-plugin-argo-cd-backend` (backend)
* `docker-compose up -d` (local testing)
* `git commit` / `git push` (both repos)
* `gh pr create` (PR #3)

## Validation

* `docker-compose up -d` (backstage-app running on localhost:7007)
* `git push` (both repos pushed successfully)
* `gh pr create` (PR #3 created: <https://github.com/mikeybeezy/goldenpath-idp-backstage/pull/3>)

## Current State / Follow-ups

* ArgoCD plugin integrated and running locally
* Scaffold templates updated with DRY annotations
* PR #3 ready for review and merge
* Next: Test with real ArgoCD instance in cluster
* Next: Deploy updated Backstage image to dev environment
* Next: Verify ArgoCD tab appears for annotated components in cluster

Signed: Claude Opus 4.5 (2026-01-22T15:30:00Z)

---

## Updates (append as you go)

### Update - 2026-01-22T15:30:00Z

**What changed**
* Completed all ArgoCD plugin integration work
* All three scaffold templates updated
* Both repos committed and pushed
* PR #3 created for backstage repo

**Artifacts touched**
* All files listed above

**Validation**
* `git status` - Clean working directory in both repos
* `gh pr view 3` - PR created and ready for review

**Next steps**
* Merge PR #3 after CI passes
* Build new Docker image with ArgoCD plugin
* Deploy to dev cluster
* Test ArgoCD integration end-to-end

**Outstanding**
* PR #3 needs review and merge
* Docker image needs rebuild with ArgoCD plugin
* End-to-end testing with real ArgoCD required

Signed: Claude Opus 4.5 (2026-01-22T15:30:00Z)

---

## Plugin Comparison Summary

| Feature | Roadie | Red Hat | Janus IDP |
|---------|--------|---------|-----------|
| Architecture | Standalone | K8s plugin dependent | K8s plugin dependent |
| Maturity | 3+ years | ~1 year | ~2 years |
| Weekly Downloads | ~15,000 | ~2,000 | N/A |
| Setup Complexity | Low | Medium | Medium |
| Documentation | Excellent | Good | Good |
| Community Support | Strong | Growing | Growing |

**Decision**: Roadie selected for standalone architecture and proven stability.

---

**Historical Note (2026-01-26):** References to `backstage-helm/` paths in this document are historical. Per CL-0196, the directory structure was consolidated:
* `backstage-helm/charts/backstage/` → `gitops/helm/backstage/chart/`
* `backstage-helm/backstage-catalog/` → `catalog/`
