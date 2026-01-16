---
id: PRD-0001-rds-user-db-provisioning
title: 'PRD-0001: Automated RDS User and Database Provisioning'
type: documentation
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 10_PLATFORM_REQUIREMENTS
  - 30_PLATFORM_RDS_ARCHITECTURE
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0001: Automated RDS User and Database Provisioning

Status: draft  
Owner: platform  
Date: 2026-01-16  

## Problem Statement

RDS users and databases are currently created manually after Terraform applies.
Secrets are generated, but the actual roles and databases are missing. This
creates drift, slows onboarding, and increases risk of mistakes.

## Goals

- Automatically create RDS users and databases based on declared inputs.
- Ensure provisioning is idempotent and safe to re-run.
- Keep audit trails for who/what/when.
- Enforce least-privilege access and environment guardrails.

## Non-Goals

- Application schema migrations or data seeding.
- RDS lifecycle management (backup/restore, failover).
- Multi-engine support beyond Postgres in v1.

## Scope

Applies to platform-managed Postgres RDS instances in dev, test, staging, and
prod environments.

## Requirements

### Functional

- Read desired DB/user definitions from a single source of truth.
- Create roles and databases if missing.
- Apply grants and default privileges per requested access level.
- Support idempotent re-runs with no destructive side effects.
- Fail fast on missing secrets or invalid inputs.

### Non-Functional

- Must be auditable (inputs, outputs, and timestamps recorded).
- Must not require human interactive access to the DB.
- Must be safe for prod (explicit approval gate).
- Must not break when Kubernetes API is unavailable.

## Proposed Approach (High-Level)

1. Define `application_databases` as the source of truth.
2. Store user passwords in AWS Secrets Manager.
3. Run a Kubernetes Job that connects to RDS using a delegated admin role.
4. Execute idempotent SQL to create roles, databases, and grants.
5. Record outcome and evidence (build_id, timestamp, results).

## Guardrails

- `ALLOW_DB_PROVISION=true` required for non-dev.
- Block if DB exists but owner does not match requested role.
- Block if role exists but is not managed by platform conventions.

## Observability / Audit

- Emit a structured log record for each provisioned user/database.
- Record run metadata in a durable location (CI logs or governance report).

## Acceptance Criteria

- A new app definition results in a created DB + role without manual `psql`.
- A second run produces no changes and exits successfully.
- Audit log includes environment, db name, user, and run id.
- Prod provisioning is blocked unless explicitly approved.

## Success Metrics

- Time-to-ready for new app DB <= 5 minutes from apply.
- 100% of DB user creation runs are traceable to a build_id.
- Zero manual `psql` steps for provisioning in dev.

## Open Questions

- Do we standardize a delegated admin role or use master for v1?
- Where is the canonical audit record stored (logs vs. docs)?
- Should the job run as part of CI or Argo sync wave?

## References

- docs/20-contracts/10_PLATFORM_REQUIREMENTS.md
- docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md

---

## Comments and Feedback

- <Reviewer name/date>: <comment>
