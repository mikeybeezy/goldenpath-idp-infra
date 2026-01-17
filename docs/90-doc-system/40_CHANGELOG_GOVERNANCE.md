---
id: 40_CHANGELOG_GOVERNANCE
title: Changelog Governance
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 01_GOVERNANCE
  - 02_PLATFORM_BOUNDARIES
  - ADR-0050-platform-changelog-label-gate
  - ADR-0051-platform-reliability-metrics-contract-minimums
  - CHANGELOG_LABELS
  - CL-0001-teardown-kubectl-timeout-guard
  - CL-0002-bootstrap-refactor
  - Changelog-template
  - DOCS_CHANGELOG_README
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# Changelog Governance

Doc contract:

- Purpose: Define when and how changelog entries are required.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/changelog/CHANGELOG_LABELS.md, docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md

This document defines how changelog entries are created, reviewed, and
enforced for GoldenPath IDP.

## Purpose

Changelog entries capture material, user-visible changes to platform behavior
and contracts. The changelog is not a commit log.

## Enforcement

- A changelog entry is required only when a PR carries the label
  `changelog-required`.
- CI enforces the label gate and fails when the label is present without a
  corresponding entry.
- The enforcing workflow is `changelog-policy.yml`.

## Required change types

- CI/CD flow, approvals, or gates
- Terraform behavior or state handling
- Teardown/bootstrap safety or timing
- Defaults, flags, or required inputs
- Operator actions or recovery steps

## Exclusions

- Comments, formatting, or typos only
- Internal refactors with no behavior change
- Dependency bumps with no user impact

## Entry format

Entries live in `docs/changelog/entries/` and use sequential IDs:
`CL-0001`, `CL-0002`, ...

Use `docs/changelog/Changelog-template.md` as the canonical template.

## Ownership and review

- The PR author creates the entry when the label is applied.
- Reviewers verify that the entry matches the change impact.

## Related docs

- `docs/changelog/README.md`
- `docs/changelog/CHANGELOG_LABELS.md`
