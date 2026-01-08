---
id: pull_request_template
title: Pull Request Template
type: template
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle: active
category: platform
version: 1.0
dependencies: []
relates_to:
  - 24_PR_GATES
  - 04_PR_GUARDRAILS
supported_until: 2028-01-01
breaking_change: false
---

Select at least one checkbox per section by changing `[ ]` to `[x]`.

## Change Type
- [ ] Feature
- [ ] Bug fix
- [ ] Infra change
- [ ] Governance / Policy

## Decision Impact
- [ ] Requires ADR
- [ ] Updates existing ADR
- [ ] No architectural impact

## Production Readiness
- [ ] Readiness checklist completed
- [ ] No production impact

## Testing / Validation
- [ ] Plan/apply link provided (paste below)
- [ ] Test command or run ID provided (paste below)
- [ ] Not applicable

Testing/Validation details:
- Plan/apply link:
- Test command/run:

## Risk & Rollback
- [ ] Rollback plan documented (link or notes below)
- [ ] Data migration required
- [ ] No data migration
- [ ] Not applicable

Rollback notes/link:

## Notes / Summary (optional)
-
