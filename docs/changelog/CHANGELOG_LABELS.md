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
