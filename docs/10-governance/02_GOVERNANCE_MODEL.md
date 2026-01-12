---
id: 02_GOVERNANCE_MODEL
title: Governance Model – Golden Path IDP (Deprecated)
type: policy
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 01_GOVERNANCE
  - 05_OBSERVABILITY_DECISIONS
  - 28_SECURITY_FLOOR_V1
  - 29_CD_DEPLOYMENT_CONTRACT
status: deprecated
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# Governance Model – Golden Path IDP (Deprecated)

Doc contract:

- Purpose: Record the previous V1 governance draft for reference.
- Owner: platform
- Status: deprecated
- Review cadence: as needed
- Related: docs/10-governance/01_GOVERNANCE.md, docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md, docs/60-security/28_SECURITY_FLOOR_V1.md

This draft has been consolidated to reduce duplication and keep governance
authoritative.

Use these sources instead:

- Governance principles, operating model, and Backstage lens:
  `docs/10-governance/01_GOVERNANCE.md`
- Observability ownership and tooling boundaries:
  `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`
- Delivery and change control contracts:
  `docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md`
- Security baseline:
  `docs/60-security/28_SECURITY_FLOOR_V1.md`
