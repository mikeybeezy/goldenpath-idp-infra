---
id: ADR-0188
title: Phase 2 GitHub App Authentication Strategy
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0170-build-pipeline-architecture
  - GOV-0012-build-pipeline-standards
  - GOV-0013-devsecops-security-standards
  - GOV-0014-devsecops-implementation-matrix
  - _build-and-release.yml
  - ROADMAP
  - session-2026-02-01-phase1-cicd-consolidation
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-02-01'
date: 2026-02-01
deciders: platform-team
consulted: Claude Opus 4.5
informed: dev-teams
---

# ADR-0188: Phase 2 GitHub App Authentication Strategy

## Status

Proposed

## Context

Phase 1 of the CI/CD pipeline implementation is complete. The canonical `_build-and-release.yml` workflow is now the single source of truth for all CI/CD operations, providing:

- Gitleaks secret scanning (environment-aware gating)
- Trivy container vulnerability scanning with SARIF upload
- Syft SBOM generation
- Environment-aware security gates (advisory for local/dev, blocking for test/staging/prod)

The next evolution requires **GitHub App authentication** to enable:

1. **Git write-back** - Automated commits for version bumps, SBOM attestations, and GitOps manifests
2. **Cross-repo operations** - Trigger workflows in app repos from infra changes
3. **Audit trail** - Rich, queryable audit logs vs. anonymous PAT commits
4. **Token rotation** - 1-hour auto-expiring tokens vs. long-lived secrets

Currently, workflows use GITHUB_TOKEN (limited to current repo) or manually rotated PATs (no audit trail, manual rotation burden).

## Decision

### GitHub App Strategy

Create a dedicated **GoldenPath IDP Bot** GitHub App with:

| Permission | Scope | Justification |
|------------|-------|---------------|
| Contents | Read/Write | Git push for version bumps, SBOM commits |
| Pull Requests | Read/Write | Auto-create PRs for promotions |
| Actions | Read | Trigger workflow_dispatch events |
| Metadata | Read | Repository discovery |

### Installation Scope

- **Organization-wide** installation (not per-repo)
- Explicit repo list to start (infra + app repos)
- Expand as repos are onboarded via scaffolder

### Token Flow

```
Workflow starts
    │
    ▼
Generate installation token (1-hour TTL)
    │
    ▼
Configure git with App identity
    │
    ▼
Perform write operations
    │
    ▼
Token expires automatically
```

### Credential Storage

| Environment | Storage | Access |
|-------------|---------|--------|
| GitHub Actions | GitHub Secrets (org-level) | Workflow reference |
| Local Dev | N/A | Use personal PAT or no write-back |

Secrets required:
- `GOLDENPATH_APP_ID` - GitHub App ID
- `GOLDENPATH_APP_PRIVATE_KEY` - PEM-encoded private key

### Phase 2 Implementation Milestones

| Milestone | Description | Evidence |
|-----------|-------------|----------|
| M2.1 | Create GitHub App in org settings | App ID documented |
| M2.2 | Install App on goldenpath-idp-infra | Installation ID captured |
| M2.3 | Store credentials in org secrets | Secret names visible |
| M2.4 | Add token generation step to canonical workflow | Workflow update committed |
| M2.5 | Test git write-back in dev environment | Commit with App signature |
| M2.6 | Document onboarding for new repos | Guide published |

### Git Commit Identity

Commits made by the App will use:

```
Author: goldenpath-idp-bot[bot] <123456+goldenpath-idp-bot[bot]@users.noreply.github.com>
Committer: GitHub <noreply@github.com>
```

This provides clear audit trail distinguishing automation from human commits.

## Consequences

### Positive

- **Audit trail**: All automated commits traceable to App, not anonymous PAT
- **Auto-rotation**: No manual secret rotation; tokens expire in 1 hour
- **Cross-repo**: Single App can operate across all org repos
- **Granular permissions**: Least-privilege scoping vs. PAT with broad access
- **Compliance**: Meets SOC2/ISO requirements for service account identity

### Negative

- **Setup overhead**: ~1 hour one-time setup for App creation and installation
- **Key management**: Private key must be protected (org secret, not repo secret)
- **Debugging**: App actions appear as bot user, may require log correlation

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Private key compromise | Low | High | Store in GitHub org secrets; rotate immediately on suspicion |
| App rate limiting | Low | Medium | Use caching for token generation; batch operations |
| App deleted accidentally | Low | High | Document App config; IaC for recreation |

## Alternatives Considered

### Personal Access Tokens (PATs)

- Pros: Simple setup, familiar pattern
- Cons: Manual rotation, no audit trail, tied to human account
- Rejected: Doesn't meet compliance requirements for service identity

### Deploy Keys

- Pros: Scoped to single repo, SSH-based
- Cons: One key per repo, no cross-repo capability, manual rotation
- Rejected: Doesn't scale for multi-repo platform

### Machine User Account

- Pros: GitHub's legacy pattern for bots
- Cons: Consumes license seat, requires manual management, deprecated pattern
- Rejected: GitHub Apps are the modern replacement

## Implementation Prerequisites

Before starting Phase 2:

1. **Org admin access** - Required to create GitHub App
2. **Secrets management** - Org-level secrets enabled
3. **Canonical workflow stable** - Phase 1 complete (verified)

## Related

- ADR-0170: Build Pipeline Architecture (Phase 2 roadmap)
- GOV-0014: DevSecOps Implementation Matrix (Phase 2 section)
- Session Capture: `session_capture/2026-02-01-phase1-cicd-consolidation.md`
- ROADMAP Item 063: Explore GitHub App agent roles

---

Signed: Claude Opus 4.5 (2026-02-01)
