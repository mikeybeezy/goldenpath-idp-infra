# ADR-0019: Pre-commit hooks as local quality gates

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance | Operations
- **Related:** docs/10-governance/01_GOVERNANCE.md, docs/80-onboarding/13_COLLABORATION_GUIDE.md, docs/40-delivery/24_PRE_COMMIT_HOOKS.md

---

## Context

We want fast, consistent feedback for contributors before changes reach CI. Local pre-commit hooks
can prevent common formatting and lint issues while keeping the CI pipeline authoritative. The
platform needs a lightweight, repeatable setup for new joiners.

---

## Decision

> We will require contributors to install pre-commit hooks locally and treat them as the default
> preflight checks for commits.

CI remains the source of truth; hooks reduce avoidable failures and shorten feedback loops.

---

## Scope

Applies to contributors working in this repository. This does not replace CI checks or merge
requirements.

---

## Consequences

### Positive

- Faster feedback for formatting and lint issues.
- Fewer avoidable CI failures.
- Consistent local workflow for new joiners.

### Tradeoffs / Risks

- Requires local tooling installation.
- Hooks may differ slightly from CI behavior.

### Operational impact

- Maintain a minimal pre-commit configuration.
- Document installation and troubleshooting steps.

---

## Alternatives considered

- CI-only checks (rejected: slower feedback, more churn).
- Optional hooks with no expectation (rejected: inconsistent developer experience).

---

## Follow-ups

- Add or update `.pre-commit-config.yaml`.
- Document hook setup and usage.
- Add a CI job to run the same checks as a safety net.

---

## Notes

Developers may bypass hooks only for urgent fixes, with a follow-up to restore compliance.
