<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0043-platform-teardown-lb-eni-wait
title: 'ADR-0043: Teardown waits for LoadBalancer ENIs before subnet delete'
type: adr
status: superseded
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 15_TEARDOWN_AND_CLEANUP
  - 44_DOC_TIGHTENING_PLAN
  - ADR-0043-platform-teardown-lb-eni-wait
  - ADR-0045-platform-teardown-lb-delete-default
  - ADR-0164-teardown-v3-enhanced-reliability
  - audit-20260103
supersedes: []
superseded_by: ADR-0045
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0043: Teardown waits for LoadBalancer ENIs before subnet delete

Filename: `ADR-0043-platform-teardown-lb-eni-wait.md`

- **Status:** Superseded by `ADR-0045-platform-teardown-lb-delete-default.md`
- **Date:** 2025-12-30
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh`, `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`, `.github/workflows/ci-teardown.yml`, `docs/10-governance/policies/ci-teardown-extra-permissions.json`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Teardown has been hanging at subnet deletion because network load balancer ENIs
remain after Kubernetes LoadBalancer Services are deleted. Terraform destroy or
AWS deletes then fail with `DependencyViolation` because subnets still have
attached ENIs. This is especially common during partial teardown or when the
NLB takes longer to release ENIs.

Constraints:

- Teardown must remain automation-first and recoverable from partial failures.
- Any destructive shortcuts must be explicit and auditable.

---

## Decision

We will add an ENI wait gate after LoadBalancer Service deletion and before
subnet deletion:

- Teardown waits for NLB ENIs to disappear from the cluster subnets.
- If ENIs persist beyond a timeout, an explicit break-glass option can delete
  the remaining Kubernetes load balancers and re-wait.
- CI exposes the break-glass flag and required permissions are documented.

---

## Scope

Applies to:

- `bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh`
- `.github/workflows/ci-teardown.yml`
- Teardown documentation and IAM policy guidance

Does not apply to:

- Orphan cleanup deletion order (`cleanup-orphans.sh`)
- Non-AWS Kubernetes environments

---

## Consequences

### Positive

- Fewer teardown failures due to subnet dependency violations.
- Cleaner recovery from partial teardown with a deterministic wait gate.
- Clear operator intent for destructive LB deletion.

### Tradeoffs / Risks

- Adds time to teardown when NLB ENIs linger.
- Break-glass LB deletion can remove active LBs if used incorrectly.
- Requires additional IAM permissions for teardown roles.

### Operational impact

- Operators can set `FORCE_DELETE_LBS=true` (or CI input) when ENIs persist.
- Teardown roles need `elasticloadbalancing:DeleteLoadBalancer` and
  `ec2:DescribeNetworkInterfaces`.
- Docs must explain the wait gate and recovery path.

---

## Alternatives considered

- **Do nothing:** leaves teardown hanging and increases manual cleanup.
- **Always delete LBs:** too destructive; removes safety and intent.
- **Rely solely on orphan cleanup:** slower feedback loop and more drift.

---

## Follow-ups

- Update teardown docs with ENI wait guidance and break-glass steps.
- Maintain the extra teardown IAM permissions policy file.

---

## Notes

This is an operational guardrail, not a change to the environment model.
