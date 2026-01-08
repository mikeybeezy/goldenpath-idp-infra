---
id: ADR-0021-platform-pr-terraform-plan
title: 'ADR-0021: PR Terraform plan with automated comments'
type: adr
status: active
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0021
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0021: PR Terraform plan with automated comments

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Delivery | Governance
- **Related:** docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md, docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, .github/workflows/pr-terraform-plan.yml

---

## Context

We want Terraform plan feedback on pull requests without introducing Atlantis or requiring manual
copy/paste. The goal is to surface infrastructure changes early while keeping apply manual and
controllable.

---

## Decision

> We will run a PR-only Terraform plan and post the output as a PR comment.

The plan runs against `envs/dev` without a backend and never applies changes.

---

## Scope

Applies to Terraform changes in this repository and PR workflows.

---

## Consequences

### Positive

- Early visibility of infra changes in PRs.
- No extra infrastructure (Atlantis) required.
- Keeps apply gated and manual.

### Tradeoffs / Risks

- Plan output may be truncated for large changes.
- Plans run without backend state, which can reduce accuracy.

### Operational impact

- Maintain the PR plan workflow and comment behavior.
- Keep the plan scope limited to avoid leaking sensitive output.

---

## Alternatives considered

- Atlantis (rejected for now: additional service to operate).
- Terraform Cloud (rejected for now: additional cost and dependency).

---

## Follow-ups

- Monitor plan output size and adjust truncation if needed.
- Consider read-only backend access if plan accuracy becomes a problem.

---

## Notes

This is a fast feedback loop; CI remains the source of truth.
