---
id: 08_GITHUB_AGENT_ROLES
title: GitHub Agent Roles (Apps and Service Accounts)
type: policy
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
- 04_PR_GUARDRAILS
- 07_AI_AGENT_GOVERNANCE
- 26_AI_AGENT_PROTOCOLS
---

# GitHub Agent Roles (Apps and Service Accounts)

Doc contract:

- Purpose: Define how to grant AI/automation roles without human GitHub accounts.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/07_AI_AGENT_GOVERNANCE.md, docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md, docs/10-governance/04_PR_GUARDRAILS.md

This doc explains how to implement agent roles using GitHub Apps, with minimal
privileges and auditability.

## Recommendation (default)

Use a GitHub App for AI/automation roles. GitHub Apps provide scoped, auditable
access without creating new human accounts.

## Why GitHub Apps

- Fine-grained permissions per repo.
- Auditable installation and access.
- Token rotation built-in.
- No personal accounts required.

## Minimal permission model

Start with least privilege and expand only as required.

Suggested baseline:

- Contents: read/write (only if the agent must push commits).
- Pull requests: read/write (open or update PRs).
- Issues: read (labels, comments).
- Metadata: read.

Avoid by default:

- Administration (only if required for branch protection updates).
- Actions: write (only if workflow dispatch is needed).
- Secrets: write (human-only unless explicitly approved).

## Setup steps (high level)

1. Create a GitHub App (org or repo scope).
2. Grant minimal permissions and install only on required repos.
3. Store the App ID and private key in secure secrets.
4. Use the App token in automation workflows.
5. Record the App in the AI Change Log if used for changes.

## Auditability

- Track App installations and permission changes.
- Require PRs for any App permission updates.
- Keep evidence links in PR descriptions (run IDs, logs).

## Operator checklist

- App permissions reviewed and approved.
- Branch protection on `main` enforces development-only merges.
- PR checklist and label gates remain in effect.

## Future options

- Per-domain Apps (docs vs infra) to reduce blast radius.
- Time-bound App tokens with tighter scopes per job.
