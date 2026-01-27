---
id: CL-0189
title: Development Branch Full Lockdown Protection
type: changelog
status: active
date: 2026-01-25
author: platform-team
change_type: security
impact: high
relates_to:
  - 07_AI_AGENT_GOVERNANCE
  - PROMPT-0003
  - agent-merge-guard.yml
---

# CL-0189: Development Branch Full Lockdown Protection

## Summary

Implemented full branch protection for `development` branch to prevent unauthorized direct pushes and require human approval for all merges.

## Changes

### Branch Protection Rules

| Rule | Setting |
|------|---------|
| Require PR | Yes |
| Required approvals | 1 (human) |
| Dismiss stale reviews | Yes |
| Require status checks | Yes |
| Enforce for admins | Yes |
| Allow force push | No |
| Allow deletions | No |

### Required Status Checks

- `pre-commit` - Quality pre-commit hooks
- `Terraform Lint & Validate` - Terraform syntax validation
- `pr-guardrails` - PR checklist and template
- `require-session-logs` - Session documentation enforcement

### New Workflow

Added `.github/workflows/agent-merge-guard.yml`:
- Detects agent-authored PRs (bot accounts, known patterns)
- Adds warning notice requiring human approval
- Integrates with existing PR review requirements

## Motivation

An agent pushed 717 files directly to development without PR review, bypassing all governance checks. This change ensures:

1. All changes go through PR review
2. At least one human must approve
3. All CI checks must pass before merge
4. Agents cannot self-merge to development

## Impact

- **Agents**: Must create PRs and wait for human approval
- **Humans**: Standard PR workflow, 1 approval required
- **CI**: Existing checks now enforced on development branch
