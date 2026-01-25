---
id: CL-0034-pr-template-enforcement
title: 'Changelog: PR template enforcement and CI iteration'
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
  - CL-0034-pr-template-enforcement
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-04
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# Changelog: PR template enforcement and CI iteration

Date: 2026-01-03
Owner: platform

## Summary

- Enforce PR template header and reject escaped newlines in guardrails.
- Document template-based PR creation and default CI iteration until green.
- Update PR guardrails guidance to reflect template enforcement.

## References

- Workflow: .github/workflows/pr-guardrails.yml
- Docs: docs/10-governance/04_PR_GUARDRAILS.md
- Docs: docs/80-onboarding/24_PR_GATES.md
- Docs: docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md
