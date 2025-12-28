# New Joiners Guide

This guide outlines the minimum setup expected for contributors to GoldenPath IDP.

## Required setup

- Install the project tooling listed in `docs/13_COLLABORATION_GUIDE.md`.
- Review the platform/team boundary in `docs/02_PLATFORM_BOUNDARIES.md`.
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

## Expectations

- Pre-commit hooks are required for local commits.
- CI remains the source of truth; hooks are the fast preflight gate.

## Skip policy

Bypass hooks only for urgent fixes, then run the hooks in a follow-up commit.
Document the reason in the PR.

```text
SKIP=hook-id git commit
```

## Need help?

Ask in the platform team channel or open an issue with the exact error output.
