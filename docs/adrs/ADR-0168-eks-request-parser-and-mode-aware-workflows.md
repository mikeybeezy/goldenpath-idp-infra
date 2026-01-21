---
id: ADR-0168
title: EKS Request Parser and Mode-Aware Workflows
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
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0032-platform-eks-access-model
  - ADR-0033-platform-ci-orchestrated-modes
  - ADR-0144
  - ADR-0153
  - ADR-0161
  - ADR-0170
  - CL-0142
  - CL-0143
  - CL-0147
  - EKS_REQUEST_FLOW
  - SCRIPT-0043
  - session-2026-01-17-eks-backstage-scaffolder
supersedes: []
superseded_by: []
tags:
  - eks
  - parser
  - self-service
  - governance
  - ci
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-17
deciders:
  - platform-team
---

## Status

Accepted

## Context

EKS provisioning needed the same contract-driven, parser-first path used for
RDS and Secrets, but EKS requests were either implicit (Terraform edits) or
blocked by the scope gate. This created drift risk, unclear ownership, and
inconsistent inputs (enums, modes, and build identifiers).

We needed a consistent EKS request flow that:
- Captures intent in a governed request file.
- Validates against canonical enums.
- Generates deterministic tfvars for Terraform.
- Supports explicit modes for cluster creation vs bootstrap.
- Enforces non-dev guardrails.

## Decision

Adopt an EKS request system that mirrors the platform parser pattern:

1. Request files live under `docs/20-contracts/eks-requests/<env>/EKS-XXXX.yaml`.
2. The parser (`scripts/eks_request_parser.py`, SCRIPT-0043) validates enums and
   required fields, then generates tfvars to
   `envs/<env>/clusters/generated/<id>.auto.tfvars.json`.
3. Modes are explicit and validated: `cluster-only`, `bootstrap-only`,
   `cluster+bootstrap`.
4. `build_id` is required for modes that create clusters.
5. Workflows provide validation and gated apply:
   - `ci-eks-request-validation.yml` validates requests in PRs.
   - `eks-request-apply.yml` applies requests and enforces `allow_non_dev` for
     staging/prod.
6. Canonical enums for EKS are owned in `schemas/metadata/enums.yaml`.

## Scope

Applies to:
- EKS request files and request schema.
- The EKS request parser and generated tfvars.
- CI validation and apply workflows for EKS requests.

Does not change:
- The underlying EKS Terraform module design.
- Existing Backstage templates (a new EKS template is planned separately).

## Consequences

### Positive

- Aligns EKS with the contract-driven parser architecture.
- Standardizes mode handling and build_id requirements.
- Reduces drift between requests, tfvars, and workflows.

### Tradeoffs / Risks

- Requires ongoing enum maintenance and request validation.
- Some advisory fields remain non-wired and only emit warnings.
- Adds additional workflow steps for validation and apply.

### Operational impact

- Platform team owns the parser and enum lifecycle.
- Operators must use request files and the apply workflow instead of ad-hoc
  Terraform edits.

## Alternatives considered

- Direct tfvars edits (rejected: bypasses governance and validation).
- Backstage-only workflow without parser (rejected: diverges from platform
  contract standard).
- One-mode-only EKS flow (rejected: bootstrap-only use case requires separation).

## Follow-ups

1. Add a Backstage EKS request template aligned to the new schema.
2. Document the EKS request flow alongside RDS and Secrets.
3. Wire non-wired advisory fields once Terraform support lands.

## Notes

- `build_id` is a required identifier for cluster creation modes.
- Non-dev applies remain gated by `allow_non_dev`.
