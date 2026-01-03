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
- Install pre-commit and enable hooks:

```text
pre-commit install
```

## Before your first PR

- Run all hooks locally to validate your setup:

```text
pre-commit run --all-files
```

- Fix any issues reported by the hooks before opening a PR.
- Review PR gates and how to unblock them in `docs/80-onboarding/24_PR_GATES.md`.
- Review AI agent protocols in `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md` (these rules apply to human collaborators too).

## Expectations

- Pre-commit hooks are required for local commits.
- CI remains the source of truth; hooks are the fast preflight gate.
- Pre-commit runs on pull requests and should be required in branch protection.
- PRs merge into `development` first; `main` only accepts merges from `development`.

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
