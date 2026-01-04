---
id: CL-0002
title: 'CL-0002: Refactor Bootstrap to Terraform'
type: changelog
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-04
  breaking_change: false
relates_to:

- ADR-0063
- CL-0002

---

# CL-0002: Refactor Bootstrap to Terraform

Date: 2026-01-01
Owner: platform
Scope: envs/all
Related: ADR-0063

## Summary

- Replaced shell-based ArgoCD installation with Terraform Helm Provider.
- This simplifies the deployment process to a single `terraform apply`.

## Impact

- **Breaking Change**: The `make bootstrap` command is deprecated. Use `make apply` for all lifecycle stages (creation and updates).
- **Behavior Change**: ArgoCD is now managed as a Terraform resource. Deleting the Terraform stack (destroy) will explicitly uninstall ArgoCD before deleting the cluster.

## Changes

### Added

- Terraform `helm_release` resource for ArgoCD in `modules/kubernetes_addons`.
- New required provider `hashicorp/helm` in `main.tf`.

### Removed

- `bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh`
- `bootstrap/10_gitops-controller/10_argocd_helm.sh`
- `make bootstrap` target (aliased to `make apply` with a warning).

### Documented

- Updated `README.md` to remove "Bootstrap" step from the Quickstart guide.
- Added `ADR-0063-platform-terraform-helm-bootstrap.md`.

## Validation

- Validated that `terraform apply` on a fresh environment results in a running ArgoCD instance.
- Verified that `terraform destroy` cleanly removes the release.
