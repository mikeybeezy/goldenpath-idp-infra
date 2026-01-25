<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0032-ai-agent-governance
title: 'Changelog: AI agent governance and auditability'
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
  - ADR-0079-platform-ai-agent-governance
  - CL-0032-ai-agent-governance
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

# Changelog: AI agent governance and auditability

Date: 2026-01-03
Owner: platform

## Summary

- Add AI governance policy for guardrails, auditability, and QA expectations.
- Add AI protocols for operator and agent execution rules.
- Add AI change log ledger and link in doc index.
- Clarify PR monitoring tasks and human-only merge approval.
- Add tiered authority model and core principle for human ownership.
- Add agent protocol guarantees for idempotence, traceability, and reviewability.

## References

- ADR: docs/adrs/ADR-0079-platform-ai-agent-governance.md
- Docs: docs/10-governance/07_AI_AGENT_GOVERNANCE.md
- Docs: docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md
- Docs: docs/90-doc-system/AI_CHANGELOG.md
