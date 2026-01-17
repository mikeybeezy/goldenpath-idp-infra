---
id: ADR-0045-platform-teardown-lb-delete-default
title: 'ADR-0045: Default LB delete when ENIs persist during teardown'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0043-platform-teardown-lb-eni-wait
  - ADR-0045-platform-teardown-lb-delete-default
  - ADR-0047-platform-teardown-destroy-timeout-retry
  - ADR-0164-teardown-v3-enhanced-reliability
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---
# ADR-0045: Default LB delete when ENIs persist during teardown

Filename: `ADR-0045-platform-teardown-lb-delete-default.md`

- **Status:** Proposed
- **Date:** 2025-12-30
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh`, `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`, `.github/workflows/ci-teardown.yml`, `docs/10-governance/policies/ci-teardown-extra-permissions.json`, `docs/adrs/ADR-0043-platform-teardown-lb-eni-wait.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Even with the ENI wait gate, teardowns can still hang when NLB ENIs linger and
the load balancer does not delete in time. Operators consistently choose the
break-glass option to delete remaining cluster LBs, which unblocks subnet
deletion and completes teardown. Making this the default removes repeated
manual intervention and speeds up recovery.

Constraints:

- Deletion must be scoped to the cluster to avoid impacting unrelated LBs.
- The behavior must remain auditable and predictable.

---

## Decision

We will make LB deletion the default when ENIs persist:

- `FORCE_DELETE_LBS` defaults to `true`.
- Deletion is scoped to LBs tagged with `elbv2.k8s.aws/cluster=<cluster_name>`.
- CI teardown defaults to this behavior, but operators can still override.

---

## Scope

Applies to:

- Teardown script ENI wait behavior
- CI teardown workflow inputs and defaults
- Teardown documentation and IAM policy guidance

Does not apply to:

- Orphan cleanup deletion order
- Manual deletion outside the cluster tag scope

---

## Consequences

### Positive

- Faster, more reliable teardown completion.
- Less manual intervention during partial teardown recovery.
- Clear cluster-scoped guardrails via tag match.

### Tradeoffs / Risks

- Deletes cluster-scoped LBs by default, which may surprise operators if they
  expect manual confirmation.
- Requires IAM permission to read LB tags and delete LBs.

### Operational impact

- Ensure teardown roles include `elasticloadbalancing:DescribeTags` and
  `elasticloadbalancing:DeleteLoadBalancer`.
- Operators can disable default LB deletion by setting `FORCE_DELETE_LBS=false`
  if needed.

---

## Alternatives considered

- **Keep break-glass optional:** rejected due to repeated manual usage and slow
  recovery.
- **Delete all LBs unscoped:** rejected due to high risk of collateral deletes.

---

## Follow-ups

- Keep documentation aligned with default behavior.
- Monitor teardown logs for unexpected LB deletions.

---

## Notes

This decision supersedes ADR-0043.
