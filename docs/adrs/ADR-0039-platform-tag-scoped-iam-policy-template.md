---
id: ADR-0039-platform-tag-scoped-iam-policy-template
title: 'ADR-0039: Tag-Scoped IAM Policy Template for Destructive Automation'
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
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
  - 01_GOVERNANCE
  - 01_TAG_SCOPED_POLICY_TEMPLATE
  - 35_RESOURCE_TAGGING
  - ADR-0037
  - ADR-0037-platform-resource-tagging-policy
  - ADR-0039
---

# ADR-0039: Tag-Scoped IAM Policy Template for Destructive Automation

- **Status:** Proposed
- **Date:** 2025-12-29
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance / Operations
- **Related:** `docs/10-governance/01_GOVERNANCE.md`, `docs/10-governance/35_RESOURCE_TAGGING.md`, `docs/policies/01_TAG_SCOPED_POLICY_TEMPLATE.md`, `docs/adrs/ADR-0037-platform-resource-tagging-policy.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Teardown and cleanup automation requires destructive permissions. Broad IAM
policies raise the risk of deleting unintended resources, especially in shared
accounts. We already enforce a platform-wide tagging policy, so tags are the
most reliable guardrail for scoping deletion actions.

We need a standard, reusable policy template that enforces tag-scoped deletes
while keeping read-only discovery unblocked.

---

## Decision

We will adopt a **tag-scoped IAM policy template** for destructive automation.

- Delete actions must be scoped to `BuildId` and `Environment` tags.
- Read-only discovery actions remain unscoped.
- The template lives in `docs/policies/01_TAG_SCOPED_POLICY_TEMPLATE.md`.

---

## Scope

Applies to:

- CI roles that perform teardown or orphan cleanup
- Any automation that deletes or mutates AWS resources

Does not apply to:

- Read-only plan roles
- Human break-glass roles (separate governance)

---

## Consequences

### Positive

- Reduces blast radius of destructive automation.
- Makes cleanup intent auditable and consistent.
- Enforces tag hygiene across the platform.

### Tradeoffs / Risks

- Missing tags will block automated cleanup.
- Requires consistent tagging in all provisioning paths.

### Operational impact

- Update CI cleanup roles to use the template.
- Ensure BuildId and Environment tags are always present.

---

## Alternatives considered

- **Broad delete permissions:** rejected due to high blast radius.
- **Manual-only cleanup:** rejected due to high toil and slow recovery.
- **Separate cleanup account:** deferred; too heavy for V1.

---

## Follow-ups

- Apply the template to teardown/orphan cleanup policies.
- Add checks for missing tags in CI or policy-as-code.

---

## Notes

If tag coverage is unreliable, cleanup will fail by design. This is acceptable
because it surfaces tagging gaps early.
