---
id: US-0001-governance-driven-repo-scaffolder
title: "US-0001: Governance-driven repo scaffolder"
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
relates_to: []
---

# US-0001: Governance-driven repo scaffolder

Date: 2026-01-03
Owner: platform
Status: approved
Related: docs/adrs/ADR-0078-platform-governed-repo-scaffolder.md, docs/changelog/entries/CL-0031-governed-repo-scaffolder.md

## Story

As a **platform consumer**, I want a governed repo scaffolder so that new
services are created with the right metadata, guardrails, and deployment
templates from day one.

## Context / Problem

- New repos are created ad-hoc and miss required metadata.
- Guardrails (branch protection, required checks) are inconsistent.
- Onboarding time increases because teams retrofit CI/CD and docs.

## Scope

- In scope:
  - Deterministic repo creation from a Golden Path template.
  - Required governance metadata captured at creation.
  - Default guardrails applied automatically.
- Out of scope:
  - Retroactive fixes to existing repos.
  - Automatic service discovery (V1.1).

## Features tied to this story

- Feature: Repo scaffolder workflow + Backstage template
  - Why: eliminate ad-hoc repo creation and metadata drift.
  - For: app teams and platform operators.
  - Evidence: `docs/adrs/ADR-0078-platform-governed-repo-scaffolder.md`

## Acceptance criteria

- [ ] Repo created with `catalog-info.yaml` and required metadata.
- [ ] Branch protection and required checks enabled by default.
- [ ] Golden Path template rendered with no unresolved placeholders.

## Success signals

- New services reach first deploy faster (reduced setup time).
- Fewer PR guardrail failures from missing metadata.
- Standard identity: every repo ships with the same CI/CD, README, and branch protections.
- No orphans: every repo is owned by a team.
- Compliance-by-default: cannot create a public repo or skip branch protection.

## Risks / Tradeoffs

- Requires repo-creation token with elevated permissions.
- Template and workflow inputs must remain aligned.
