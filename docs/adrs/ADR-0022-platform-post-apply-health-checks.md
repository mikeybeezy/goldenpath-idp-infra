---
id: ADR-0022-platform-post-apply-health-checks
title: 'ADR-0022: Post-apply health checks for platform readiness'
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
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
- ADR-0022
---

# ADR-0022: Post-apply health checks for platform readiness

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Operations | Reliability
- **Related:** docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md, docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, .github/workflows/infra-terraform.yml

---

## Context

Terraform apply and bootstrap do not guarantee that the platform is usable. We need a deterministic,
binary signal that the environment is healthy after apply so that promotions and demos are safe and
repeatable.

---

## Decision

> We will add a post-apply health-check stage that validates core platform readiness.

The health check will verify:

- EKS is reachable and nodes are Ready.
- Argo CD root app is Synced and Healthy.
- Kong health endpoint returns success.

---

## Scope

Applies to apply workflows for dev/test/staging/prod environments.

---

## Consequences

### Positive

- Deterministic signal of platform readiness.
- Faster detection of bootstrap regressions.
- Clear, auditable CI outcome after apply.

### Tradeoffs / Risks

- Health checks may fail for transient conditions (timing, dependency lag).
- Requires clear conventions for app names and endpoints.

### Operational impact

- Maintain health-check scripts and expected endpoints.
- Document required inputs (cluster name, app name, health URL).
- Use a short retry/backoff to smooth transient readiness delays.

---

## Alternatives considered

- Manual spot checks (rejected: inconsistent, non-repeatable).
- Only check Terraform exit code (rejected: does not prove platform health).

---

## Follow-ups

- Define standard Argo root app naming per env.
- Document Kong health endpoint and namespace.
- Add the health-check job to the apply workflow.

---

## Notes

The health check is a gate; apply is considered successful only if readiness passes.
