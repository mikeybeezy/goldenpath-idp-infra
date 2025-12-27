# ADR-0017: Policy as code for infrastructure changes

- **Status:** Proposed
- **Date:** 2025-12-26
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `docs/20_CI_ENVIRONMENT_SEPARATION.md`, `.github/workflows/infra-terraform.yml`
- --

## Context

As the platform scales, we need consistent guardrails that prevent unsafe infrastructure and
application changes without relying solely on manual review. With Backstage as our first client,
we must apply policy as code to both infrastructure and application delivery so the platform is
safe by default and the developer experience reflects our own standards.

- --

## Decision

> We will enforce policy as code for infrastructure and application changes in CI.

Baseline requirements:
- Evaluate Terraform plans against a small, maintained policy set.
- Block applies when policies fail.
- Keep policies minimal and focused on high-impact risks.

- --

## Scope

Applies to infrastructure and application changes in this repository, including Terraform and
application delivery workflows.

- --

## Consequences

### Positive

- Consistent, automated enforcement of critical guardrails.
- Safer changes as environments and contributors grow.
- Clear audit trail of policy decisions.

### Tradeoffs / Risks

- Requires policy authoring and maintenance.
- False positives can slow delivery if rules are too strict.

### Operational impact

- Platform team maintains policy rules and updates them as requirements evolve.
- CI workflows incorporate policy checks before apply.

- --

## Alternatives considered

- Manual reviews only (rejected: inconsistent and non-scalable).
- Environment-specific ad hoc checks (rejected: duplication and drift).

- --

## Follow-ups

- Select the policy engine (e.g., OPA/Conftest or Checkov).
- Define the initial policy set for infrastructure and applications.
- Wire the checks into `infra-terraform.yml` and relevant application workflows.

- --

## Notes

Keep the policy set intentionally small to avoid over-blocking while the platform matures.
