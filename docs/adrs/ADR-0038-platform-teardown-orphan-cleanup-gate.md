---
id: ADR-0038-platform-teardown-orphan-cleanup-gate
title: 'ADR-0038: Gate Orphan Cleanup in CI Teardown with Explicit Modes'
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
  - 15_TEARDOWN_AND_CLEANUP
  - ADR-0036
  - ADR-0036-platform-orphan-cleanup-workflow
  - ADR-0037
  - ADR-0037-platform-resource-tagging-policy
  - ADR-0038
  - ORPHAN_CLEANUP
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

# ADR-0038: Gate Orphan Cleanup in CI Teardown with Explicit Modes

- **Status:** Proposed
- **Date:** 2025-12-29
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Operations / Governance
- **Related:** `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`, `docs/70-operations/runbooks/ORPHAN_CLEANUP.md`, `docs/adrs/ADR-0036-platform-orphan-cleanup-workflow.md`, `docs/adrs/ADR-0037-platform-resource-tagging-policy.md`, `.github/workflows/ci-teardown.yml`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Teardown reliability is the weakest part of the infra lifecycle. We have seen
teardown loops hang when GitOps recreates LoadBalancer Services and when orphan
cleanup takes too long or is ambiguous in intent.

We need a teardown flow that is fast, deterministic, and automation-first, while
still giving operators an explicit choice over destructive orphan cleanup.

---

## Decision

We will introduce an explicit **cleanup mode gate** in CI teardown.

CI teardown will expose an input that requires operators to choose one of:

- `delete` — remove BuildId-tagged orphan resources
- `dry_run` — discover and report orphans only
- `none` — skip orphan discovery and deletion

The default mode will be `delete` for ephemeral environments to preserve fast,
clean teardown and reduce toil, with opt-out available for safety.

---

## Scope

Applies to:

- CI teardown workflows for ephemeral environments
- Tag-based orphan discovery and cleanup within CI teardown

Does not apply to:

- Manual CLI cleanup (`cleanup-orphans.sh`)
- Terraform destroy behavior

---

## Consequences

### Positive

- Operators must choose an explicit cleanup mode; intent is visible and auditable.
- Default behavior matches automation-first teardown for short-lived clusters.
- Discovery-only mode provides safer troubleshooting.

### Tradeoffs / Risks

- `delete` relies on BuildId uniqueness and consistent tagging; mistakes can
  delete active resources.
- More workflow inputs add operational surface area.

### Operational impact

- Update CI teardown workflow inputs and documentation.
- Ensure BuildId uniqueness is enforced and tag policy compliance is maintained.

---

## Alternatives considered

- **Manual-only cleanup** (ADR-0036): rejected for high toil and slow recovery.
- **Always-on cleanup without choice**: rejected due to safety concerns and lack
  of explicit operator intent.
- **Separate cleanup workflow only**: rejected because it adds friction for
  frequent ephemeral teardown cycles.

---

## Follow-ups

- Implement cleanup mode input in CI teardown.
- Update teardown docs and runbooks with the new modes.
- Validate BuildId uniqueness checks and tagging enforcement.

---

## Notes

If this ADR is accepted, it supersedes `ADR-0036-platform-orphan-cleanup-workflow.md`.
