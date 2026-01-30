---
id: session-capture-2026-01-30-backstage-governance-otel
title: Backstage Branch Governance and OpenTelemetry CI Integration
type: session-capture
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
relates_to:
  - ADR-0164-agent-trust-and-identity-architecture
  - ADR-0055-platform-tempo-tracing-backend
  - CL-0200-backstage-branch-protection-governance
  - PROMPT-0003-recursive-pr-gate-compliance
supersedes: []
superseded_by: []
tags:
  - governance
  - ci-cd
  - opentelemetry
  - branch-protection
inheritance: {}
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 8.0
---

# 2026-01-30T14:00Z — Governance: Backstage branch protection + OTel CI — env=dev build_id=na

Owner: platform-team
Agent: Claude Opus 4.5
Goal: Implement comprehensive branch governance for backstage repo and add OpenTelemetry CI tracing

Date range: 2026-01-30
Environment: GitHub `goldenpath-idp-backstage`
Objective: Establish agent trust boundaries and enable CI observability

## In-Session Log

- 13:00Z — Started: Branch protection analysis — status: complete
- 13:15Z — Change: Created main-branch-guard.yml — file: .github/workflows/main-branch-guard.yml
- 13:20Z — Change: Created governance-registry-guard.yml — file: .github/workflows/governance-registry-guard.yml
- 13:30Z — Change: Applied branch protection via GitHub API — branches: main, development, governance-registry
- 13:45Z — Decision: Agents can never merge to main — why: ADR-0164 trust boundary
- 13:50Z — Decision: governance-registry requires agent-merge-approved label — why: explicit human permission
- 14:00Z — Change: Added Docker path filter — file: .github/workflows/ci.yml
- 14:10Z — Blocker: validate-source check pending — next step: Fixed branch protection rule name mismatch
- 14:15Z — Result: PR #7 all checks passing — outcome: ready for human merge
- 14:30Z — Change: Added otel-cli integration — file: .github/workflows/ci.yml

## Checkpoints

- [x] Branch protection enabled on all 3 branches
- [x] Agents blocked from merging to main
- [x] Agents require permission label for governance-registry
- [x] Docker path filter implemented
- [x] OpenTelemetry CI tracing added
- [x] PR #7 ready for human merge
- [x] PR #8 merged (Docker path filter)

## Key Decisions

### 1. Agent Trust Boundaries (per ADR-0164)

| Target Branch | Agent Can Merge? | Condition |
|---------------|------------------|-----------|
| main | **NO** (never) | Human-only for production deployments |
| development | Yes | Discretionary after CI passes |
| governance-registry | With permission | Requires `agent-merge-approved` label |

### 2. Branch Protection Configuration

All three branches protected with:
- Force push: disabled
- Deletion: blocked
- Required status checks: enabled

### 3. OpenTelemetry CI Integration

Implemented otel-cli tracing for CI pipelines:
- Service name: `backstage-ci`
- Endpoint: configurable via `vars.OTEL_EXPORTER_OTLP_ENDPOINT`
- Traced operations: pipeline start, yarn build, docker build, pipeline complete
- Graceful degradation: continues if endpoint not configured

## Artifacts Touched

### goldenpath-idp-backstage
- `.github/workflows/ci.yml` (modified - path filter + otel-cli)
- `.github/workflows/main-branch-guard.yml` (new)
- `.github/workflows/governance-registry-guard.yml` (new)
- Branch protection rules (via API)

### goldenpath-idp-infra
- `docs/changelog/entries/CL-0200-backstage-branch-protection-governance.md` (new)
- `session_capture/2026-01-30-backstage-governance-and-otel-ci.md` (this file)

## Outputs Produced

- **PRs (backstage):**
  - PR #7: Release - CI pipelines, TDD enforcement, branch governance (ready for human merge)
  - PR #8: Docker path filter (merged to development)

- **Workflows Created:**
  - main-branch-guard.yml - Blocks agents from main, enforces development→main flow
  - governance-registry-guard.yml - Requires permission label for agent merges

- **CI Enhancements:**
  - Docker validation only runs when Dockerfile/backend files change
  - OpenTelemetry traces sent for build observability

## Technical Details

### Docker Path Filter

Uses `dorny/paths-filter@v3` to detect changes:
```yaml
filters:
  docker:
    - 'Dockerfile'
    - '**/Dockerfile'
    - 'packages/backend/**'
    - 'yarn.lock'
    - 'package.json'
    - '.dockerignore'
```

### OpenTelemetry Integration

```yaml
env:
  OTEL_EXPORTER_OTLP_ENDPOINT: ${{ vars.OTEL_EXPORTER_OTLP_ENDPOINT }}
  OTEL_SERVICE_NAME: 'backstage-ci'
  OTEL_CLI_VERSION: '0.4.5'

# Example traced step
- name: Build backend (traced)
  run: |
    otel-cli exec \
      --service "${{ env.OTEL_SERVICE_NAME }}" \
      --name "yarn-build-backend" \
      --attrs "github.run_id=${{ github.run_id }}" \
      -- yarn build:backend
```

### Branch Protection Fix

Issue: `validate-source` check was "Expected — Waiting for status to be reported"

Root cause: Branch protection required `validate-source` (job ID) but workflow reported `Validate Source Branch` (job name)

Fix: Updated branch protection via API:
```bash
gh api repos/.../branches/main/protection/required_status_checks -X PATCH \
  --input '{"checks": [{"context": "Validate Source Branch"}]}'
```

## Next Actions

- [ ] Human to merge PR #7 to main (backstage repo)
- [ ] Configure `OTEL_EXPORTER_OTLP_ENDPOINT` repository variable when Tempo ingress is ready
- [ ] Verify traces appear in Grafana after first traced build
- [ ] Document otel-cli setup in CI environment contract

## Session Report

### Summary
- Implemented comprehensive branch governance for backstage repo per ADR-0164
- Created guard workflows to enforce agent trust boundaries
- Added Docker path filter to reduce unnecessary CI runs
- Integrated OpenTelemetry CLI for CI build tracing (planned → implemented)
- Fixed branch protection status check name mismatch

### Decisions
- Agents cannot merge to main under any circumstances
- Agents need explicit human permission (label) for governance-registry
- OpenTelemetry traces are optional (graceful degradation if endpoint not set)

### Risks/Follow-ups
- Tempo ingress must be configured for traces to be collected
- Repository variable `OTEL_EXPORTER_OTLP_ENDPOINT` needs to be set
- PR #7 requires human merge to complete branch protection rollout

### Validation
- PR #8 CI passed with Docker validation correctly skipped (path filter working)
- PR #7 all checks green, ready for human merge
- Workflow syntax validated via GitHub Actions
