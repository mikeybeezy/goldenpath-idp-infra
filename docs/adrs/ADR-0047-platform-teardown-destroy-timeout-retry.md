---
id: ADR-0047-platform-teardown-destroy-timeout-retry
title: 'ADR-0047: Retry Terraform destroy after timeout with cluster-scoped LB cleanup'
type: adr
status: active
lifecycle: active
version: '1.0'
relates_to:
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0045
  - ADR-0045-platform-teardown-lb-delete-default
  - ADR-0047
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0047: Retry Terraform destroy after timeout with cluster-scoped LB cleanup

Filename: `ADR-0047-platform-teardown-destroy-timeout-retry.md`

- **Status:** Proposed
- **Date:** 2025-12-30
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`, `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh`, `docs/adrs/ADR-0045-platform-teardown-lb-delete-default.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Teardown can stall when Terraform destroy reaches subnet deletion while
Kubernetes-created Network Load Balancer ENIs are still present. The LB cleanup
step removes services, but AWS eventual consistency can leave ENIs for several
minutes. This causes long-running pipeline hangs and intermittent failures.

Operational constraints observed:

- Managed-service ENIs cannot be detached or deleted directly.
- ENIs can persist after LB deletion for minutes to hours.
- ENI counts per LB vary with load; tags may be incomplete.
- Terraform cannot observe internal cleanup, so destroy waits can hang.

We need a bounded, repeatable teardown that avoids stuck pipelines while keeping
the forced cleanup scoped to only the cluster’s Kubernetes-managed LBs.

---

## Decision

We will cap Terraform destroy with a timeout. If the timeout is hit or
LoadBalancer ENIs remain, teardown will:

1. Re-check for remaining LB ENIs.
2. Delete Load Balancers **only** when they are cluster-tagged and have
   Kubernetes service tags.
3. Print a forced-cleanup summary (ENIs + LB names).
4. Retry Terraform destroy once.

---

## Scope

Applies to teardown via `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh`
for ephemeral clusters. It does not apply to manual AWS-only teardown or
non-Kubernetes-managed load balancers.

---

## Consequences

### Positive

- Teardown no longer hangs indefinitely on subnet dependency violations.
- Forced cleanup is scoped to cluster-tagged Kubernetes LBs.
- Operators get an audit-friendly summary of forced deletions.

### Tradeoffs / Risks

- Requires additional IAM permissions for LB/ENI discovery and deletion.
- If tagging is incorrect or inconsistent, cleanup may skip required LBs.
- Adds a retry path that can mask upstream misconfigurations if overused.

### Operational impact

- Teardown roles must allow LB tag discovery and deletion.
- Operators should review the forced-cleanup summary when it occurs.

---

## Alternatives considered

- **Wait indefinitely for ENIs:** rejected due to pipeline stalls.
- **Manual cleanup only:** rejected due to high operator toil.
- **Delete all LBs in the VPC:** rejected as too risky and not scoped.

---

## Follow-ups

- Ensure teardown IAM roles include required LB/ENI permissions.
- Keep `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md` updated with timeout/retry behavior.

---

## Notes

This ADR extends ADR-0045 by adding a bounded timeout and retry to handle
eventual consistency without relying on manual intervention.
