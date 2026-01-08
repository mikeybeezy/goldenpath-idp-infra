---
id: CL-0079
title: 'CL-0079: Delivery Automation Backfill'
type: changelog
lifecycle: active
schema_version: 1
relates_to:
  - ADR-0123
---

# CL-0079: Delivery Automation Backfill

Date: 2026-01-07
Owner: platform-team
Scope: Delivery
Related: ADR-0123

## Summary

This entry backfills the governance record for the Delivery Automation Suite, which handles ECR provisioning and build telemetry.

## Changes

### Added
- `scripts/scaffold_ecr.py`: Standardized ECR creation.
- `scripts/ecr-build-push.sh`: Image delivery wrapper.
- `scripts/generate-build-log.sh`: Build telemetry.
- `scripts/generate-teardown-log.sh`: Destruction telemetry.
- `scripts/resolve-cluster-name.sh`: Environment-aware cluster naming.

## Validation

- These scripts have been in active production use across the `goldenpath-idp-backstage` and `goldenpath-wordpress-app` workflows.
