# ADR-0016: CI environment separation and manual promotion gates

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `.github/workflows/infra-terraform.yml`, `docs/01_GOVERNANCE.md`
- --

## Context

We need a CI/CD model that scales safely from early-stage usage to later growth without frequent
rework. Infrastructure changes must be reviewed, environment-scoped, and applied with explicit
human control while still keeping a single, consistent workflow for contributors.

- --

## Decision

> We will separate CI environments by name and enforce manual apply gates per environment.

Core rules:
- One workflow handles all environments via inputs.
- Each environment uses a dedicated GitHub Environment name (`dev`, `test`, `staging`, `prod`).
- Apply steps are gated by Environment approvals.
- IAM roles and state backends are environment-scoped.

- --

## Scope

Applies to infrastructure workflows and environment separation in this repository.

- --

## Consequences

### Positive

- Clear approval boundaries for each environment.
- A single workflow scales without duplication.
- Environment-specific roles and state reduce blast radius.

### Tradeoffs / Risks

- Requires GitHub Environment configuration and reviewer setup.
- Slightly more workflow complexity to map env inputs to role/backends.

### Operational impact

- Create GitHub Environments for each stage with required reviewers.
- Maintain per-environment IAM roles and backend resources.

- --

## Alternatives considered

- Separate workflows per environment (rejected as primary path; allowed for stricter separation).
- CI-only applies without manual gates (rejected for production safety).

- --

## Follow-ups

- Document the current CI environment separation implementation.
- Add environment-specific role and backend mappings for test/staging/prod.

- --

## Notes

Option 3 (separate workflows per environment) remains an approved alternative for teams that
prioritize stronger boundaries or simpler per-env readability.
