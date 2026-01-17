---
id: CL-0064-terraform-lint-workflow
title: '[CI] Add Offline Terraform Lint & Validation Gate'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0102
  - CL-0064-terraform-lint-workflow
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
## [1.0.0] - 2026-01-06

### Added
- **CI/CD**: Added `.github/workflows/ci-terraform-lint.yml` to provide fast, offline validation for Terraform code.
  - Checks formatting (`terraform fmt`)
  - Validates syntax (`terraform validate`) without backend initialization.
  - Blocks PRs with invalid HCL before expensive plans run.

### Changed
- **Governance**: Implemented ADR-0102 (Layer 2 Terraform Validation).
- **Standards**: All PRs modifying `.tf` files now require passing lint checks.
