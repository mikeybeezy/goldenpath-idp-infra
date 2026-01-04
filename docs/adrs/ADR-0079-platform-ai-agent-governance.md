---
id: ADR-0079-platform-ai-agent-governance
title: 'ADR-0079: AI Agent Governance and Auditability'
type: adr
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
- 07_AI_AGENT_GOVERNANCE
- 26_AI_AGENT_PROTOCOLS
- ADR-0079
- AI_CHANGELOG
---

# ADR-0079: AI Agent Governance and Auditability

Date: 2026-01-03
Status: Proposed
Owners: platform

## Context

AI agents are increasingly used for documentation, workflow updates, and
automation changes. Without explicit governance, changes risk drift, poor
traceability, and inconsistent QA.

We need lightweight rules that preserve speed while ensuring auditability,
guardrails, and reproducible outcomes.

## Decision

Adopt an AI governance layer with three concrete artifacts and a tiered
authority model:

1. `docs/10-governance/07_AI_AGENT_GOVERNANCE.md`
   - Defines authority, guardrails, auditability, QA expectations, and
     escalation rules.
2. `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md`
   - Detailed operating procedures aligned to governance policy.
3. `docs/90-doc-system/AI_CHANGELOG.md`
   - A living ledger to record AI-driven changes with evidence.

The tiered model defines what actions are allowed per risk class (read-only,
write isolated, safe execution, human-only high risk).

## Consequences

**Positive**

- Clear rules for safe AI use, with traceable evidence.
- Faster onboarding and fewer repeated debates.
- Consistent QA expectations (green gate, evidence links).

**Negative**

- Additional documentation overhead per change.
- Requires discipline to keep the ledger and references current.

## Alternatives considered

1. **No formal governance, rely on ad-hoc reviews.**
   - Rejected: insufficient auditability and inconsistent QA.
2. **Only add protocols (no governance policy).**
   - Rejected: protocols alone lack enforcement and escalation rules.
3. **Tooling-only enforcement (no docs).**
   - Rejected: obscures reasoning and reduces transferability.

## Related

- docs/10-governance/07_AI_AGENT_GOVERNANCE.md
- docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md
- docs/90-doc-system/AI_CHANGELOG.md
