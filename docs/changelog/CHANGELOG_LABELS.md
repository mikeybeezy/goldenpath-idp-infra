---
id: CHANGELOG_LABELS
title: Changelog Labels (Living)
type: documentation
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
  supported_until: 2028-01-01
  breaking_change: false
relates_to:

- 40_CHANGELOG_GOVERNANCE
- CHANGELOG_TEMPLATE
- CL-####

---

# Changelog Labels (Living)

Doc contract:

- Purpose: Track changelog label rules and required entry format.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md, docs/changelog/Changelog-template.md

This document records the labels and rules used by the changelog gate.

## Labels

| Label | Meaning | Required entry |
| --- | --- | --- |
| `changelog-required` | PR introduces a material platform behavior change | `docs/changelog/entries/CL-####-short-title.md` |
| `changelog-exempt` | Explicit exemption for test-only or non-user-facing changes | None |

If both `changelog-required` and `changelog-exempt` are present, the gate
skips enforcement.

## Entry sections

Entries should include the sections listed in
`docs/changelog/Changelog-template.md`.

## Change history

- 2025-12-31: Initial label-gated changelog policy added.
- 2026-01-03: Added `changelog-exempt` label.
