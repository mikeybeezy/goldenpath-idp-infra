---
id: PHASE1_CICD_IMPLEMENTATION_STRATEGY
title: Phase 1 CI/CD Implementation Strategy
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
relates_to:
  - GOV-0014-devsecops-implementation-matrix
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - _build-and-release.yml
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Phase 1 CI/CD Implementation Strategy

**Status:** In Progress (~85% Complete)
**Owner:** platform-team
**Target:** Q1 2026
**Reference:** [GOV-0014](../10-governance/policies/GOV-0014-devsecops-implementation-matrix.md)

---

## Executive Summary

Phase 1 establishes the foundational CI/CD pipeline with security scanning, artifact generation, and standardized workflows. This document provides the implementation strategy to complete the remaining ~15% of Phase 1.

---

## Current State Assessment

### Implemented (Done)

| Component | Workflow/Script | Evidence |
|-----------|-----------------|----------|
| Canonical workflow | `_build-and-release.yml` | Deployed, tested |
| Trivy blocking gates | `_build-and-release.yml:339` | EXIT_CODE=1 for test/staging/prod |
| SARIF upload | `_build-and-release.yml:350` | Uploads to GitHub Security tab |
| SBOM generation | `_build-and-release.yml` (Syft) | Artifact upload configured |
| Gitleaks CI | `gitleaks.yml` + `_build-and-release.yml:119` | PR check + build job |
| Pre-commit config | `.pre-commit-config.yaml` | Template available |
| Concurrency groups | `_build-and-release.yml` | `deploy-${{ env }}` groups |

### Remaining (Gap)

| Component | Gap Description | Effort |
|-----------|-----------------|--------|
| Thin caller workflow | ~~No `delivery.yml` template for app repos~~ **DONE** | S |
| hello-goldenpath-idp | Sample app not using canonical workflow | M |
| Phase 1 status update | GOV-0014 checkboxes still show "Pending" | S |

### Consolidation Note

The `_build-and-release.yml` workflow contains **inline** docker build/push logic with full security scanning (Trivy, SBOM, Gitleaks). The standalone `ecr-build-push.sh` script is **deprecated for CI use** - it duplicates functionality without the security gates. Retained only for local development scenarios.

---

## Implementation Tasks

### Task 1: Create Thin Caller Workflow Template (DONE)

**Objective:** Provide a minimal `delivery.yml` that app repos use to call the canonical workflow.

**Acceptance Criteria:**
- [ ] Template exists at `docs/templates/delivery.yml`
- [ ] Calls `_build-and-release.yml` via `workflow_call`
- [ ] Passes required inputs (environment, ecr_repository, etc.)
- [ ] Documented in onboarding guide

**Template:**
```yaml
# .github/workflows/delivery.yml (app repo)
name: Delivery Pipeline

on:
  push:
    branches: [main, development]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'dev'
        type: choice
        options: [dev, test, staging, prod]

jobs:
  build-and-release:
    uses: mikeybeezy/goldenpath-idp-infra/.github/workflows/_build-and-release.yml@main
    with:
      environment: ${{ github.event.inputs.environment || 'dev' }}
      ecr_repository: ${{ github.event.repository.name }}
      build_context: '.'
      dockerfile_path: './Dockerfile'
    secrets: inherit
```

**Definition of Done:**

- [x] Template file created (`docs/templates/workflows/delivery.yml`)
- [ ] README updated with usage instructions
- [ ] Scaffolder template updated to include `delivery.yml`

---

### Task 2: Onboard hello-goldenpath-idp to Canonical Workflow

**Objective:** Demonstrate the canonical workflow with a real sample application.

**Acceptance Criteria:**
- [ ] `hello-goldenpath-idp` repo uses thin caller workflow
- [ ] CI runs successfully on push to development
- [ ] Image appears in ECR with correct tags
- [ ] Trivy scan passes (or documents known vulnerabilities)
- [ ] SBOM artifact attached to workflow run

**Steps:**
1. Create `hello-goldenpath-idp` repo (if not exists)
2. Add minimal Dockerfile (alpine + hello world)
3. Add `delivery.yml` thin caller
4. Push to development branch
5. Verify CI completes successfully
6. Document in session capture

**Definition of Done:**
- Workflow run link showing green checks
- ECR image visible in console
- SBOM artifact downloadable from GitHub Actions

---

### Task 3: Update GOV-0014 Status

**Objective:** Mark Phase 1 items as complete with evidence links.

**Acceptance Criteria:**
- [ ] All Phase 1 items in GOV-0014 marked complete
- [ ] Evidence links added (workflow files, PRs, ECR)
- [ ] Phase 1 completion date recorded

**Changes to GOV-0014:**
```markdown
### 9.1 Phase 1 Complete When

- [x] Canonical workflow deployed and tested
      Evidence: `.github/workflows/_build-and-release.yml`
- [x] Trivy blocking gates active for test/staging/prod
      Evidence: `_build-and-release.yml:345`
- [x] SARIF uploads to GitHub Security tab
      Evidence: `_build-and-release.yml:350`
- [x] SBOM generated for every build
      Evidence: Syft step in canonical workflow
- [x] Gitleaks in PR checks
      Evidence: `gitleaks.yml`
- [x] Pre-commit template available
      Evidence: `.pre-commit-config.yaml`
- [x] `hello-goldenpath-idp` using thin caller
      Evidence: <link to repo workflow run>
```

---

## Execution Order

```
Completed:
└── Task 1: Create thin caller template (DONE)

Remaining:
├── Task 2: Onboard hello-goldenpath-idp (2-4 hours)
└── Task 3: Update GOV-0014 status (30 min)
```

---

## Dependencies

| Dependency | Status | Blocker? |
|------------|--------|----------|
| AWS OIDC provider configured | Done | No |
| ECR repository exists | Done | No |
| GitHub Actions runners available | Done | No |
| Trivy action version pinned | Done | No |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OIDC auth fails in CI | High | Test locally first with `aws sts get-caller-identity` |
| Trivy blocks on false positive | Medium | Use `.trivyignore` for known non-issues |
| Sample app has vulnerabilities | Low | Use minimal base image (distroless/alpine) |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Phase 1 completion | 100% | GOV-0014 checkboxes |
| Sample app CI green | 1 successful run | GitHub Actions |
| ECR image pushed | 1 image with dual tags | AWS Console |
| SBOM artifact present | 1 per build | GitHub Actions artifacts |

---

## Phase 1 → Phase 2 Handoff

Once Phase 1 is complete:

1. **Create Phase 2 kickoff ADR** - GitHub App authentication strategy
2. **Update ROADMAP.md** - Move Phase 1 items to "Done"
3. **Schedule Phase 2 planning** - Auth & Promotion scope

---

## Changelog

| Date       | Change                                                                    | Author        |
|------------|---------------------------------------------------------------------------|---------------|
| 2026-02-01 | Removed ecr-build-push.sh task (consolidated into _build-and-release.yml) | platform-team |
| 2026-02-01 | Initial version                                                           | platform-team |

---

## Related Documents

- [GOV-0014: DevSecOps Implementation Matrix](../10-governance/policies/GOV-0014-devsecops-implementation-matrix.md)
- [ADR-0100: Standardized ECR Lifecycle](../adrs/ADR-0100-standardized-ecr-lifecycle-and-documentation.md)
- [ADR-0174: Pipeline Decoupling](../adrs/ADR-0174-pipeline-decoupling-from-cluster-bootstrap.md)
