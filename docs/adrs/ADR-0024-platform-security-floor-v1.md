---
id: ADR-0024
title: ADR-0024: Security floor for V1
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
relates_to: []
---

# ADR-0024: Security floor for V1

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security | Governance
- **Related:** docs/10-governance/01_GOVERNANCE.md, docs/60-security/22_CONTAINER_REGISTRY_STANDARD.md, docs/60-security/27_CI_IMAGE_SCANNING.md

---

## Context

We need a minimal, non-negotiable security baseline that reduces catastrophic risk without slowing
delivery. V1 must be secure-by-default and leave heavier DevSecOps capabilities to V2.

---

## Decision

> We will establish a V1 security floor with a small set of mandatory guardrails.

This floor is the minimum for platform and reference workloads; teams can exceed it.

---

## Scope

Applies to platform-owned and reference workloads in this repository. It does not mandate advanced
DevSecOps controls (SBOM signing, runtime agents) in V1.

---

## Consequences

### Positive

- Prevents high-risk mistakes without heavy process.
- Keeps delivery deterministic and low-friction.
- Creates a clear baseline for future DevSecOps layers.

### Tradeoffs / Risks

- Does not provide full compliance posture.
- Relies on CI and GitOps for enforcement.

### Operational impact

- Maintain the V1 checklist and keep it aligned with CI and governance.
- Document exceptions explicitly.

---

## Alternatives considered

- Full DevSecOps in V1 (rejected: too heavy for current delivery maturity).
- No explicit baseline (rejected: inconsistent and risky).

---

## Follow-ups

- Publish the V1 checklist in a living document.
- Add a governance reference to the V1 floor.

---

## Notes

V2 can introduce SBOMs, signing, and runtime security once delivery is stable.
