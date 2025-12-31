# CL-0001: Teardown kubectl timeout guard

Date: 2025-12-31
Owner: platform
Scope: teardown
Related: docs/17_BUILD_RUN_FLAGS.md, bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh

## Summary

- Add a kubectl request timeout to LoadBalancer cleanup calls to avoid indefinite hangs.
- Document the new timeout flag for operators.

## Impact

- Teardown LB cleanup will fail fast on API stalls and continue through the wait loop.
- Operators can tune cleanup request timeout without changing teardown logic.

## Changes

### Added

- `KUBECTL_REQUEST_TIMEOUT` flag for teardown LB cleanup calls.

### Changed

- LoadBalancer service get/delete calls use request timeouts in teardown runners.

### Fixed

- Teardown can no longer hang indefinitely on a stuck Kubernetes API call during LB cleanup.

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
