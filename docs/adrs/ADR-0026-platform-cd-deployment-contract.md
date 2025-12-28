# ADR-0026: CD deployment contract

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance | Delivery
- **Related:** docs/01_GOVERNANCE.md, docs/29_CD_DEPLOYMENT_CONTRACT.md, docs/21_CI_ENVIRONMENT_CONTRACT.md, docs/02_PLATFORM_BOUNDARIES.md
---

## Context

GoldenPath uses GitOps-based continuous deployment to apply and reconcile desired state across
environments. We need to make deployment expectations explicit to ensure deterministic promotion,
clear rollback semantics, and auditable outcomes independent of CI logs.

---

## Decision

> GoldenPath defines an explicit CD deployment contract.

The contract specifies:

- the minimum deployment metadata required
- the source of truth for desired and actual state
- the criteria for deployment success
- the promotion and rollback model

This contract applies to platform workloads and serves as the reference for team workloads.

---

## Scope

Applies to deployment semantics in this repository. It does not redefine CI input contracts or
application behavior.

---

## Consequences

### Positive

- Deployments become deterministic and auditable.
- Promotion semantics are consistent and explicit.
- Rollbacks are simplified and reliable.
- CI and CD responsibilities are clearly separated.

### Tradeoffs / Risks

- Requires minimal upfront documentation and discipline.
- Introduces an explicit contract that must be maintained over time.

---

## Alternatives considered

- Relying on CI logs as the deployment record (rejected: lacks durability and clarity).
- Ad-hoc promotion and rollback mechanisms (rejected: inconsistency and operator risk).
- Controller-specific behavior only (rejected: couples semantics to a single tool).

---

## Follow-ups

- Keep the contract aligned with GitOps workflows.
- Add a release receipt format if needed.

---

## Notes

The contract may evolve independently; the ADR records the decision to formalize it.
