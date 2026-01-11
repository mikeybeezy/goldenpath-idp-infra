---
id: 2026-01-05_1922_ecr-workflow-optimization
title: 'Implementation Plan: ECR Workflow Optimization'
type: implementation-plan
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: governance
status: active
version: '1.0'
supported_until: 2028-01-01
breaking_change: false
---

# ECR Workflow Optimization roadmap

This plan outlines the steps to optimize the ECR registry creation process, enhance documentation synchronization, and improve the developer experience.

## Proposed Tasks

### Workflow Updates (`create-ecr-registry.yml`)
- [x] **Task 1: Auto-generate Registry IDs**
    - *Action:* Remove the manual `id` input; auto-calculate it from the name.
- [x] **Task 2: Automatic Documentation Sync**
    - *Action:* Run `generate_catalog_docs.py` inside the workflow before committing.
- [x] **Task 3: HCL Validation**
    - *Action:* Add a check to ensure `terraform.tfvars` remains valid HCL after appending.

### Script Refactors (`generate_catalog_docs.py`)
- [x] **Task 4: Externalize Security Policies**
    - *Action:* Move risk-based settings to a shared `docs/10-governance/policies/ecr-risk-settings.yaml`.
- [x] **Task 5: Generalize for Multi-Catalog**
    - *Action:* Refactor script to handle other resource domains (S3, RDS).

### User Experience & Tooling
- [x] **Task 6: PR Guidance Injection**
    - *Action:* Add deep-links to the [Push Image Guide](docs/70-operations/runbooks/app-team/push-image-guide.md) in the PR body.
- [x] **Task 7: Image Creation & Tagging Script**
    - *Action:* Create a standardized script (e.g., `scripts/ecr-build-push.sh`) to handle building, multi-tagging (Git SHA + SemVer), and pushing.

---

## Verification Plan

### Automated Verification
- **Github Actions**: Ensure the `create-ecr-registry.yml` workflow completes without errors after refactors.
- **Python Tests**: Run `python3 scripts/generate_catalog_docs.py` and verify Markdown output matches expectations.
- **HCL Lint**: Use `terraform fmt -check` or a simple grep/awk check to verify `tfvars` integrity.

### Manual Verification
- Trigger the workflow and verify the resulting PR includes the correct ID and synced documentation.
- Test the new build-push script with a sample application.
