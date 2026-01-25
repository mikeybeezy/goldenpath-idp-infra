<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0181
title: CREATEDB Privilege for Application Database Users
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
  - ADR-0165-rds-user-db-provisioning-automation
  - ADR-0158-platform-standalone-rds-bounded-context
  - SCRIPT-0035
supersedes: []
superseded_by: []
tags:
  - rds
  - provisioning
  - postgresql
  - security
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-24
deciders:
  - platform-team
---

## Status

Accepted (Implemented 2026-01-24)

## Context

The RDS provisioning script (`rds_provision.py`, SCRIPT-0035) creates PostgreSQL
roles for application databases. Initially, roles were created with only `LOGIN`
privilege:

```sql
CREATE ROLE app_user WITH LOGIN PASSWORD '...';
```

This caused Backstage to fail at startup with:

```
error: permission denied to create database "backstage_plugin_app"
```

### Why Applications Need CREATEDB

Modern applications often create additional databases dynamically:

| Application | Plugin Databases Created |
|-------------|-------------------------|
| Backstage   | `backstage_plugin_app`, `backstage_plugin_catalog`, `backstage_plugin_scaffolder` |
| Keycloak    | May create plugin databases depending on extensions |

These are created at application startup, not during provisioning. Without
`CREATEDB`, applications fail to start.

### Where This Fits in the Deploy Sequence

```
Terraform Pass 1 → VPC, EKS, RDS instance
Terraform Pass 2 → Namespaces, ServiceAccounts, Secrets (bootstrap)
RDS Provisioning → Creates roles with CREATEDB ← THIS ADR
ArgoCD Sync      → Apps start and create plugin databases
```

CREATEDB is granted during **RDS Provisioning** (step 3), which runs after
Terraform bootstrap but before applications start.

## Decision

Grant `CREATEDB` privilege to all application database users created by
`rds_provision.py`.

### Implementation

**Before:**
```sql
CREATE ROLE app_user WITH LOGIN PASSWORD '...';
ALTER ROLE app_user WITH PASSWORD '...';  -- for existing roles
```

**After:**
```sql
CREATE ROLE app_user WITH LOGIN CREATEDB PASSWORD '...';
ALTER ROLE app_user WITH LOGIN CREATEDB PASSWORD '...';  -- idempotent upgrade
```

### Affected Code

- `scripts/rds_provision.py` - `provision_role()` function (lines 326-398)

### Idempotent Upgrade

When `rds_provision.py` runs against existing roles (e.g., during password
rotation), the `ALTER ROLE` statement ensures `CREATEDB` is granted even if
the role was created before this change.

## Scope

Applies to all application database users defined in `application_databases`:

```hcl
application_databases = {
  keycloak = {
    database_name = "keycloak"
    username      = "keycloak_user"
  }
  backstage = {
    database_name = "backstage"
    username      = "backstage_user"
  }
  # ... additional applications
}
```

## Consequences

### Positive

- Applications can create plugin databases at startup without manual intervention
- Provisioning is fully automated end-to-end
- Idempotent: safe to re-run provisioning on existing environments

### Security Considerations

- `CREATEDB` allows users to create new databases, but NOT:
  - Create roles (`CREATEROLE` not granted)
  - Access other databases (still requires explicit `GRANT`)
  - Become superuser (`SUPERUSER` not granted)
- Databases created by applications are owned by the creating user
- Risk is limited to the RDS instance (no cross-instance impact)

### Tradeoffs

- Slightly broader permissions than absolute minimum
- Applications can create arbitrary databases (but cannot access others)

### Operational Impact

- No manual `ALTER USER ... CREATEDB` needed after provisioning
- Existing deployments upgraded automatically on next provisioning run

## Alternatives Considered

1. **Grant CREATEDB manually after provisioning** - Rejected: defeats automation
2. **Pre-create all plugin databases in Terraform** - Rejected: requires knowing
   all plugin databases upfront, fragile as applications evolve
3. **Use superuser credentials for apps** - Rejected: excessive permissions,
   security risk

## Implementation Details

**Commit:** `8bce1b18` - `fix(rds): grant CREATEDB privilege to application database users`

**Script:** `scripts/rds_provision.py` (SCRIPT-0035)

**Trigger:** Runs during `make rds-provision-auto` or `make deploy` with RDS enabled

## Verification

After provisioning, verify roles have CREATEDB:

```sql
SELECT rolname, rolcreatedb FROM pg_roles WHERE rolname LIKE '%_user';
```

Expected output:
```
    rolname      | rolcreatedb
-----------------+-------------
 backstage_user  | t
 keycloak_user   | t
```
