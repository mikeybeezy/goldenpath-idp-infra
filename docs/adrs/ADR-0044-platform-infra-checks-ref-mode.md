---
id: ADR-0044-platform-infra-checks-ref-mode
title: 'ADR-0044: Configurable ref for infra checks dispatch'
type: adr
status: superseded
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 04_PR_GUARDRAILS
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0044-platform-infra-checks-ref-mode
  - ADR-0046-platform-pr-plan-validation-ownership
  - READINESS_CHECKLIST
  - audit-20260103
supersedes: []
superseded_by: ADR-0046
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0044: Configurable ref for infra checks dispatch

Filename: `ADR-0044-platform-infra-checks-ref-mode.md`

- **Status:** Superseded by `ADR-0046-platform-pr-plan-validation-ownership.md`
- **Date:** 2025-12-30
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `.github/workflows/pr-terraform-plan.yml`, `.github/workflows/infra-terraform.yml`, `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

PR Terraform Plan dispatches Infra Terraform Checks for validation. Teams need
clarity on where those checks run: on the PR branch, on the target branch, or
both. The default should remain simple, but we need a low-friction way to test
base vs head behavior without introducing additional workflows.

Constraints:

- Avoid adding new workflow layers.
- Keep the default behavior unchanged.

---

## Decision

We will add a repository variable to control which ref Infra Terraform Checks
dispatch to when triggered from the PR plan workflow:

- `INFRA_CHECKS_REF=head` (default) runs checks on the PR branch.
- `INFRA_CHECKS_REF=base` runs checks on the target branch.
- `INFRA_CHECKS_REF=both` runs checks on both refs.

---

## Scope

Applies to:

- PR-driven infra checks dispatch in CI
- Repo configuration via Actions variables

Does not apply to:

- Manual `infra-terraform.yml` runs
- Apply workflows (which remain manual)

---

## Consequences

### Positive

- Teams can test base vs head behavior without adding workflows.
- Default behavior remains unchanged and simple.

### Tradeoffs / Risks

- Adds one configuration surface area that can be mis-set.
- `both` doubles check workload when enabled.

### Operational impact

- Operators can set `INFRA_CHECKS_REF` in GitHub Actions variables.
- Default behavior is still head ref if unset or invalid.

---

## Alternatives considered

- **Separate workflows per ref:** rejected due to extra complexity.
- **Hardcode base ref:** rejected because it hides PR-branch validation.

---

## Follow-ups

- Document the variable in CI environment contract.

---

## Notes

This is a small control knob for CI ergonomics, not a policy change.
