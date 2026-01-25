<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0025-pr-gates-runbook
title: 'CL-0025: PR gates runbook'
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
  - CL-0025-pr-gates-runbook
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

# CL-0025: PR gates runbook

Date: 2026-01-03
Owner: platform
Scope: onboarding documentation
Related: PR #119, PR #121

## Summary

- add a deterministic PR-to-green runbook with a failure triage loop
- document common guardrail failures, fast fixes, and conflict handling

## Impact

- contributors get a consistent sequence for unblocking PRs; no runtime impact

## Changes

### Documented

- PR gate runbook steps and troubleshooting guidance

## Rollback / Recovery

- Not required

## Validation

- Not run (documentation change)
