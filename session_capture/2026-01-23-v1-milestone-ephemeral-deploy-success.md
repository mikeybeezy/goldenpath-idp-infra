---
id: 2026-01-23-v1-milestone-ephemeral-deploy-success
title: V1 Milestone - Ephemeral Deploy Success and RDS Architecture Clarification
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0177-ci-iam-comprehensive-permissions
  - RDS_USER_DB_PROVISIONING
  - 2026-01-23-ci-iam-permissions-fix
---
# Session Capture: V1 Milestone - Ephemeral Deploy Success

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-23
**Timestamp:** 2026-01-23T07:00:00Z
**Branch:** development (goldenpath-idp-infra)

## Scope

- Validate ephemeral cluster deployment as V1 milestone success
- Clarify RDS architecture and dependency chain
- Document standalone RDS deployment workflow
- Merge conflict resolution for PR #275

## Work Summary

### PR #275 Completed

- Resolved merge conflict in `session_summary/agent_session_summary.md`
- Added changelog entry CL-0166 for CI IAM permissions fix
- All 22 CI checks passed
- PR ready for human merge

### V1 Milestone Assessment

Confirmed ephemeral cluster deployment as **success** because:

| Component | Status | Notes |
|-----------|--------|-------|
| CI Pipeline | Working | Commit → Deploy functional |
| VPC/Subnets | Working | Persistent VPC exists |
| EKS cluster | Working | Control plane + nodes up |
| IRSA roles | Working | ESO, ExternalDNS, Autoscaler, ALB |
| ArgoCD | Working | App-of-apps deployed |
| Secrets | Working | Adopt-or-create pattern |
| Keycloak | Pending | Needs standalone RDS |
| Backstage | Pending | Needs standalone RDS |

### RDS Architecture Clarified

**Key insight:** Keycloak/Backstage not working is **expected** - they need standalone RDS deployed first.

**Dependency chain:**
```
1. Persistent VPC (exists) ✓
2. Standalone RDS (envs/dev-rds/) - NEEDS DEPLOYMENT
3. Ephemeral clusters connect to existing RDS
```

**Two RDS workflows explained:**

| Workflow | Purpose | When to use |
|----------|---------|-------------|
| `rds-database-apply.yml` | Deploy RDS instance + pre-configured DBs | First-time setup |
| `create-rds-database.yml` | Add new database to existing RDS | Self-service for new apps |

### Secrets Flow Validated

```
RDS creates: goldenpath/dev/backstage/postgres
  └── { username, password, host, port, dbname }
          ↓
ExternalSecret pulls from Secrets Manager
          ↓
Backstage pod uses credentials
```

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Count as V1 success | Yes | Non-DB apps working, DB apps just need RDS |
| RDS deployment approach | Standalone first | ADR-0158 pattern - separate lifecycle |
| Documentation needed | No | Existing docs in RDS_USER_DB_PROVISIONING.md sufficient |

## Artifacts Touched

### Modified

- `session_summary/agent_session_summary.md` - Merged conflict, added sessions
- `docs/changelog/entries/CL-0166-ci-iam-comprehensive-permissions.md` - Created

### Validated

- `gitops/helm/backstage/values/dev.yaml` - ExternalSecret config correct
- `envs/dev-rds/terraform.tfvars` - Pre-configured with keycloak/backstage users
- `envs/dev-rds/main.tf` - Creates secrets with correct structure

## Current State / Follow-ups

**Immediate next step:**
```bash
gh workflow run rds-database-apply.yml -f environment=dev
```

This will:
1. Create RDS PostgreSQL instance
2. Create keycloak + backstage databases
3. Create secrets in Secrets Manager
4. Enable Keycloak/Backstage to connect

**After RDS deployed:**
- Keycloak and Backstage pods will auto-recover
- Full platform stack operational

**PR #275 status:** Ready for human merge
- URL: https://github.com/mikeybeezy/goldenpath-idp-infra/pull/275

Signed: Claude Opus 4.5 (2026-01-23T07:00:00Z)
