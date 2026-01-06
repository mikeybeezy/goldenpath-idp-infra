---
id: ADR-0111-platform-documentation-auto-healing
title: 'ADR-0111: Automated Documentation Auto-Healing'
type: documentation
category: adrs
version: 1.0
owner: platform-team
status: active
dependencies:
  - ADR-0103
  - ADR-0104
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
  - ADR-0101
---

# ADR-0111: Automated Documentation Auto-Healing

- **Status:** Accepted
- **Date:** 2026-01-06
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** [ADR-0101: PR Metadata Auto-Heal](./ADR-0101-pr-metadata-auto-heal.md)

---

## Context

Our platform uses automated indexing scripts (`generate_script_index.py`, `generate_workflow_index.py`) to maintain documentation portals (`scripts/index.md`, `ci-workflows/CI_WORKFLOWS.md`). 

Currently, these scripts are passive; they rely on developers or manual agents to run them. This has led to frequent "Documentation Drift" where new scripts or workflows are added but the indices are not updated. 

While we have validation in CI, it merely flags the error, requiring manual intervention to fix.

## Decision

We will implement an **Automated Documentation Auto-Healing** mechanism.

> We will upgrade indexing scripts to support validation mode and implement a GitHub Action that automatically commits index updates back to Pull Request branches when drift is detected.

## Scope

- **Applies to**: `scripts/index.md`, `ci-workflows/CI_WORKFLOWS.md`.
- **Does not apply to**: Hand-written documentation or Architecture Decision Records (ADRs).

## Consequences

### Positive

- **Zero Drift**: Documentation is guaranteed to be in sync with the repository state.
- **Developer Velocity**: Developers don't need to remember to run indexing scripts; the platform "heals" itself.
- **Consistency**: Indices follow a standardized format enforced by the generation logic.

### Tradeoffs / Risks

- **Bot Noise**: PRs will see automated commits from `github-actions[bot]`.
- **Merge Complexity**: Automated commits might occasionally cause minor merge conflicts if the developer is actively editing the same files.

### Operational impact

- The CI bot must have `contents: write` permissions.
- Workflows must use `[skip ci]` to prevent infinite loops.

## Alternatives considered

1. **Strict Validation Only**: Keeping the current "fail in CI" model. Rejected because it adds friction to the developer experience for a purely mechanical task.
2. **Scheduled Sync**: Running a cron job to update indices. Rejected because it leads to "state delay" between PR merge and documentation update.

## Follow-ups

1. Upgrade `scripts/generate_script_index.py` with `--validate`.
2. Upgrade `scripts/generate_workflow_index.py` with `--validate`.
3. Implement `.github/workflows/ci-index-auto-heal.yml`.
