---
id: ADR-0072
title: 'ADR-0072: PR checklist template in PR gates guide'
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
- 24_PR_GATES
- ADR-0072
------

# ADR-0072: PR checklist template in PR gates guide

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance | Documentation
- **Related:** `.github/pull_request_template.md`, `docs/80-onboarding/24_PR_GATES.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

The PR guardrails require checklist selections in the PR body. The checklist
template lives in GitHub, but contributors often do not discover it until the
PR guard fails. This adds friction for onboarding and increases the number of
blocked PRs for simple documentation changes.

---

## Decision

We will include a copy of the PR checklist template in the PR gates guide
(`docs/80-onboarding/24_PR_GATES.md`) with a note that the canonical template
remains in `.github/pull_request_template.md`.

---

## Scope

Applies to onboarding and PR guardrails documentation only.

---

## Consequences

### Positive

- Contributors can copy/paste the checklist without leaving the docs.
- Fewer failed PR guardrail checks due to missing selections.

### Tradeoffs / Risks

- The copy can drift from the canonical template if the GitHub template changes.

### Operational impact

- Update the PR gates guide whenever `.github/pull_request_template.md` changes.

---

## Alternatives considered

- **Link only to the GitHub template:** lower maintenance but higher friction.
- **Embed a screenshot:** quickly becomes stale and cannot be copied.
