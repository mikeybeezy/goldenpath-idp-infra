---
id: CL-0200-backstage-branch-protection-governance
title: Backstage repo branch protection and governance hardening
type: changelog
status: active
owner: platform-team
domain: governance
applies_to:
  - goldenpath-idp-backstage
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: gh-api-revert
  observability_tier: bronze
  maturity: 3
schema_version: 1
relates_to:
  - ADR-0164-agent-trust-and-identity
  - ADR-0182-tdd-philosophy
supersedes: []
superseded_by: []
tags:
  - governance
  - security
  - backstage
  - branch-protection
inheritance: {}
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0200: Backstage repo branch protection and governance hardening

## Summary

Implemented comprehensive branch protection and governance controls on the `goldenpath-idp-backstage` repository. All three branches (`main`, `development`, `governance-registry`) are now protected from deletion, and `main` has strict merge controls.

## Changes Made

### 1. Branch Protection on `main`

| Rule | Setting |
|------|---------|
| Require PR before merging | ✅ Enabled |
| Require 1 approval | ✅ Enabled |
| Require CODEOWNER review | ✅ Enabled |
| Dismiss stale reviews | ✅ Enabled |
| Require `validate-source` status check | ✅ Enabled |
| Require branch up to date | ✅ Enabled |
| Enforce for admins | ✅ Enabled |
| Block force pushes | ✅ Enabled |
| Block deletions | ✅ Enabled |

### 2. Branch Protection on `development`

| Rule | Setting |
|------|---------|
| Enforce for admins | ✅ Enabled |
| Block force pushes | ✅ Enabled |
| Block deletions | ✅ Enabled |

### 3. Branch Protection on `governance-registry`

| Rule | Setting |
|------|---------|
| Enforce for admins | ✅ Enabled |
| Block force pushes | ✅ Enabled |
| Block deletions | ✅ Enabled |

**Note:** The `governance-registry` branch on backstage serves a different purpose than the identically-named branch on `goldenpath-idp-infra`. It does not follow the same merge/sync patterns as the infra repo's governance registry.

### 4. New Workflow: `main-branch-guard.yml`

Added workflow to enforce source branch policy and **block agents from merging to main**:

#### Source Branch Rules

- PRs to `main` from `development` → ✅ Allowed
- PRs to `main` with `hotfix` label → ✅ Allowed (requires CODEOWNER approval)
- PRs to `main` from any other branch →  Blocked

#### Agent/Bot Blocking (Strict Enforcement)

**Agents are NOT allowed to merge to main under any circumstances.**

The workflow explicitly blocks actors matching these patterns:

- `bot`, `[bot]`
- `github-actions`
- `dependabot`
- `renovate`
- `claude`, `copilot`
- `agent`, `automation`

```yaml
# Job 1: validate-source
# - Blocks any actor matching bot/agent patterns
# - Then checks source branch is 'development' or has 'hotfix' label

# Job 2: human-merge-required
# - Documents policy in GitHub Actions summary
```

#### Merges to `development` (Discretionary)

Merges from feature branches to `development` are **discretionary** - no strict source branch enforcement. Agents may create PRs to development, but the branch is protected from deletion and force push.

### 5. New Workflow: `governance-registry-guard.yml`

Added workflow to enforce permission-based agent control for `governance-registry`:

#### Policy

- **Humans**: Can merge freely (no restrictions)
- **Agents**: Must have `agent-merge-approved` label to merge

#### How It Works

1. Workflow detects if PR actor is an agent/bot
2. If agent, checks for `agent-merge-approved` label
3. If label missing →  Block merge
4. If label present → ✅ Allow merge (human granted permission)

#### Granting Permission

A CODEOWNER must:

1. Review the agent's PR changes
2. Add the `agent-merge-approved` label
3. Agent can then merge

### 6. Merge Policy Summary

| Target Branch         | Source Restriction                | Agent Can Merge?                    | Agent Can Create PR? |
| --------------------- | --------------------------------- | ----------------------------------- | -------------------- |
| `main`                | `development` or `hotfix` label   |  **NO** (never)                   | ✅ Yes               |
| `development`         | Any (discretionary)               | ✅ Yes                              | ✅ Yes               |
| `governance-registry` | Any                               | ⚠️ **Only with permission label**  | ✅ Yes               |

## Rationale

Per ADR-0164 (Agent Trust and Identity Architecture):
- Agents cannot delete protected branches
- Agents cannot bypass CODEOWNER requirements
- Agents cannot force push to protected branches
- Hotfix path requires human approval via CODEOWNER

## Pre-existing Assets (Unchanged)

The following were already in place:

- **CODEOWNERS**: Comprehensive file with ADR-0164 compliant patterns
- **ci.yml**: Lint, test, build, Docker push pipeline
- **tdd-gate.yml**: Enforces test coverage for new code
- **test-integrity-guard.yml**: Prevents test weakening

## Validation

```bash
# Verify branch protection via GitHub API
gh api repos/mikeybeezy/goldenpath-idp-backstage/branches/main/protection
gh api repos/mikeybeezy/goldenpath-idp-backstage/branches/development/protection
gh api repos/mikeybeezy/goldenpath-idp-backstage/branches/governance-registry/protection
```

## Impact

- **Agents**: Cannot delete any branch, cannot merge to `main` without human approval
- **Humans**: Must use `development` → `main` flow, or `hotfix` label for emergencies
- **CI**: `validate-source` check must pass before merge to `main`

## Files Changed

- `.github/workflows/main-branch-guard.yml` (new) - in `goldenpath-idp-backstage`
- `.github/workflows/governance-registry-guard.yml` (new) - in `goldenpath-idp-backstage`
- Branch protection rules (via GitHub API) - all 3 branches
