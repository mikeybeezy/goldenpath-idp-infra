---
id: 23_NEW_JOINERS
title: New Joiners Guide
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 00_START_HERE
  - 02_PLATFORM_BOUNDARIES
  - 13_COLLABORATION_GUIDE
  - 24_PR_GATES
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - 38_BRANCHING_STRATEGY
  - ADR-0042-platform-branching-strategy
  - CL-0078
  - agent_session_summary
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# New Joiners Guide

Doc contract:

- Purpose: Define onboarding expectations and local setup steps.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/80-onboarding/13_COLLABORATION_GUIDE.md, docs/20-contracts/02_PLATFORM_BOUNDARIES.md, docs/40-delivery/38_BRANCHING_STRATEGY.md

This guide outlines the minimum setup expected for contributors to GoldenPath IDP.

## Required setup

- Install the project tooling listed in `docs/80-onboarding/13_COLLABORATION_GUIDE.md`.
- Review the day-one checklist in `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md`.
- Review the platform/team boundary in `docs/20-contracts/02_PLATFORM_BOUNDARIES.md`.
- Initialize your local environment:

```bash
bin/governance setup
```

## Before your first PR

- Run all hooks and linters locally to validate your setup:

```bash
bin/governance lint
```

- Fix any issues reported by the tools before opening a PR.
- Use `scripts/scaffold_doc.py` for any new docs; pre-commit will auto-fix headers if needed.
- Review PR gates and how to unblock them in `docs/80-onboarding/24_PR_GATES.md`.
- Review AI agent protocols in `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md` (these rules apply to human collaborators too).
- **Internalize VQ**: Your first task is to read [**VQ Principles & Philosophy**](../product/VQ_PRINCIPLES.md) and identify the VQ bucket (**🔴 HV/HQ**, etc.) for your first contribution.

## Expectations (The Value Provider Mindset)

We don't just "commit code" here; we **reclaim time**.

- **Value-Led PRs**: Every PR you open is expected to include a VQ classification in the PR body. This ensures we focus on high-impact work and avoid over-engineering low-value targets.
- **Pre-commit hooks** are required for local commits.
- **CI remains the source of truth**; hooks are the fast preflight gate.
- **Merge Path**: PRs merge into `development` first; `main` only accepts merges from `development`.

## Branching and PR flow

- Create branches from `development`.
- Open PRs into `development`.
- Only `development` is allowed to merge into `main`.

## Skip policy

Bypass hooks only for urgent fixes, then run the hooks in a follow-up commit.
Document the reason in the PR.

```text
SKIP=hook-id git commit
```

## Need help?

Ask in the platform team channel or open an issue with the exact error output.
