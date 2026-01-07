---
id: 03_GOVERNANCE_BACKSTAGE
title: Backstage Governance (Deprecated)
type: policy
domain: platform-core
applies_to: []
owner: platform-team
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
  - 01_GOVERNANCE
  - 18_BACKSTAGE_MVP
  - ADR-0008
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: governance
status: deprecated
version: '1.0'
dependencies: []
supported_until: 2027-01-03
breaking_change: false
---

# Backstage Governance (Deprecated)

Doc contract:

- Purpose: Preserve the previous Backstage governance mapping for reference.
- Owner: platform
- Status: deprecated
- Review cadence: as needed
- Related: docs/10-governance/01_GOVERNANCE.md, docs/00-foundations/18_BACKSTAGE_MVP.md, docs/adrs/ADR-0008-app-backstage-portal.md

Backstage governance guidance has been consolidated into
`docs/10-governance/01_GOVERNANCE.md` under **Backstage Governance Lens (Summary)** to avoid
duplication.
