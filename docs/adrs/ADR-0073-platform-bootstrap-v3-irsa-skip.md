# ADR-0073: Bootstrap v3 skips Terraform IRSA apply in Stage 3B

- **Status:** Proposed
- **Date:** 2026-01-02
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Delivery | Reliability
- **Related:** `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh`, `.github/workflows/ci-bootstrap.yml`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Bootstrap Stage 3B runs a targeted Terraform apply for IRSA service accounts.
When the service accounts already exist, the plan reports "No changes" and the
bootstrap guard treats that as a failure, blocking otherwise healthy runs.

---

## Decision

We will introduce a **v3 bootstrap script** that skips Terraform IRSA apply in
Stage 3B and only validates that the required service accounts exist.

---

## Scope

Applies to bootstrap runs that select `BOOTSTRAP_VERSION=v3`.

---

## Consequences

### Positive

- Bootstrap becomes idempotent even when IRSA resources already exist.
- Fewer false failures when IRSA was created during build/apply.

### Tradeoffs / Risks

- IRSA creation is no longer performed during v3 bootstrap.
- IRSA drift is not corrected by bootstrap and must be handled in build/apply.

### Operational impact

- Operators should create IRSA service accounts during build/apply, or use v1/v2
  when bootstrap should create them.

---

## Alternatives considered

- **Patch the v2 guard to accept "No changes":** still runs Terraform in
  bootstrap; more moving parts for a stage intended to be validation only.
- **Expose an IRSA toggle only:** relies on manual input and is easy to mis-set.


