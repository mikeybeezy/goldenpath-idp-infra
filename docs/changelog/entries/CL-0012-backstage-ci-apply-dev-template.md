# CL-0012: Backstage template for dev Terraform apply

Date: 2025-12-31
Owner: platform
Scope: Backstage, CI workflow UX
Related: `backstage/templates/ci-apply-dev/template.yaml`, `.github/workflows/infra-terraform-apply-dev.yml`

## Summary

- Add a Backstage Scaffolder template to trigger the dev Terraform apply workflow.

## Impact

- Developers can launch the dev apply workflow from Backstage with guardrails.

## Changes

### Added

- `CI Apply (dev)` Backstage template and catalog location in Backstage values.

## Rollback / Recovery

- Remove the template file and catalog location.

## Validation

- Not run (manual workflow).
