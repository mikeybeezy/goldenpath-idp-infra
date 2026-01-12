---
id: ADR-0041-platform-orphan-cleanup-deletion-order
title: 'ADR-0041: Deterministic orphan cleanup deletion order'
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
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0038
  - ADR-0038-platform-teardown-orphan-cleanup-gate
  - ADR-0041
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

# ADR-0041: Deterministic orphan cleanup deletion order

Filename: `ADR-0041-platform-orphan-cleanup-deletion-order.md`

- **Status:** Proposed
- **Date:** 2025-12-29
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`, `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh`, `docs/adrs/ADR-0038-platform-teardown-orphan-cleanup-gate.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Orphan cleanup can fail when AWS resources are deleted out of dependency order
(for example, trying to delete a subnet that still has ENIs or a route table
that is still associated). We need a deterministic deletion order to make the
cleanup routine reliable and predictable.

Constraints:

- Cleanup must remain BuildId-tagged and avoid state backends.
- The routine should be safe for repeated runs (idempotent-ish).

---

## Decision

We will enforce and document a deterministic deletion order in the orphan
cleanup script:

1) EKS node groups → EKS cluster
2) Load balancers
3) EC2 instances
4) ENIs (unattached only)
5) IAM roles (BuildId-tagged)
6) NAT gateways
7) Elastic IPs
8) Route tables (detach associations, skip main)
9) Subnets
10) Security groups (non-default)
11) Internet gateways (detach then delete)
12) VPCs

This order is implemented in `cleanup-orphans.sh` and documented in the teardown
runbook.

---

## Scope

Applies to:

- `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh`
- Orphan cleanup execution in CI and manual runs

Does not apply to:

- Terraform destroy (which follows provider dependency logic)
- Manual cleanup outside the BuildId-tagged orphan scope

---

## Consequences

### Positive

- Fewer cleanup failures due to dependency violations.
- Safer, repeatable cleanup runs in CI.
- Clear operator expectations for cleanup behavior.

### Tradeoffs / Risks

- Order is opinionated and may require updates as new resource types are added.
- IAM role cleanup can fail if roles are still in use; retries may still be needed.

### Operational impact

- Operators should follow the documented order when manually cleaning resources.
- The cleanup script continues to avoid modifying Terraform state backends.

---

## Alternatives considered

- **Best-effort deletion in any order:** rejected due to frequent AWS dependency failures.
- **Rely only on Terraform destroy:** rejected because orphan cleanup is needed
  when Terraform state is missing or invalid.

---

## Follow-ups

- Add retries for IAM role deletion if AWS reports roles in use.
- Extend order when new resource types are added to cleanup.

---

## Notes

If this decision changes, create a new ADR and supersede this one.
