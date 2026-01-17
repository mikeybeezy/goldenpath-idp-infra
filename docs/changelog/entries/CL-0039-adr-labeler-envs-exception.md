---
id: CL-0039-adr-labeler-envs-exception
title: Exclude envs from ADR labeler rule
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - CL-0039-adr-labeler-envs-exception
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-04
version: '1.0'
breaking_change: false
---

## CL-0039: Exclude envs from ADR labeler rule

Date: 2026-01-03
Author: Antigravity

## Summary

Remove `envs/**` from the `adr-required` labeler rule to reduce friction for
build-id only updates.

## Changes

- Labeler no longer applies `adr-required` for `envs/**` paths.
- Guardrails doc updated to reflect the new scope.

## Impact

- Build-id updates to `envs/**` no longer require ADR entries.
