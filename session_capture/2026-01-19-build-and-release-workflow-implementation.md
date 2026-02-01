---
id: 2026-01-19-build-and-release-workflow-implementation
title: Build and Release Canonical Workflow Implementation
type: session-capture
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
  - session-2026-01-19-build-pipeline-architecture
  - GOV-0012-build-pipeline-standards
  - GOV-0014-devsecops-implementation-matrix
  - ADR-0170-build-pipeline-architecture
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - CL-0149-build-pipeline-architecture
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Session Capture: Build and Release Canonical Workflow Implementation

## Session Metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-19
**Timestamp:** 2026-01-19T23:00:00Z
**Branch:** goldenpath/buildpipeline
**Commit:** cbf1288912fafa58fd1c34ac490c8d850faad67c

## Scope

- Implement canonical `_build-and-release.yml` reusable workflow
- Add security scanning gates (Gitleaks, Trivy)
- Implement SBOM generation with Syft
- Configure environment-aware security enforcement
- Create promotion and deploy workflow stubs

## Context

This session followed the architecture design session (2026-01-19-build-pipeline-architecture) which defined the multi-repo strategy and reusable workflow pattern. This implementation session created the actual workflow files per GOV-0012 and GOV-0014 Phase 1 requirements.

## Work Summary

### 1. Canonical Build Workflow (`_build-and-release.yml`)

Created 427-line reusable workflow with:

| Component | Implementation | Line Reference |
|-----------|----------------|----------------|
| **Gitleaks** | `gitleaks/gitleaks-action@v2` | Job: `gitleaks` |
| **Trivy** | `aquasecurity/trivy-action@0.28.0` | Step: `Scan image with Trivy` |
| **SBOM** | Syft via Trivy integration | Artifact upload |
| **SARIF** | `github/codeql-action/upload-sarif@v3` | Step: `Upload Trivy scan results` |

### 2. Environment-Aware Security Gates

| Environment | Gitleaks | Trivy | SARIF Upload |
|-------------|----------|-------|--------------|
| local/dev | Advisory | Advisory (exit-code: 0) | No |
| test/staging/prod | Blocking | Blocking (exit-code: 1) | Yes |

### 3. Workflow Inputs

```yaml
inputs:
  environment:
    description: 'Target environment'
    required: true
    type: string
  ecr_repository:
    description: 'ECR repository name'
    required: true
    type: string
  build_context:
    description: 'Docker build context'
    default: '.'
  dockerfile_path:
    description: 'Path to Dockerfile'
    default: './Dockerfile'
  test_enabled:
    description: 'Run tests before build'
    default: true
  test_command:
    description: 'Test command to run'
    default: ''
  trivy_exit_code:
    description: 'Override Trivy exit code'
    required: false
```

### 4. Job Flow

```
gitleaks (secrets) ──┐
                     ├──> build ──> [success summary]
test (optional) ─────┘
```

### 5. Additional Workflows Created

| Workflow | Purpose | Status |
|----------|---------|--------|
| `_promote.yml` | Image promotion between environments | Stub |
| `_deploy.yml` | Deployment to target environment | Placeholder |

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Action version pinning | Security best practice per GOV-0012 | Pinned Trivy to @0.28.0, no @master/@latest |
| SARIF upload permissions | Requires security-events: write | Added to permissions block |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trivy version pinning | @0.28.0 | GOV-0012 prohibits @master/@latest |
| SBOM format | SPDX via Syft | Industry standard, GitHub dependency graph compatible |
| Gate mode detection | Environment-based | Simple, predictable, matches promotion flow |
| Test job dependency | Parallel with Gitleaks | Tests don't need secrets scan to start |

## Artifacts Touched

### Added

- `.github/workflows/_build-and-release.yml` - Canonical build workflow (427 lines)
- `.github/workflows/_promote.yml` - Image promotion workflow (258 lines)
- `.github/workflows/_deploy.yml` - Deployment workflow placeholder (151 lines)

### Referenced

- `docs/10-governance/policies/GOV-0012-build-pipeline-standards.md`
- `docs/10-governance/policies/GOV-0014-devsecops-implementation-matrix.md`
- `docs/adrs/ADR-0170-build-pipeline-architecture.md`

## Validation

- Workflow syntax validated via GitHub Actions linter
- Environment gate logic tested with different input combinations
- SARIF upload format verified against GitHub Security requirements

## Phase 1 Completion Status

| GOV-0014 Phase 1 Item | Status | Evidence |
|-----------------------|--------|----------|
| Canonical workflow deployed | Done | `_build-and-release.yml` |
| Trivy blocking gates | Done | `exit-code: 1` for test+ |
| SARIF upload | Done | `upload-sarif` step |
| SBOM generation | Done | Syft integration |
| Gitleaks CI | Done | `gitleaks` job |
| Pre-commit config | Done | `.pre-commit-config.yaml` |
| Thin caller template | Pending | Needs `delivery.yml` template |

## Current State / Follow-ups

- **Done:** Core workflow implementation complete
- **Pending:** Create thin caller template for app repos
- **Pending:** Onboard `hello-goldenpath-idp` to use canonical workflow
- **Pending:** Update GOV-0014 checkboxes with evidence links

## Related Documents

- [Session: Build Pipeline Architecture](./2026-01-19-build-pipeline-architecture.md)
- [CL-0149: Build Pipeline Architecture](../docs/changelog/entries/CL-0149-build-pipeline-architecture.md)
- [GOV-0014: DevSecOps Implementation Matrix](../docs/10-governance/policies/GOV-0014-devsecops-implementation-matrix.md)

---

Signed: Claude Opus 4.5 (2026-01-19T23:00:00Z)

**Note:** This session capture was created retroactively on 2026-02-01 to document the implementation work that occurred on 2026-01-19. The gap was identified during Phase 1 coherence review.
