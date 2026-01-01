# ADR-0060: Separate update workflow for existing ephemeral dev clusters

Filename: `ADR-0060-platform-ephemeral-update-workflow.md`

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations | Governance
- **Related:** `.github/workflows/infra-terraform-update-dev.yml`, `ci-workflows/CI_WORKFLOWS.md`, `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Ephemeral clusters are created through a new-build workflow that enforces
`new_build=true`. When operators need to update an existing ephemeral cluster
(same BuildId), that guard blocks the apply. We want a deterministic, auditable
path for updates **without** relaxing the new-build script that protects fresh
cluster creation.

This aligns with the governance stance that rollback/backout and recovery must
remain possible through explicit, controlled workflows.

---

## Decision

We will add a **separate, manual CI workflow** for updating existing ephemeral
dev clusters. The workflow will:

- Require explicit confirmation and a valid BuildId.
- Require a successful plan for the same commit and BuildId.
- Require the state file to already exist (update-only guard).

---

## Scope

Applies to:
- Dev ephemeral clusters where the BuildId already exists.
- Updates that must reuse the existing state key.

Does not apply to:
- New ephemeral cluster creation.
- Persistent lifecycle clusters (for now).
- Automated apply on merge.

---

## Consequences

### Positive

- Clear separation of **create** vs **update** flows.
- Preserves the new-build guardrails for ephemeral creation.
- Provides a deterministic, auditable update path with plan gating.

### Tradeoffs / Risks

- Adds another workflow to maintain and document.
- Operators must choose the correct workflow for the task.
- Dev-only for now; other environments will require follow-up.

### Operational impact

- Operators must provide a valid BuildId and confirm apply.
- Plan runs must succeed before update is allowed.
- Workflow index and runbook references must stay current.

---

## Alternatives considered

- **Relax the new-build guard in the existing apply workflow:** rejected because
  it weakens protections around ephemeral creation.
- **Modify the new-build script:** rejected to avoid regressing a working path.
- **Manual local apply:** rejected due to weaker auditability and access drift.

---

## Follow-ups

- Add the workflow to `ci-workflows/CI_WORKFLOWS.md`.
- Consider extending the update workflow to test/staging/prod.
- Revisit once a health-check-driven apply gate exists.

---

## Notes

If the update workflow becomes the dominant path, revisit whether it should be
merged into a single UI entry with explicit mode selection.
