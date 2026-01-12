---
id: 24_PRE_COMMIT_HOOKS
title: Pre-commit Hooks (Living Document)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0019
category: delivery
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:pre-commit
  - module:terraform
  - module:markdownlint
breaking_change: false
---

# Pre-commit Hooks (Living Document)

This document describes how pre-commit hooks are configured and used in this repo.

## What this is

Pre-commit hooks run locally before a commit is created. They prevent common formatting and lint
issues from reaching CI.

## Installation

```text
pre-commit install
```

## Run all hooks

```text
pre-commit run --all-files
```

## Current hooks

Keep this list aligned with `.pre-commit-config.yaml`.

- Markdown lint (docs and ADRs)
- Terraform fmt
- Whitespace and EOF fixes

## Bypass policy

Bypass only for urgent fixes, then follow up with a cleanup commit.

```text
SKIP=hook-id git commit
```

This is not automated. Teams are expected to document the reason in the PR and
run the hooks in a follow-up commit as soon as possible.

## Troubleshooting

- If a hook fails, run it locally and fix the reported files.
- If a hook behaves differently from CI, raise it with the platform team.
