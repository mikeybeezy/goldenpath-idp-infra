# Implementation Plan: Phase 2 - Closed-Loop Metadata Injection & Cost Visibility

This plan outlines the strategy for propagating "governance metadata" into Kubernetes resources and enabling FinOps cost visibility via Infracost.

## User Review Required

> [!IMPORTANT]
> This change will modify `values.yaml` files across the repository to include a `governance` block. This ensures that live Kubernetes resources can "advertise" their ownership and risk profiles.

## Proposed Changes

### [Core Tooling]
#### [MODIFY] [scripts/standardize-metadata.py](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/standardize-metadata.py)
Update the "Healer" to perform a **Governance Injection Pass**:
- After standardizing a `metadata.yaml`, it will search for associated deployment files:
  - `values.yaml` or `values/*.yaml` in the same directory.
  - `deploy/**/values.yaml` in subdirectories.
- Inject a standardized `governance` block into these files.

### [GitOps Components]
#### [MODIFY] [ArgoCD Applications](file:///Users/mikesablaze/goldenpath-idp-infra/gitops/argocd/apps/)
Update ArgoCD application manifests to include metadata annotations:
- `goldenpath.idp/owner`
- `goldenpath.idp/risk`
- `goldenpath.idp/id`

### [Application Templates]
#### [MODIFY] [Application Templates](file:///Users/mikesablaze/goldenpath-idp-infra/apps/)
Update Jinja-style templates to render these governance fields as Kubernetes annotations/labels.

### [Cost Visibility]
#### [ENABLE] [Infracost in CI](file:///Users/mikesablaze/goldenpath-idp-infra/.github/workflows/pr-terraform-plan.yml)
Activate FinOps cost reporting for Terraform PRs:
- **Prerequisite**: Set `INFRACOST_API_KEY` secret in GitHub.
- **Mechanism**: The workflow automatically detects the key and runs `infracost breakdown`.
- **Output**: A PR comment detailing the cost impact of the change.

## Verification Plan

### Automated Tests
- Run `python3 scripts/standardize-metadata.py` and verify `values.yaml` changes via `git diff`.
- Run `python3 scripts/validate-metadata.py .` to ensure 100% compliance is maintained.

### Manual Verification
- Inspect a sample `values.yaml` (e.g. [gitops/helm/kong/values/dev.yaml](file:///Users/mikesablaze/goldenpath-idp-infra/gitops/helm/kong/values/dev.yaml)) for the new `governance` block.
- Verify that [PLATFORM_HEALTH.md](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md) still correctly aggregates this data.
