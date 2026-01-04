---
id: ADR-0016
title: 'ADR-0016: CI environment separation and manual promotion gates'
type: adr
owner: platform-team
status: active
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
- ADR-0016
------

# ADR-0016: CI environment separation and manual promotion gates

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `.github/workflows/infra-terraform.yml`, `docs/10-governance/01_GOVERNANCE.md`

---

## Context

We need a CI/CD model that scales safely from early-stage usage to later growth without frequent
rework. Infrastructure changes must be reviewed, environment-scoped, and applied with explicit
human control while still keeping a single, consistent workflow for contributors.

---

## Decision

> We will separate CI environments by name and enforce manual apply gates per environment.

Core rules:

- One workflow handles all environments via inputs.
- Each environment uses a dedicated GitHub Environment name (`dev`, `test`, `staging`, `prod`).
- Apply steps are gated by an explicit workflow input (`apply=true`) at dispatch time.
- IAM roles and state backends are environment-scoped.

---

## Scope

Applies to infrastructure workflows and environment separation in this repository.

---

## Consequences

### Positive

- Clear approval boundaries for each environment.
- A single workflow scales without duplication.
- Environment-specific roles and state reduce blast radius.

### Tradeoffs / Risks

- Requires GitHub Environment configuration and reviewer setup.
- Slightly more workflow complexity to map env inputs to role/backends.

### Operational impact

- Maintain per-environment IAM roles and backend resources.
- Require explicit operator intent by using a manual apply toggle at workflow dispatch.

---

## Alternatives considered

- Separate workflows per environment (rejected as primary path; allowed for stricter separation).
- CI-only applies without manual gates (rejected for production safety).

---

## Follow-ups

- Document the current CI environment separation implementation.
- Add environment-specific role and backend mappings for test/staging/prod.

---

## Notes

Option 3 (separate workflows per environment) remains an approved alternative for teams that
prioritize stronger boundaries or simpler per-env readability.

GitHub Environments remain a future option for manual approval gates if licensing and repo
requirements make it viable.
