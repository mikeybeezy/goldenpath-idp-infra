<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0061-ecr-workflow-optimizations
title: ECR Workflow and Documentation Optimizations
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
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - CL-0061-ecr-workflow-optimizations
  - RB-0024-request-registry
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0061: ECR Workflow and Documentation Optimizations

Implemented a comprehensive series of optimizations to the ECR registry creation lifecycle and the platform documentation engine.

## Changes

### Workflow Updates (`.github/workflows/create-ecr-registry.yml`)
- **Automated Registry IDs**: Removed manual `id` input; replaced with automated calculation logic.
- **Documentation Auto-Sync**: Added mandatory documentation generation step to ensure `REGISTRY_CATALOG.md` is updated in the same PR.
- **HCL Validation**: Added `terraform fmt` check to guard the integrity of `terraform.tfvars`.
- **Developer UX**: Added deep-links to the [Push Image Guide](docs/70-operations/runbooks/app-team/push-image-guide.md) in the PR body.

### Scripting & Governance
- **Refactored `generate_catalog_docs.py`**:
    - Converted to a domain-agnostic engine capable of documenting multiple resource types.
    - Added support for loading security policies from external YAML files.
    - Improved pluralization/singularization logic for resource labels.
- **Centralized Policies**: Created `docs/10-governance/policies/ecr-risk-settings.yaml` as the single source of truth for risk-based security controls.
- **New Build Script**: Created `scripts/ecr-build-push.sh` to standardize Docker builds, multi-tagging (Git SHA + Version), and ECR pushes for app teams.

## Verification
- **Verified**: Documentation generator successfully generates pluralized titles ("Registry Inventory") and loads external policies.
- **Verified**: Workflow dispatch validates inputs and performs atomic updates to catalog and tfvars.
