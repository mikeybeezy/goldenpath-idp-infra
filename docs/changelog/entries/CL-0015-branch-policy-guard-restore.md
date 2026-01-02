# CL-0015: Restore branch policy guard for main

Date: 2026-01-02
Owner: platform
Scope: CI, governance
Related: PR #104, `docs/adrs/ADR-0065-platform-branch-policy-guard.md`

## Summary

- Restore the branch policy guard to require development -> main merges.

## Impact

- Direct merges from non-development branches to main are blocked.

## Changes

### Changed

- Reinforced `development` as the only allowed source branch for main merges.

### Documented

- Added ADR for the branch policy guard restoration.

## Rollback / Recovery

- Revert the branch policy guard change in `.github/workflows/branch-policy.yml`.

## Validation

- CI guardrails enforce the policy on pull requests to main.
