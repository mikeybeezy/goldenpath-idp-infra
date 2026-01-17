---
id: 10_SECRET_SCANNING_POLICY
title: Secret Scanning Policy (Gitleaks)
type: policy
domain: security
risk_profile:
  production_impact: low
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 04_PR_GUARDRAILS
  - 09_GOVERNANCE_TESTING
  - CL-0100
tags:
  - security
  - secrets
  - gitleaks
category: governance
supported_until: 2028-01-10
version: '1.0'
breaking_change: false
---
# Secret Scanning Policy (Gitleaks)

Doc contract:

- Purpose: Prevent secrets from entering the repository.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/04_PR_GUARDRAILS.md

## Scope

This policy applies to all code and documentation committed to the repository.

## Requirements

### Local (Pre-commit)

- Developers must run pre-commit locally before pushing changes.
- Gitleaks is included in `.pre-commit-config.yaml` and runs on staged files.

Install once:

```bash
pre-commit install
```

### CI (PR to main)

- `Security - Gitleaks` runs on every PR targeting `main`.
- A finding fails the check and blocks merge.

## Handling Findings

1. Remove the secret from the commit.
2. Rotate the secret immediately.
3. If the secret is in Git history, coordinate a rewrite with platform.

## Allowlisting

- Only allowed for known false positives.
- Add allowlist entries to `.gitleaks.toml` with justification.
- Document the exception in the PR summary and changelog if needed.

## Enforcement

- Local pre-commit + CI checks are mandatory.
- Bypass requires platform approval and documented rationale.
