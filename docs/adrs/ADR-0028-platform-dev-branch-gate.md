# ADR-0028: Dev branch gate before main

Filename: `ADR-0028-platform-dev-branch-gate.md`

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Delivery
- **Related:** `docs/21_CI_ENVIRONMENT_CONTRACT.md`, `docs/29_CD_DEPLOYMENT_CONTRACT.md`, `docs/01_GOVERNANCE.md`

---

## Context

We want quality gates that prove changes run in a real environment before they
reach `main`. Relying solely on plans or post-merge applies weakens the value of
the dev environment as a gate. A simple branch strategy can enforce a practical
pre-merge apply without introducing per-PR ephemeral environments.

## Decision

Introduce a **dev branch gate**:

- Feature branches merge into `dev`.
- `dev` applies to the shared dev environment.
- Only changes that pass in `dev` are promoted to `main`.

This keeps the dev environment as a shared gate while avoiding per-PR
environment cost.

## Scope

Applies to platform infrastructure and platform workloads. It defines the
minimum promotion path for changes that affect delivery rails or infrastructure.

## Consequences

### Positive

- Real apply happens before `main` changes.
- Clear promotion path with a shared dev gate.
- Lower cost than per-PR ephemeral environments.

### Tradeoffs / Risks

- Shared dev can become a bottleneck if multiple changes converge.
- Failures on `dev` block promotion to `main`.

### Operational impact

- `dev` becomes the pre-merge validation branch.
- Promotion requires a clean dev run before merging to `main`.

## Alternatives considered

- **PR-scoped dev environments:** better isolation but higher cost/complexity.
- **Plan-only gates:** cheaper but weaker quality signal.

## Follow-ups

- Update branch protection to require dev checks before `main`.
- Document the dev gate workflow in governance and onboarding.

## Diagram

```
Legend:
[PLAN] = terraform plan workflow (read-only role)
[APPLY] = terraform apply workflow (write role)
[STATE] = S3 + DynamoDB backend
-->    = trigger

+---------------------------+
|  Feature Branches (feat/*)|
|  - Devs implement change  |
+-------------+-------------+
              |
              | PR merge --> dev
              v
+---------------------------+        [QUALITY GATE]
|  dev branch (gate)        |  -------------------------+
|  - Shared pre-merge gate  |                           |
+-------------+-------------+                           |
              |                                         |
              | manual trigger                          |
              v                                         |
+---------------------------+                            |
|  [PLAN] infra-terraform   |                            |
|  - OIDC: TF_AWS_IAM_ROLE  |                            |
|  - init/plan (dev)        |                            |
+-------------+-------------+                            |
              |                                         |
              | manual trigger                          |
              v                                         |
+---------------------------+                            |
|  [APPLY] infra-terraform  |                            |
|  - OIDC: TF_AWS_IAM_ROLE  |                            |
|    _DEV_APPLY             |                            |
|  - apply dev              |                            |
+-------------+-------------+                            |
              |                                         |
              | success --> allow merge to main         |
              v                                         |
+---------------------------+                            |
|  main branch              | <--------------------------+
|  - Only after dev apply   |
+-------------+-------------+
              |
              | optional promotion
              v
+---------------------------+
|  staging / prod gates     |
|  - Manual promotion       |
|  - Separate roles         |
+---------------------------+

+---------------------------+
|  [STATE] Backend          |
|  - S3 bucket (dev state)  |
|  - DynamoDB lock table    |
+---------------------------+
```

## Notes

This decision balances quality gates with cost and operational simplicity.
