# CL-0013: Dev bootstrap defaults off

Date: 2026-01-02
Owner: platform
Scope: dev, bootstrap, terraform
Related: ADR-0064, PR #101

## Summary

- Disable dev defaults for Terraform-managed K8s resources and storage add-ons.
- Reduce bootstrap failures when prerequisites are not yet met.

## Impact

- Dev bootstrap no longer creates IRSA service accounts or requires storage add-ons
  unless explicitly enabled.

## Changes

### Added

- N/A.

### Changed

- `enable_k8s_resources` default is now `false` in `envs/dev/terraform.tfvars`.
- `enable_storage_addons` default is now `false` in `envs/dev/terraform.tfvars`.

### Fixed

- N/A.

### Deprecated

- N/A.

### Removed

- N/A.

### Documented

- ADR-0064 documents the default change and operator opt-in.

### Known limitations

- Operators must explicitly opt in when prerequisites are ready.

## Rollback / Recovery

- Revert the defaults in `envs/dev/terraform.tfvars` to `true`.

## Validation

- Not run (doc-only change; bootstrap rerun pending).
