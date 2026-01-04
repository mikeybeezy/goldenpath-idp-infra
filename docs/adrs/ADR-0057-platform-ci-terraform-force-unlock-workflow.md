---
id: ADR-0057
title: 'ADR-0057: CI Terraform force-unlock workflow (break-glass)'
type: adr
owner: platform-team
status: active
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
- 07_TF_STATE_FORCE_UNLOCK
- 15_TEARDOWN_AND_CLEANUP
- ADR-0057
---

# ADR-0057: CI Terraform force-unlock workflow (break-glass)

Filename: `ADR-0057-platform-ci-terraform-force-unlock-workflow.md`

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `.github/workflows/ci-force-unlock.yml`, `docs/runbooks/07_TF_STATE_FORCE_UNLOCK.md`, `docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Teardown and destroy runs can leave Terraform state locks when runs fail,
runner pods are canceled, or a prior step exits without releasing the lock.
Local `force-unlock` is risky and often unavailable when operators lack
credentials or cluster access. We need a controlled, auditable, CI-native
mechanism to unblock teardown and rollback paths without bypassing governance.

This aligns with the platform stance: **rollback/backout must be possible** and
operators must be able to restore the system to a safe state when automation
fails.

---

## Decision

We will provide a **manual, break-glass CI workflow** that performs a
Terraform `force-unlock` against the correct backend key for a given
environment and BuildId, with explicit confirmation and minimal privileges.

---

## Scope

Applies to:

- CI-driven Terraform runs for platform infra lifecycle (`build`, `teardown`,
  `teardown-resume`) where locks persist.

Does not apply to:

- Routine Terraform operations (no automatic unlocks).
- Non-platform Terraform stacks.

---

## Consequences

### Positive

- Enables rollback/backout when a state lock blocks teardown or cleanup.
- Keeps unlock actions in CI with audit trails (workflow inputs and logs).
- Reduces reliance on local credentials or ad-hoc break-glass access.

### Tradeoffs / Risks

- Force-unlock can corrupt state if another active apply is still running.
- Requires operator discipline to confirm the lock is truly stale.
- Adds another workflow to maintain and document.

### Operational impact

- Operators must locate the lock ID (from DynamoDB lock info or logs).
- Unlock requires explicit confirmation input and uses CI OIDC role access.
- Runbook guidance is required and must be followed.

---

## Alternatives considered

- **Manual local force-unlock only:** blocked by access constraints and poor auditability.
- **Auto-unlock on failure:** too risky; can unlock an in-flight apply.
- **Disable locking (`-lock=false`):** unsafe and violates state integrity guarantees.

---

## Follow-ups

- Keep the runbook updated with lock discovery steps.
- Ensure CI role permissions remain tag- and state-key-scoped.
- Consider adding a lock-detection step in teardown to surface lock metadata.

---

## Notes

- The workflow keys state using `env + lifecycle + build_id`, not PR commit SHA.
  The lock ID is derived from the DynamoDB lock record for that state key.
