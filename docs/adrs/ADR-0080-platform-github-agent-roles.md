---
id: ADR-0080
title: 'ADR-0080: GitHub App Roles for AI/Automation Access'
type: adr
owner: platform-team
status: active
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

- ADR-0080

---

# ADR-0080: GitHub App Roles for AI/Automation Access

Date: 2026-01-03
Status: Proposed
Owners: platform

## Context

We need a way to grant AI and automation roles without creating new human
GitHub accounts. The solution must be auditable, least-privilege, and easy to
rotate.

## Decision

Adopt GitHub Apps as the default mechanism for AI/automation access, with
minimal permissions scoped to specific repositories.

## Consequences

**Positive**

- Fine-grained permissions and auditability.
- Tokens are short-lived and easier to rotate.
- No human accounts required.

**Negative**

- Requires App setup and lifecycle management.
- Additional documentation and onboarding steps.

## Alternatives considered

1. **Service accounts (bot users)**
   - Rejected: requires additional user accounts and broader permissions.
2. **Personal access tokens**
   - Rejected: long-lived secrets, higher risk and poorer auditability.

## Related

- docs/10-governance/08_GITHUB_AGENT_ROLES.md
- docs/10-governance/07_AI_AGENT_GOVERNANCE.md
