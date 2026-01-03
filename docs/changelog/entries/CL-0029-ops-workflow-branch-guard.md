# CL-0029: Ops workflow branch guard

Date: 2026-01-03
Owner: platform
Scope: CI/CD operations
Related: PR #126, docs/adrs/ADR-0074-platform-ops-workflow-branch-guard.md

## Summary

- restrict bootstrap, teardown, orphan cleanup, and managed LB cleanup to main/development

## Impact

- operational workflows can only run from controlled branches; reduces risk of drift

## Changes

### Changed

- branch validation added to CI bootstrap/teardown/orphan cleanup workflows

## Rollback / Recovery

- Remove branch validation steps if needed.

## Validation

- Not run (workflow change)
