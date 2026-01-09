---
id: CL-0093-human-in-the-loop-backstage-docs-prs
title: 'CL-0093: Human-in-the-loop Backstage docs generation'
type: changelog
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0133
  - CL-0093
supported_until: 2028-01-09
breaking_change: false
---

# CL-0093: Human-in-the-loop Backstage docs generation

Date: 2026-01-09
Owner: platform-team
Scope: governance, documentation automation
Related: docs/adrs/ADR-0133-human-in-the-loop-backstage-docs-prs.md

## Summary

- record the decision to generate Backstage docs via PR with human approval

## Impact

- enforces review for generated catalog docs without changing runtime behavior

## Changes

### Documented

- ADR-0133 for HITL PR-based doc generation

## Rollback / Recovery

- Not required

## Validation

- Not required (documentation change)
