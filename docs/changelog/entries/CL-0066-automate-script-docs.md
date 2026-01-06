---
id: CL-0066-automate-script-docs
title: '[Docs] Automate Script Index Generation'
type: changelog
category: documentation
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: none
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - ADR-0104
  - scripts/index.md
---

## [1.0.0] - 2026-01-06

### Added
- **Documentation**: Implemented `scripts/generate_script_index.py` to auto-generate the Platform Automation Scripts Index.
- **Governance**: Added [ADR-0104](docs/adrs/ADR-0104-automated-script-docs.md) defining the strategy for automated script documentation.

### Changed
- **Index**: `scripts/index.md` is now fully automated. It dynamically categorizes and describes all 25+ platform scripts by parsing their source code headers.
