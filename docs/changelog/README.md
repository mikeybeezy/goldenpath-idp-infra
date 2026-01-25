<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: DOCS_CHANGELOG_README
title: Changelog Guidance (Label-Gated)
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 24_PR_GATES
  - 40_CHANGELOG_GOVERNANCE
  - ADR-0050-platform-changelog-label-gate
  - CL-0001-teardown-kubectl-timeout-guard
  - CL-0002-bootstrap-refactor
  - Changelog-template
  - HEALTH_AUDIT_LOG
  - PLATFORM_HEALTH
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# Changelog Guidance (Label-Gated)

This changelog records material, user-visible changes to platform behavior and
contracts. It complements commits, PRs, ADRs, and runbooks by focusing on
observable impact.

## Policy

Changelog entries are required only when a PR carries the label
`changelog-required`. The label is applied when a change affects any item in
the required list below.

## Required when label is set

- CI/CD flow, approvals, or gates
- Terraform behavior or state handling
- Teardown/bootstrap safety or timing
- Defaults, flags, or required inputs
- Operator actions or recovery steps

## Not required

- Comments, formatting, or typos only
- Internal refactors with no behavior change
- Dependency bumps with no user impact

## Entry location and numbering

Entries live in `docs/changelog/entries/` and use sequential IDs that mirror
ADR numbering.

- Format: `CL-0001`, `CL-0002`, ...
- Filename: `CL-0001-short-title.md`
- Sequence is monotonic and never reused

## Template

The canonical template is in `docs/changelog/Changelog-template.md`.
