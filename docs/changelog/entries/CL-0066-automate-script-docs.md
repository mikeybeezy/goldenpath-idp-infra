---
id: CL-0066-automate-script-docs
title: '[Docs] Automate Script Index Generation'
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
  - ADR-0104
  - scripts/index.md
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
- **Documentation**: Implemented `scripts/generate_script_index.py` to auto-generate the Platform Automation Scripts Index.
- **Governance**: Added [ADR-0104](docs/adrs/ADR-0104-automated-script-docs.md) defining the strategy for automated script documentation.

### Changed
- **Index**: `scripts/index.md` is now fully automated. It dynamically categorizes and describes all 25+ platform scripts by parsing their source code headers.
