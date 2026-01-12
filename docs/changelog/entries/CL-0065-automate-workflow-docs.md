---
id: CL-0065-automate-workflow-docs
title: '[Docs] Automate CI Workflow Index Generation'
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
  - ADR-0103
  - ci-workflows/CI_WORKFLOWS.md
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
- **Documentation**: Implemented `scripts/generate_workflow_index.py` to auto-generate the CI Workflows Index.
- **Governance**: Added [ADR-0103](docs/adrs/ADR-0103-automated-workflow-docs.md) defining the strategy for automated workflow documentation.

### Changed
- **Index**: `ci-workflows/CI_WORKFLOWS.md` is now fully automated, featuring an ASCII tree visualization and detailed breakdown of all 30+ workflows. Manual edits to this file will now be overwritten.
