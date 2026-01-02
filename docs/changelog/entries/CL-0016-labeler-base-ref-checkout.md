# CL-0016: Labeler uses base ref checkout

Date: 2026-01-02
Owner: platform
Scope: CI, governance
Related: PR #107, `docs/adrs/ADR-0067-platform-labeler-base-ref.md`

## Summary

- Switch PR labeler checkout from base SHA to base ref to avoid stale config failures.

## Impact

- Labeler runs against the latest base branch config, reducing false failures.

## Changes

### Changed

- Labeler workflow checks out `github.event.pull_request.base.ref`.

### Documented

- Added ADR for the labeler checkout decision.

## Rollback / Recovery

- Revert the checkout change in `.github/workflows/pr-labeler.yml`.

## Validation

- CI labeler check passes on recent PRs.
