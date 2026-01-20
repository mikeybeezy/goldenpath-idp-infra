---
id: ADR-0169
title: System-Generated SecretRequest IDs with CI Immutability Guard
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0135
  - ADR-0143
  - ADR-0144
  - ADR-0170
  - CL-0111
  - SCRIPT-0033
  - SECRET_REQUEST_FLOW
supersedes: []
superseded_by: []
tags:
  - secrets
  - governance
  - ci
  - auditability
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
date: 2026-01-17
deciders:
  - platform-team
---
## Status

Accepted

## Context

SecretRequest identifiers are used for governance, auditability, and traceability
across request files, generated tfvars, and Terraform targets. When IDs are
manually entered, they are prone to collision, tampering, and inconsistent
formatting. We also do not want ID generation to depend on Backstage-specific
logic.

We need system-generated IDs with immutable enforcement as a backstop.

## Decision

1. Generate SecretRequest IDs inside the workflow that creates the PR.
2. Remove user-entered request IDs from Backstage input.
3. Enforce immutability and filename-to-id matching in CI for any SecretRequest
   change.

This keeps Backstage as the front door for intent while preserving a consistent,
auditable identity for each request.

## Scope

Applies to:
- SecretRequest creation workflow (`request-app-secret.yml`).
- SecretRequest PR validation (`secret-request-pr.yml`).
- SecretRequest files under `docs/20-contracts/secret-requests/`.

Does not change:
- SecretRequest schema or parser behavior.
- Secret provisioning flow or Terraform targets.

## Consequences

### Positive

- Deterministic, system-generated IDs reduce collisions and drift.
- IDs are immutable and validated in CI for auditability.
- Backstage templates remain simple and do not require custom ID logic.

### Tradeoffs / Risks

- Workflow becomes the single generator for request IDs.
- Requires CI guardrails to remain healthy to prevent manual edits.

### Operational impact

- Platform team maintains the request workflow and ID guard.
- Reviewers can rely on filename/id consistency for traceability.

## Alternatives considered

- User-provided IDs with regex validation (rejected: still prone to errors).
- Backstage-generated IDs (rejected: adds Backstage dependency and reduces
  portability).

## Follow-ups

1. Document the system-generated ID behavior in the Secret Request flow doc.
2. Ensure request IDs are surfaced in Backstage outputs and PR templates.

## Notes

- CI guard enforces both immutability and filename alignment.
