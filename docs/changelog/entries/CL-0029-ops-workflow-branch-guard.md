<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0029-ops-workflow-branch-guard
title: 'CL-0029: Ops workflow branch guard'
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
  - ADR-0074-platform-ops-workflow-branch-guard
  - CL-0029-ops-workflow-branch-guard
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-04
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0029: Ops workflow branch guard

Date: 2026-01-03
Owner: platform
Scope: CI/CD operations
Related: PR #126, docs/adrs/ADR-0074-platform-ops-workflow-branch-guard.md

## Summary

- restrict bootstrap, teardown, orphan cleanup, and managed LB cleanup to main/development

## Impact

- operational workflows can only run from controlled branches; reduces risk of drift

## Changes

### Changed

- branch validation added to CI bootstrap/teardown/orphan cleanup workflows

## Rollback / Recovery

- Remove branch validation steps if needed.

## Validation

- Not run (workflow change)
