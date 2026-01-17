---
id: US-0000-template
title: 'US-0000: User Story Template'
type: template
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - 00_INDEX
  - DOCS_USER-STORIES_README
  - USER_STORIES_INDEX
supported_until: 2028-01-01
version: 1.0
breaking_change: false
---
# US-0000: Short user story title

Date: YYYY-MM-DD
Owner: platform
Status: draft | approved
Related: docs/adrs/ADR-XXXX-*.md, docs/changelog/entries/CL-XXXX-*.md

## Story

As a **<persona>**, I want **<capability>** so that **<outcome>**.

## Context / Problem

- What is failing today?
- Who is impacted?
- What friction does this create?

## Scope

- In scope:
  - <what this enables>
- Out of scope:
  - <what this does not cover>

## Features tied to this story

- Feature: <name>
  - Why: <reason this feature exists>
  - For: <primary user/group>
  - Evidence: <ADR/Changelog/PR link>

## Acceptance criteria

- [ ] Repo/app created with required metadata.
- [ ] Guardrails enforced by default (branch protections, required checks).
- [ ] Documentation and catalog registration are present.

## Success signals

- <metric or signal that shows the story is working>

## Risks / Tradeoffs

- <known risks>
