# CL-0019: AWS Load Balancer Controller refactor

Date: 2026-01-02
Owner: platform
Scope: bootstrap, terraform
Related: docs/adrs/ADR-0070-platform-terraform-aws-lb-controller.md

## Summary

- Move AWS Load Balancer Controller install into Terraform via `kubernetes_addons`.

## Impact

- Controller installs during `terraform apply`; the manual bootstrap script is deprecated.

## Changes

### Added

- ADR documenting Terraform-managed AWS Load Balancer Controller.
- `kubernetes_addons.helm_release.aws_load_balancer_controller`.

### Changed

- Bootstrap installs the controller during `terraform apply`.

### Deprecated

- `bootstrap/30_core-addons/10_aws_lb_controller.sh`.

## Rollback / Recovery

- Revert the Terraform change and restore the manual bootstrap step.

## Validation

- Verify plan/apply includes the controller release.
