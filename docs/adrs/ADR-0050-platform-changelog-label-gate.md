---
id: ADR-0050
title: ADR-0050: Label-gated changelog entries
type: adr
owner: platform-team
status: active
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
relates_to: []
---

# ADR-0050: Label-gated changelog entries

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance
- **Related:** `docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md`, `docs/changelog/README.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Changelog updates are required for material behavior changes but not for
mechanical refactors or formatting fixes. A lightweight gate is needed to
require entries only when change impact warrants it, without slowing iteration
for low-risk edits.

---

## Decision

Changelog entries will be required only when a PR carries the label
`changelog-required`. CI will enforce the label gate by checking for a
`docs/changelog/entries/CL-####-*.md` entry whenever the label is present.

---

## Scope

Applies to platform repositories that use the changelog policy and template.
Does not enforce changelog entries for PRs without the label.

---

## Consequences

### Positive

- Changelog entries are created only for material, user-visible changes.
- Enforcement is explicit and easy to audit.
- Low-risk edits remain fast and lightweight.

### Tradeoffs / Risks

- Relies on label discipline and reviewer attention.
- A missed label can omit a changelog entry.

### Operational impact

- Reviewers apply the label when required change types are present.
- PR authors add a changelog entry when the label is applied.

---

## Alternatives considered

- Always require a changelog entry: rejected as too heavy for frequent
  iterations.
- No changelog enforcement: rejected due to drift in user-facing visibility.

---

## Follow-ups

- Add the `changelog-required` label to the repository.
- Add the CI workflow that enforces the label gate.
- Document the label policy and entry template.

---

## Notes

Label-gated enforcement can evolve into a stronger policy if adoption is
inconsistent.
