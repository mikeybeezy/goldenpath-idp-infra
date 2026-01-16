---
id: ADR-0165
title: Automated RDS User and Database Provisioning
type: adr
status: proposed
date: 2026-01-16
deciders:
  - platform-team
domain: platform-core
owner: platform-team
lifecycle: active
schema_version: 1
tags:
  - rds
  - provisioning
  - automation
  - governance
relates_to:
  - PRD-0001-rds-user-db-provisioning
  - 30_PLATFORM_RDS_ARCHITECTURE
  - 10_PLATFORM_REQUIREMENTS
---

## Status

Proposed

## Context

Terraform currently creates Secrets Manager entries for database credentials but
does not create the corresponding Postgres roles or databases. This leaves a
manual gap (psql access) and introduces drift between declared config and
runtime state.

We need an automated, idempotent provisioning path that is safe in non-prod and
auditable in prod.

## Decision

Implement automated RDS user and database provisioning driven by a single
source of truth (application database definitions). The provisioning step will:

- Create roles and databases idempotently.
- Apply grants and default privileges per requested access level.
- Record an audit trail (build_id, timestamp, environment, outcome).
- Require explicit approval for non-dev environments.

Initial implementation will run as a controlled automation step (CI post-apply
or Argo sync wave) using delegated admin credentials where feasible.

## Scope

Applies to platform-managed Postgres RDS instances in dev, test, staging, and
prod environments.

## Consequences

### Positive

- Eliminates manual psql provisioning steps.
- Reduces drift between secrets and actual DB state.
- Provides an auditable record of DB provisioning.

### Tradeoffs / Risks

- Adds a new automation step that must be secured and monitored.
- Requires clear approval gates for production.
- Must handle failures when Kubernetes access is unavailable.

### Operational impact

- Platform team owns the provisioning automation.
- Runbooks and audits must be updated to include this step.

## Alternatives considered

- Manual provisioning via psql (rejected: slow, error-prone).
- Terraform `null_resource` local-exec (viable but less portable).
- AWS Lambda (preferred for long-term resilience; deferred for v1).

## Follow-ups

1. Finalize the trigger path (CI vs Argo) and approval gates.
2. Define tagging and naming conventions aligned with teardown.
3. Implement the idempotent SQL and provisioning job.
4. Add a changelog entry after implementation.
