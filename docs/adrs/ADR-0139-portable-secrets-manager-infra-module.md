---
id: ADR-0139
title: 'ADR-0139: Portable Secrets Manager Infrastructure Module'
type: adr
status: proposed
domain: platform-core
owner: platform-team
lifecycle:
  supported_until: 2028-01-10
  breaking_change: false
exempt: false
risk_profile:
  production_impact: high
  security_risk: high
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 01_adr_index
  - 11_SECRETS_CATALOG_POLICY
  - 35_SECRET_MANAGEMENT
  - ADR-0007-platform-environment-model
  - ADR-0135
  - ADR-0139
  - CL-0105
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
version: '1.0'
---
# ADR-0139: Portable Secrets Manager Infrastructure Module

- **Status:** Proposed
- **Date:** 2026-01-10
- **Owners:** `platform-team`
- **Domain:** Infrastructure
- **Decision type:** Architecture | Operations

---

## Context

We need to manage AWS Secrets Manager instances across `dev`, `test`, `staging`, and `prod`. Historically, infrastructure for different environments was handled with varying degrees of duplication. To ensure that our security posture and secret management behavior are consistent, we need a "Golden Path" for provisioning the secret stores themselves.

## Decision

We will create a **Portable Infrastructure Module** (`modules/aws_secrets_manager/`) to manage the lifecycle of AWS Secrets Manager. This module will be the standard way all platform environments provision secret containers.

### Key Characteristics
1. **Consistency**: Same encryption settings, lifecycle policies, and naming conventions across all tiers.
2. **Portability**: The module accepts environment-specific variables (via `local.name_prefix` and `local.common_tags`) to ensure zero code change when porting to a new environment.
3. **Encapsulation**: Details like rotation window and KMS key selection are handled inside the module, exposing only necessary outputs (ARN, Name) to the environment layers.

## Consequences

### Positive
- **Reduced Human Error**: Provisioning a store in `prod` becomes a copy-paste module call from `dev`.
- **Governed Naming**: Naming conventions are enforced via the module's internal logic, making them predictable for automated tools like ESO.
- **Improved Maintainability**: Policy updates (e.g., changing a retention period) are done in one place for the entire fleet.

### Tradeoffs / Risks
- **Abstraction Rigidity**: If one environment requires a radically different configuration, the module might become complex with conditionals. We will mitigate this by keeping the module focused on the "Golden Path" use case.

## Operational impact

- Adding a new environment now includes adding the `aws_secrets_manager` module call to the env's `main.tf`.
- Changes to the module must be tested in `dev` before being promoted to higher environments.

## Alternatives considered

### Inline Resource Definitions
- **Pros**: Easy to implement for a single environment.
- **Cons**: Impossible to verify consistency across environments; high risk of drift.

## Follow-ups
- Implement `modules/aws_secrets_manager/main.tf` based on this standard.
- Register the module in `envs/*/main.tf`.
