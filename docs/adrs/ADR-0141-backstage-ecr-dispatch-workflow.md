---
id: ADR-0141
title: 'ADR-0141: Backstage ECR requests use GitHub Actions dispatch'
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0095-self-service-registry-creation
  - ADR-0128
  - ADR-0141
  - CL-0104
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-11
version: 1.0
breaking_change: false
---

## ADR-0141: Backstage ECR requests use GitHub Actions dispatch

- **Status:** Accepted
- **Date:** 2026-01-11
- **Owners:** `platform-team`
- **Domain:** Platform
- **Decision type:** Operations | Governance
- **Related:** ADR-0095, ADR-0128

---

## Context

The Backstage ECR scaffolder was creating PRs directly using
`fetch:plain` + `command:execute` + `publish:github:pull-request`.
That path requires a custom Backstage backend image with the command
action enabled and a stable token flow. During V1 hardening, this
introduced brittle behavior and slowed feedback when the backend
image or token handling drifted.

We need a deterministic, low-friction path for registry requests that
keeps Backstage simple while preserving the GitOps contract.

## Decision

We will trigger the existing `create-ecr-registry.yml` workflow via
`github:actions:dispatch` from Backstage. The workflow remains the
single PR-creation mechanism and is responsible for catalog and tfvars
updates.

## Scope

### Applies to

- ECR registry requests in Backstage.

### Does not apply to

- Other scaffolder templates that do not rely on registry creation.

## Consequences

### Positive

- Removes dependency on custom backend actions for V1.
- Keeps a single, audited PR creation path.
- Simplifies token handling in Backstage.

### Tradeoffs / Risks

- Backstage cannot immediately return a direct PR URL.
- Requires users to follow workflow/run links for status.

### Operational impact

- Enable `github:actions:dispatch` in Backstage allowed actions.
- Keep workflow PRs targeting `development` via a `base_branch` input.

## Alternatives considered

### Direct PR creation in Backstage

Rejected for V1 due to backend image and action enablement complexity.
Revisit in V1.1 once the backend image and secret handling are stable.

## Follow-ups

- Add a filtered PR link in template output for usability.
- Reassess direct PR creation in V1.1 once backend image is in place.
