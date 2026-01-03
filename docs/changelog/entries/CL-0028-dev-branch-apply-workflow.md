# CL-0028: Dev-branch apply workflow and changelog exemption

Date: 2026-01-03
Owner: platform
Scope: CI/CD guardrails
Related: PR <TBD>

## Summary

- add a dev-branch apply workflow for ephemeral dev builds
- allow `changelog-exempt` to skip changelog enforcement

## Impact

- dev-branch applies can be run with explicit confirmation and matching plan
- test-only changes can skip changelog entry when explicitly labeled

## Changes

### Added

- workflow: `.github/workflows/infra-terraform-apply-dev-branch.yml`
- label: `changelog-exempt`

### Changed

- changelog guardrail honors `changelog-exempt`

## Rollback / Recovery

- Remove the dev-branch workflow and the exemption check if needed.

## Validation

- Not run (workflow change)
