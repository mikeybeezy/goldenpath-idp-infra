---
id: ADR-0064-platform-dev-bootstrap-defaults
title: 'ADR-0064: Dev bootstrap defaults off for k8s resources and storage'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0064-platform-dev-bootstrap-defaults
  - CL-0013-dev-bootstrap-defaults-off
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0064: Dev bootstrap defaults off for k8s resources and storage

Filename: `ADR-0064-platform-dev-bootstrap-defaults.md`

- **Status:** Accepted
- **Date:** 2026-01-02
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `envs/dev/terraform.tfvars`, `bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Recent bootstrap runs failed when Terraform-managed Kubernetes service accounts
and storage add-on checks were enabled by default. The CI bootstrap role and
cluster readiness were not consistently aligned for those steps.

We need a safe default that keeps bootstrap reliable while we stabilize access
and storage prerequisites.

---

## Decision

We will default `enable_k8s_resources` and `enable_storage_addons` to **false**
in `envs/dev/terraform.tfvars`. Operators can opt in per run when prerequisites
are satisfied.

---

## Scope

Applies to:

- Dev environment defaults in `envs/dev/terraform.tfvars`

Does not apply to:

- Staging/prod defaults
- Manual, opt-in runs that explicitly enable these features

---

## Consequences

### Positive

- Bootstrap succeeds without requiring IRSA or storage add-on readiness.
- Operators regain control over when to enable the extra steps.

### Tradeoffs / Risks

- Dev defaults no longer validate storage readiness by default.
- IRSA service-account creation requires explicit opt-in.

### Operational impact

- Operators must enable these flags when they want storage add-ons and
  Terraform-managed service accounts.

---

## Alternatives considered

- Keep defaults enabled: rejected due to repeated bootstrap failures.
- Remove checks entirely: rejected; opt-in path is still needed.

---

## Follow-ups

- Restore defaults once CI access and storage prerequisites are consistently met.

---

## Notes

This ADR is specific to dev defaults and may be superseded once bootstrap
stability is confirmed.
