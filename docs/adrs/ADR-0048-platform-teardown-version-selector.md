---
id: ADR-0048-platform-teardown-version-selector
title: 'ADR-0048: Versioned teardown runners with selectable entrypoint'
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
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
- 15_TEARDOWN_AND_CLEANUP
- ADR-0048
---

# ADR-0048: Versioned teardown runners with selectable entrypoint

Filename: `ADR-0048-platform-teardown-version-selector.md`

- **Status:** Proposed
- **Date:** 2025-12-30
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh`, `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v2.sh`, `.github/workflows/ci-teardown.yml`, `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Teardown reliability depends on managed-service cleanup timing (LBs/ENIs) and
Terraform destroy behaviors. Iterating on teardown logic is necessary, but
changing the primary teardown script directly increases risk and makes rollback
unclear when a change regresses CI reliability.

We need a safe way to test new teardown behavior in CI without disrupting the
default path.

---

## Decision

We will maintain two teardown runner entrypoints:

- **v1**: the stable default (`goldenpath-idp-teardown.sh`)
- **v2**: the iteration track (`goldenpath-idp-teardown-v2.sh`)

CI and Makefile usage will accept a `TEARDOWN_VERSION` selector (`v1` or `v2`).
CI defaults to `v1` and only uses `v2` when explicitly selected.

---

## Scope

Applies to:

- CI teardown workflow selection.
- Manual Makefile teardown targets.

Does not apply to:

- Bootstrap or infra apply flows.
- Orphan cleanup scripts (separate entrypoints).

---

## Consequences

### Positive

- Enables safer iteration and rollback for teardown logic.
- Keeps the default path stable while testing new behavior.
- Makes experimentation explicit and auditable in CI inputs.

### Tradeoffs / Risks

- Additional scripts to maintain in sync where appropriate.
- Potential for divergence if v2 is not reviewed back into v1.

### Operational impact

- Operators must select v2 explicitly when testing new teardown behavior.
- Documentation and runbooks must state the selection mechanism.

---

## Alternatives considered

- **Edit v1 in place:** faster but risks breaking the default path.
- **Branch-only experiments:** adds repo branching overhead and less visibility in CI.
- **Feature flags inside a single script:** keeps one file but increases script complexity.

---

## Follow-ups

- Document `TEARDOWN_VERSION` in teardown docs and CI contract.
- Track v2 changes and promote into v1 when validated.

---

## Notes

If v2 becomes the stable default, publish a new ADR and mark this one as
Superseded.
