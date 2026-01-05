---
id: ADR-0098-standardized-pr-gates
title: 'ADR-0098: Standardized PR Gates for ECR Pipeline'
type: decision
category: adrs
version: 1.0
owner: platform-team
status: accepted
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-12-31
  breaking_change: false
relates_to:
  - ADR-0092
  - ADR-0093
---

# ADR-0098: Standardized PR Gates for ECR Pipeline

## Context

The ECR pipeline PRs were experiencing repeated CI failures due to inconsistent guardrail checks, YAML linting errors, and missing metadata. Multiple workflows needed to trigger on both `main` and `development` branches, and the PR template required explicit checklist selections.

## Decision

We introduce a unified set of PR gate workflows that enforce:
- Mandatory checklist selections in the PR body.
- Consistent `pull_request` triggers for all relevant CI jobs.
- Centralized YAML linting and pre‑commit formatting.
- Automated metadata validation.

All future PRs targeting `development` or `main` must pass these gates before merge.

## Consequences

### Positive
- CI checks become deterministic and pass reliably.
- Reduced manual re‑work for reviewers.
- Clear governance for ECR‑related changes.

### Trade‑offs / Risks
- Slight increase in CI runtime due to additional linting steps.
- Contributors must keep the PR template up‑to‑date.

### Operational Impact
- Documentation updated (this ADR, changelog entry).
- Existing PRs may need to be rebased to satisfy new checks.

## Alternatives considered
- Keep existing ad‑hoc guardrails – rejected due to high failure rate.
- Disable linting – rejected because code quality would degrade.

## Follow‑ups
- Update the PR template to include the required checkboxes.
- Communicate the new process to all engineering teams.
