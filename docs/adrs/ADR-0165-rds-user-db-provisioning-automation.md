---
id: ADR-0165
title: Automated RDS User and Database Provisioning
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
  - 10_PLATFORM_REQUIREMENTS
  - 30_PLATFORM_RDS_ARCHITECTURE
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0165
  - ADR-0166
  - CATALOG_INDEX
  - CL-0140
  - CL-0143
  - CL-0147
  - PRD-0001-rds-user-db-provisioning
  - PR_GUARDRAILS_INDEX
  - RB-0032
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_REQUEST_FLOW
  - RDS_SESSION_FEEDBACK
  - RDS_USER_DB_PROVISIONING
  - SCRIPT-0035
  - SESSION_CAPTURE_2026_01_17_01
  - agent_session_summary
  - session-2026-01-17-eks-backstage-scaffolder
  - session-2026-01-19-build-pipeline-architecture
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

Accepted (Implemented 2026-01-16)

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

1. ~~Finalize the trigger path (CI vs Argo) and approval gates.~~ Done: CI post-apply
2. ~~Define tagging and naming conventions aligned with teardown.~~ Done: Uses existing conventions
3. ~~Implement the idempotent SQL and provisioning job.~~ Done: SCRIPT-0035
4. Add a changelog entry after implementation.
5. Consider Lambda fallback for v2 (K8s-independent execution).

## Implementation Details (2026-01-16)

**Script**: `scripts/rds_provision.py` (SCRIPT-0035)

**Trigger**: Makefile targets `rds-provision` and `rds-provision-dry-run`

**Approval Gate**: `ALLOW_DB_PROVISION=true` required for non-dev environments

**Key Design Decisions**:
- Python script (consistent with existing parsers)
- Uses master credentials for v1 (delegated admin deferred to v2)
- Idempotent SQL patterns for role/database creation
- CSV audit trail to stdout
- Dry-run mode for safe preview

**Runbook**: RB-0032-rds-user-provision.md

## Execution Architecture (2026-01-24)

### Problem: VPC Access Required

RDS instances are deployed in private VPC subnets. The provisioning script must
execute from within the VPC to reach the RDS endpoint. Local execution (developer
machine, GitHub runners) fails with DNS resolution errors because the RDS private
DNS name is not resolvable outside the VPC.

### Solution: K8s Job Execution

Run `rds_provision.py` as a Kubernetes Job inside the EKS cluster. Pods in the
cluster have VPC network access and can reach the private RDS endpoint.

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Execution Flow                              │
├─────────────────────────────────────────────────────────────────┤
│  Terraform Pass 2 (enable_k8s_resources=true)                   │
│    └── Creates platform-system namespace                        │
│    └── Creates platform-provisioner ServiceAccount (IRSA)       │
│                                                                 │
│  RDS Provisioning (make rds-provision-auto)                     │
│    └── Detects EKS cluster available                            │
│    └── Creates K8s Job in platform-system namespace             │
│    └── Job pod has VPC access → reaches RDS                     │
│    └── Job pod has IRSA → reads/writes Secrets Manager          │
│    └── Waits for completion, fetches logs                       │
└─────────────────────────────────────────────────────────────────┘
```

### Terraform-Managed Infrastructure

The `platform-system` namespace and ServiceAccount are created by Terraform
during Pass 2, following the same pattern as `argocd` and `external-secrets`
namespaces. This ensures the infrastructure exists BEFORE RDS provisioning runs.

| Resource | Location | Purpose |
|----------|----------|---------|
| `kubernetes_namespace_v1.platform_system` | `envs/dev/main.tf` | Namespace for platform automation |
| `kubernetes_service_account_v1.platform_provisioner` | `envs/dev/main.tf` | IRSA-enabled SA for Secrets Manager |
| `iam_role.rds_provisioner` | `modules/iam/main.tf` | IAM role for Secrets Manager access |

### RDS Modes Support

| Mode | Trigger | Sequence |
|------|---------|----------|
| **Coupled** | `make deploy` with `rds_config.enabled=true` | EKS → platform-system → RDS provision → bootstrap |
| **Standalone** | `make rds-deploy` | EKS must exist → K8s Job runs in platform-system |

### IRSA Policy

The `platform-provisioner` ServiceAccount requires:

- `secretsmanager:GetSecretValue` - Read RDS master credentials
- `secretsmanager:PutSecretValue` - Write application credentials
- `secretsmanager:CreateSecret` - Create new secrets if needed

### Fallback Paths

1. **Port-forward**: For debugging, forward RDS port through cluster
2. **Lambda** (v2): Future K8s-independent execution path (see Follow-ups)
