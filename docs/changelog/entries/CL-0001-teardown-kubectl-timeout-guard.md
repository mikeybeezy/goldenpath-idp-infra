<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0001-teardown-kubectl-timeout-guard
title: 'CL-0001: Teardown kubectl timeout guard'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 40_CHANGELOG_GOVERNANCE
  - CL-0001-teardown-kubectl-timeout-guard
  - Changelog-template
  - DOCS_CHANGELOG_README
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-04
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0001: Teardown kubectl timeout guard

Date: 2025-12-31
Owner: platform
Scope: teardown
Related: docs/40-delivery/17_BUILD_RUN_FLAGS.md, bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh

## Summary

- Add kubectl request timeouts and non-blocking deletes to teardown cleanup paths.
- Document the new timeout flag for operators.

## Impact

- Teardown cleanup avoids indefinite waits on stuck API calls and deletion finalizers.
- Operators can tune cleanup request timeout without changing teardown logic.

## Changes

### Added

- `KUBECTL_REQUEST_TIMEOUT` flag for teardown cleanup calls.

### Changed

- Teardown delete calls use request timeouts and `--wait=false` for Argo/Kong/LB cleanup.

### Fixed

- Teardown is more resilient to stuck Kubernetes API calls and long-running deletions.

### Deprecated

- None.

### Removed

- None.

### Documented

- Teardown flags updated to include the kubectl timeout guard.

### Known limitations

- Timeout guard does not resolve underlying API unavailability.

## Rollback / Recovery

- Not required; remove the flag or revert the change.

## Validation

- Not run (CI will exercise on next teardown).
