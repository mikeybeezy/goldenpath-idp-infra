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
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0165
  - CL-0140
  - DOCS_PRDS_README
  - RB-0032
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_REQUEST_FLOW
  - RDS_USER_DB_PROVISIONING
  - agent_session_summary
  - session-2026-01-19-build-pipeline-architecture
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# PRD-0001: Automated RDS User and Database Provisioning

Status: implemented
Owner: platform
Date: 2026-01-16
Implemented: 2026-01-19

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

## Feedback Summary (2026-01-16)

- Align provisioning with teardown conventions (BuildId, ClusterName, ManagedBy tags).
- Decide on a resilience strategy if Kubernetes is unavailable (CI or Lambda fallback).
- Prefer delegated admin over master credentials for auditability and least privilege.
- Define where audit records live (CI logs + governance report).
- Standardize naming conventions for databases and roles.

## Next Steps

1. Choose the admin credential model (delegated role vs. master for v1).
2. Select the trigger path (CI post-apply vs. Argo sync wave) and approval gates.
3. Define tagging and naming conventions for DBs/users to support teardown.
4. Specify the audit record location and format.
5. Draft the idempotent SQL contract and the minimal provisioning job spec.

## References

- docs/20-contracts/10_PLATFORM_REQUIREMENTS.md
- docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md

---

## Comments and Feedback
When providing feedbackk, leave a comment and timestamp your comment

### Claude Opus 4.5 / 2026-01-16

**Overall Assessment**: Well-structured PRD with clear requirements. The following points should be considered before implementation:

#### 1. Teardown Integration (High Priority)

Given recent teardown v3 work, provisioned databases must be tagged for cleanup:

- Add `BuildId`, `ClusterName`, and `ManagedBy=platform` tags to all created resources
- Teardown searches by `BuildId` tag or name pattern - provisioning MUST follow same conventions
- Consider adding `RDS_CLEANUP_POLICY` variable: `retain` | `delete` | `snapshot-and-delete`

#### 2. Kubernetes Job Resilience (Medium Priority)

PRD states "Must not break when Kubernetes API is unavailable" but proposes K8s Job:

- **Option A**: Fallback mechanism if K8s Job fails to schedule
- **Option B**: Run as Terraform `null_resource` with `local-exec` (avoids K8s dependency)
- **Option C**: AWS Lambda triggered by Terraform (true K8s-independence)
- **Recommendation**: Option B for v1, migrate to Option C for production-grade

#### 3. Open Question Recommendations

| Question                       | Recommendation                          | Rationale                                                            |
| ------------------------------ | --------------------------------------- | -------------------------------------------------------------------- |
| Delegated admin vs master?     | **Delegated admin from day 1**          | Using master creates security debt and complicates audit trails      |
| Audit record location?         | **Both CI logs AND governance report**  | Append to `docs/governance/audit/` with build_id reference           |
| CI vs Argo sync wave?          | **CI for initial, Argo for subsequent** | Explicit control for first deployment                                |

#### 4. Missing Considerations

- **Secret Rotation**: How will password rotation be handled post-provisioning? Consider AWS Secrets Manager rotation Lambda integration path.
- **Connection Pooling**: Will PgBouncer or RDS Proxy be used? Affects user/role creation strategy.
- **Shared Instance Cleanup**: Current teardown deletes RDS instances but doesn't handle user-created databases within shared instances.

#### 5. Naming Convention Suggestion

Standardize for pattern-based cleanup and auditing:

```text
Database: <app_name>_<env>_db
Role:     <app_name>_<env>_user
```

#### 6. Integration with Existing Teardown

The `delete_rds_instances_for_build()` function in teardown v3 currently:

- Searches by `BuildId` tag
- Falls back to `kubernetes.io/cluster/<cluster_name>` tag
- Falls back to name pattern matching

**Action Required**: Ensure provisioning script tags databases with at least one of these patterns.

**Signed**: Claude Opus 4.5 (claude-opus-4-5-20251101)
**Timestamp**: 2026-01-16T18:45:00Z

---
