---
id: ADR-0037-platform-resource-tagging-policy
title: 'ADR-0037: Platform resource tagging policy'
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
- 01_GOVERNANCE
- 35_RESOURCE_TAGGING
- ADR-0037
---

# ADR-0037: Platform resource tagging policy

- **Status:** Accepted
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `docs/10-governance/01_GOVERNANCE.md`, `docs/10-governance/35_RESOURCE_TAGGING.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

GoldenPath creates and tears down short-lived environments frequently. Without
consistent tags, it is difficult to audit cost, identify owners, and safely
clean up orphans. We already rely on tags for BuildId-based cleanup and
reporting, but tagging is not consistently applied across all resources.

---

## Decision

We will enforce a **platform-wide tagging policy** and apply explicit tags to
all taggable resources created by Terraform and bootstrap tooling, including
EKS add-ons and OIDC providers.

---

## Scope

Applies to:

- Terraform-managed AWS resources in all environments.
- Bootstrap-created AWS resources.
- EKS add-ons and OIDC providers for consistency and visibility.

Does not apply to:

- Non-taggable AWS resources (e.g., IAM attachments, route table associations).
- Kubernetes-native resources (use labels/annotations instead).

---

## Consequences

### Positive

- Cleaner cost attribution and audit trails.
- Faster and safer orphan cleanup.
- Consistent operator experience across environments.

### Tradeoffs / Risks

- Requires discipline to keep tags in sync across modules and tooling.
- Non-taggable resources must be cleaned through their parent resources.

### Operational impact

- Tag standards must be reflected in Terraform modules and bootstrap scripts.
- Orphan cleanup relies on tag presence and accuracy.

---

## Alternatives considered

- Rely on AWS cost allocation tags only (insufficient for cleanup).
- Tag only primary resources (misses add-ons and secondary resources).

---

## Follow-ups

- Add a living tag index and update governance references.
- Add explicit tags for EKS add-ons and OIDC providers.

---

## Notes

Non-taggable resources are removed indirectly during teardown by deleting their
parent resources or by using label/selector-based cleanup for Kubernetes.
