<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0104
title: 'CL-0104: Backstage ECR requests dispatch workflow'
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
  - ADR-0141
  - CL-0104
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-11
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0104: Backstage ECR requests dispatch workflow

Date: 2026-01-11
Owner: platform-team
Scope: Backstage scaffolder, ECR registry workflow
Related: PR #212, docs/adrs/ADR-0141-backstage-ecr-dispatch-workflow.md

## Summary

- Switch the Backstage ECR request template to dispatch the workflow on main.
- Keep workflow PRs targeting `development` via an explicit `base_branch` input.
- Add a filtered PR link and keep a workflow link as the primary signal.

## Impact

- Backstage no longer needs command execution to create registry PRs.
- Users follow the workflow run and filtered PR link for status.

## Changes

### Added

- Dispatch-based template flow for ECR registry requests.

### Changed

- Workflow PR base now aligns with the dispatch branch.
- Template output includes a filtered PR link.

### Fixed

- Avoids PR drift when main and development diverge.

### Deprecated

- None.

### Removed

- None.

### Documented

- Updated runbook notes for Helm override issues.

### Known limitations

- Backstage cannot emit a direct PR URL at dispatch time.

## Rollback / Recovery

- Revert PR #212.

## Validation

- Not run (template + workflow changes).
