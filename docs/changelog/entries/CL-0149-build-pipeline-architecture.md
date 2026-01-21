---
id: CL-0149
title: Build Pipeline Architecture and Governance
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0170
  - GOV-0012
  - GOV-0012-build-pipeline-standards
  - session-2026-01-19-build-pipeline-architecture
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-19
author: platform-team
breaking_change: false
---

# CL-0149: Build Pipeline Architecture and Governance

## Summary

Established canonical build pipeline architecture with multi-repo strategy, tagging conventions, and security gate policies.

## Changes

### Added

- ADR-0170: Build Pipeline Architecture and Multi-Repo Strategy
- GOV-0012: Build Pipeline Standards governance document
- Consolidated governance matrix for tagging, auth, and security gates
- Session capture documenting design decisions and agent collaboration

### Decisions Made

| Decision | Details |
|----------|---------|
| Tagging (local/dev) | `:latest` with digest strategy |
| Tagging (test/staging/prod) | `<env>-<sha>` immutable tags |
| Authentication | GitHub App for git write-back |
| Security gates | Blocking for test/staging/prod |
| Concurrency | Parallel builds, serialized deploys per env |

### Governance Matrix

| Environment | Tag Format | Security Gate | Approval |
|-------------|------------|---------------|----------|
| local | `:latest` | Advisory | No |
| dev | `:latest` | Advisory | No |
| test | `test-<sha>` | Blocking | No |
| staging | `staging-<sha>` | Blocking | Optional |
| prod | `prod-<sha>` | Blocking | Required |

## Impact

- All new application repos must use the canonical reusable workflow
- Security scans become blocking for non-dev environments
- Bootstrap requires GitHub App setup
- Existing `hello-goldenpath-idp` workflow will be refactored in Phase 1

## Migration

No immediate migration required. Implementation will occur in phases:

1. **Phase 1**: Create canonical workflow, refactor hello-goldenpath-idp
2. **Phase 2**: GitHub App setup, promotion workflow
3. **Phase 3**: Documentation and templates
4. **Phase 4** (V1.1): SBOM, signing, rollback playbook

## Files Added

- `docs/adrs/ADR-0170-build-pipeline-architecture.md`
- `docs/10-governance/policies/GOV-0012-build-pipeline-standards.md`
- `docs/changelog/entries/CL-0149-build-pipeline-architecture.md`
- `session_capture/2026-01-19-build-pipeline-architecture.md`

## Related

- ADR-0170: Build Pipeline Architecture
- GOV-0012: Build Pipeline Standards
- Session: 2026-01-19-build-pipeline-architecture

Signed: platform-team (2026-01-19)
