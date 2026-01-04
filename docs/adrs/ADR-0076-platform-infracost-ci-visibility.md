---
id: ADR-0076
title: 'ADR-0076: Lightweight CI cost visibility with Infracost'
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
  - ADR-0076
  - CL-0030
---

# ADR-0076: Lightweight CI cost visibility with Infracost

Filename: `ADR-0076-platform-infracost-ci-visibility.md`

- **Status:** Implemented
- **Date:** 2026-01-04
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** docs/10-governance/06_COST_GOVERNANCE.md, docs/70-operations/40_COST_VISIBILITY.md, docs/changelog/entries/CL-0030-infracost-ci-visibility.md

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

We want early, low-friction cost visibility for Terraform changes without
blocking delivery. Cost information should surface in PRs to build a habit of
cost awareness before introducing hard gates.

## Decision

We will integrate Infracost into the PR Terraform plan workflow as a
lightweight, advisory cost signal.

- Cost output is posted as a PR comment.
- The check does not block PRs at this stage.
- A missing API key skips the cost step without failing the plan.

## Scope

Applies to:

- PR Terraform plan workflow in `.github/workflows/pr-terraform-plan.yml`.
- Terraform changes in `envs/*` that produce a plan JSON.

Does not apply to:

- Apply workflows or production promotion gating.
- Non-Terraform changes.

## Consequences

### Positive

- Cost impact is visible during review.
- Low operational overhead to start building cost discipline.
- Clear path to add diff baselines and budget gates later.

### Tradeoffs / Risks

- Advisory-only: cost spikes can still merge without review.
- Infracost accuracy depends on provider pricing updates and plan fidelity.

### Operational impact

- Requires `INFRACOST_API_KEY` secret to be configured.
- Owners should monitor cost drift and decide when to add thresholds.

## Alternatives considered

- No cost tooling: rejected due to lack of early visibility.
- Immediate hard budget gates: rejected to avoid blocking iteration early.

## Follow-ups

- Add baseline diff comparisons (main vs PR) when the team is ready.
- Consider opt-in budget thresholds after a period of observation.

## Notes

Initial rollout is intentionally non-blocking and can be tightened later.
