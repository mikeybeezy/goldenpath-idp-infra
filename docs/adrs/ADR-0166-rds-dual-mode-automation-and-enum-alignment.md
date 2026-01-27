---
id: ADR-0166
title: Dual-Mode RDS Automation with Enum-Aligned Requests
type: adr
status: proposed
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
  - 30_PLATFORM_RDS_ARCHITECTURE
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0160
  - ADR-0165
  - ADR-0166
  - CATALOG_INDEX
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_REQUEST_FLOW
  - RDS_REQUEST_V1
  - RDS_SESSION_FEEDBACK
  - SCRIPT-0034
  - SCRIPT-0035
  - SESSION_CAPTURE_2026_01_17_01
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - rds
  - provisioning
  - automation
  - governance
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-16
deciders:
  - platform-team
---

## Status

Proposed

## Context

The platform intentionally supports two RDS deployment modes:

1. Coupled RDS (created alongside EKS via `rds_config.enabled`).
2. Standalone RDS (separate Terraform root for team-requested databases).

Both modes must coexist without drift. Today, Backstage templates and workflows
use hard-coded enums and omit size-tier inputs, while the RDS request parser and
schemas enforce canonical enums in `schemas/metadata/enums.yaml`. This creates
future rework risk and inconsistent outcomes.

## Decision

We will keep both RDS modes and make the automation enum-aligned:

1. Use a single, canonical enum source for all RDS request inputs.
2. Map size tiers to instance classes using the existing parser mapping.
3. Add a mode-aware provisioning entrypoint so coupled and standalone flows
   share the same provisioning mechanics.

## Scope

Applies to:
- Backstage RDS request template and GitHub workflow inputs.
- RDS request schema (`schemas/requests/rds.schema.yaml`) and parser.
- Request validation (`scripts/validate_request.py`) - enforces conditional rules.
- Provisioning automation (`scripts/rds_provision.py`).
- Build/deploy targets that optionally include RDS.

Does not change:
- The underlying RDS Terraform module implementation.
- Existing RDS data or Secrets Manager layouts.

## Enum Alignment (Canonical Source)

Source: `schemas/metadata/enums.yaml`

| Field | Enum key | Values | Mapping |
| --- | --- | --- | --- |
| size | rds.instance_sizes | small, medium, large, xlarge | `scripts/rds_request_parser.py` `SIZE_TO_INSTANCE` |
| engine | rds.engines | postgres | Schema default |
| request status | rds.request_status | pending, approved, provisioning, active, failed, decommissioning, decommissioned | Catalog state |
| environment | environments | dev, test, staging, prod, ephemeral | Request target |
| domain | domains | (enum list) | Cost/governance tagging |
| owner | owners | (enum list) | Approval ownership |
| risk | risk_profile_security_risk | none, low, medium, high, access | Risk classification |

## Consequences

### Positive

- Eliminates enum drift between Backstage, workflows, and schema validation.
- Preserves both RDS modes while unifying provisioning behavior.
- Enables predictable sizing across self-service and coupled builds.

### Tradeoffs / Risks

- Requires mode selection logic in the provisioning entrypoint.
- Backstage templates and workflows must be updated to reflect canonical enums.

### Operational impact

- Platform team maintains the enum mapping and size tier policy.
- PR approvals follow existing service class requirements for databases-rds.

## Alternatives considered

- Collapse to a single RDS mode (rejected: breaks requested persistence model).
- Duplicate templates/workflows per mode (rejected: increases drift risk).

## Follow-ups

1. Add a mode-aware `rds-provision` wrapper (coupled vs standalone).
2. Update Backstage template and workflow inputs to use enum-aligned values
   and include size tier selection.
3. Document both flows with a single reference in `docs/85-how-it-works/`.

## Notes

- Size tiers map to instance classes in `scripts/rds_request_parser.py`.
- This ADR is consistent with ADR-0158 and ADR-0160; it clarifies alignment.
