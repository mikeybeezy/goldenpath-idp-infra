---
id: ADR-0036-platform-orphan-cleanup-workflow
title: 'ADR-0036: Orphan Cleanup Is Manual and Decoupled From Teardown'
type: adr
status: superseded
domain: platform-core
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle: active
version: '1.0'
superseded_by: ADR-0038
relates_to:
  - 01_GOVERNANCE
  - 20_CI_ENVIRONMENT_SEPARATION
  - ADR-0036
  - ADR-0038
  - ADR-0038-platform-teardown-orphan-cleanup-gate
supported_until: 2028-01-04
breaking_change: false
---

# ADR-0036: Orphan Cleanup Is Manual and Decoupled From Teardown

- **Status:** Superseded
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Operations / Governance
- **Related:** `docs/10-governance/01_GOVERNANCE.md`, `docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md`, `docs/adrs/ADR-0038-platform-teardown-orphan-cleanup-gate.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

CI teardown can hang or fail when orphan cleanup is executed inline, especially
when tagging permissions or AWS eventual consistency create long-running or
retry-heavy cleanup loops. This reduces confidence in teardown, makes reruns
fragile, and can block the goal of clean bring-up/bring-down cycles.

We need teardown to be predictable and fast, while still providing a safe path
to remove straggler resources when necessary.

---

## Decision

Orphan cleanup is **manual and explicit**, and is **decoupled from teardown**.

“Manual” means a **human-initiated workflow or CLI step** with clear intent and
auditable execution. It does **not** mean ad-hoc console deletion.

Teardown should complete without running orphan cleanup by default.

---

## Scope

Applies to:

- CI teardown workflows for ephemeral environments
- Any automation that deletes AWS resources after a failed or partial run

Does not apply to:

- Normal Terraform destroy flow (which should remain automated)
- One-off emergency cleanup steps outside CI

---

## Consequences

### Positive

- Teardown is faster and more reliable.
- Failures in cleanup do not block teardown completion.
- Cleanup runs are explicit and auditable.

### Tradeoffs / Risks

- Orphans may persist longer if cleanup is not triggered.
- Requires discipline to run cleanup when needed.

### Operational impact

- Provide a dedicated workflow or CLI path for orphan cleanup.
- Document when to run cleanup and how to verify results.

---

## Alternatives considered

- **Inline orphan cleanup during teardown:** rejected due to hanging and retry
  behavior, which undermines teardown reliability.
- **Always-on cleanup with fail-open:** rejected because it hides cleanup failures
  and makes behavior harder to reason about.
- **Console-only cleanup:** rejected due to lack of auditability and repeatability.

---

## Follow-ups

- Add a dedicated orphan cleanup workflow or runbook entry.
- Ensure required tagging permissions are scoped and documented.

---

## Notes

Superseded by `ADR-0038-platform-teardown-orphan-cleanup-gate.md`.

This decision favored predictable teardown over fully automated cleanup. Cleanup
remains available but is executed intentionally.
