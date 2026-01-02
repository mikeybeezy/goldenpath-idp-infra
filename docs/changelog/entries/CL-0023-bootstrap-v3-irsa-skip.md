# CL-0023: Bootstrap v3 skips IRSA apply

Date: 2026-01-02
Owner: platform
Scope: infra
Related: docs/adrs/ADR-0073-platform-bootstrap-v3-irsa-skip.md, PR #114

## Summary

Added a v3 bootstrap script that skips Terraform IRSA apply in Stage 3B and
validates existing service accounts instead.

## Changes

### Added

- `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh`

### Changed

- `Makefile`: allow `BOOTSTRAP_VERSION=v3`.
- `.github/workflows/ci-bootstrap.yml`: add `v3` option to the selector.

## Validation

- Not run (workflow-only change).
