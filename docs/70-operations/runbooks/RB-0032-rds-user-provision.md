---
id: RB-0032
title: RDS User and Database Provisioning
type: runbook
status: active
owner: platform-team
domain: platform-core
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - PRD-0001-rds-user-db-provisioning
  - ADR-0165-rds-user-db-provisioning-automation
  - SCRIPT-0035
tags:
  - rds
  - provisioning
  - database
  - automation
---

# RB-0032: RDS User and Database Provisioning

## Purpose

Provision PostgreSQL roles and databases on platform RDS instances based on
`application_databases` configuration in Terraform. This runbook covers both
automated (CI) and manual provisioning scenarios.

## Prerequisites

- AWS credentials with Secrets Manager read access
- Network access to RDS endpoint (VPC/security group)
- Python 3.9+ with boto3 and psycopg2-binary
- `envs/<env>-rds/terraform.tfvars` (standalone) or `envs/<env>/terraform.tfvars` (coupled)
- Secrets already created in AWS Secrets Manager:
  - Master: `goldenpath/<env>/rds/master`
  - Apps: `goldenpath/<env>/<app>/postgres`

## When to Use

**Note:** Provisioning is now automated. On merge to `development`, the `rds-database-apply.yml` workflow runs Terraform apply followed by a K8s Job for provisioning. Use this runbook for:

1. **Recovery**: If automated provisioning failed and needs manual retry
2. **Troubleshooting**: Use dry-run to verify configuration
3. **Ad-hoc**: When you need to provision outside the normal PR flow
4. **Non-dev environments**: Where additional approval is required

## Platform Engineer Testing

To test the full Backstage flow without using the UI, trigger the workflow directly via CLI:

```bash
# Simulate Backstage form submission (creates PR with all 8 fields)
gh workflow run create-rds-database.yml \
  --ref main \
  -f base_branch=development \
  -f database_name=test_inventory \
  -f username=test_inventory_user \
  -f owner=app-team \
  -f user=daniel-deans \
  -f domain=catalog \
  -f environment=dev \
  -f risk=medium \
  -f size=small \
  -f initial_schema=none
```

**What this does:**
1. Validates all inputs (same as Backstage would)
2. Updates RDS catalog (`docs/20-contracts/resource-catalogs/rds-catalog.yaml`)
3. Updates tfvars (`envs/dev-rds/terraform.tfvars`)
4. Creates a PR for review

**After PR is merged:**
```bash
make rds-apply ENV=dev        # Creates secret in Secrets Manager
make rds-provision-auto ENV=dev    # Creates PostgreSQL role + database
```

**Field reference:**

| Field | Required | Description |
|-------|----------|-------------|
| `database_name` | Yes | PostgreSQL database name (lowercase, underscores) |
| `username` | Yes | PostgreSQL role name (lowercase, underscores) |
| `owner` | Yes | Team owner (platform-team, app-team, etc.) |
| `user` | Yes | Requesting user (e.g., daniel-deans) |
| `domain` | Yes | Business domain (platform-core, catalog, etc.) |
| `environment` | Yes | Target env (dev, test, staging, prod) |
| `risk` | Yes | Data sensitivity (none, low, medium, high, access) |
| `size` | Yes | Instance size tier (small, medium, large, xlarge) |
| `initial_schema` | No | Schema template (none, basic-app, event-sourcing) |

## Standard Operations

### 1. Dry Run (Preview)

Always run dry-run first to verify configuration:

```bash
make rds-provision-auto-dry-run ENV=dev
```

Expected output shows what would be created without executing:

```
[DRY-RUN] Would create/update role: keycloak_user
[DRY-RUN] Would create database: keycloak with owner keycloak_user
[DRY-RUN] Would grant ALL on keycloak to keycloak_user
```

### 2. Provision (Dev)

For dev environment, no approval required:

```bash
make rds-provision-auto ENV=dev
```

### 3. Provision (Non-Dev)

For staging/prod, explicit approval is required:

```bash
ALLOW_DB_PROVISION=true make rds-provision-auto ENV=staging
ALLOW_DB_PROVISION=true make rds-provision-auto ENV=prod
```

### 3.1 Forcing Mode (Coupled vs Standalone)

If auto-detection is ambiguous, set the mode explicitly:

```bash
make rds-provision-auto ENV=dev RDS_MODE=coupled
make rds-provision-auto ENV=dev RDS_MODE=standalone
```

### 4. Provision with Audit Trail

Include build and run IDs for full traceability:

```bash
make rds-provision-auto ENV=dev BUILD_ID=16-01-26-01 RUN_ID=12345678
```

## Troubleshooting

### Issue: Secret Not Found

**Symptom:**
```
RuntimeError: Secret not found: goldenpath/dev/keycloak/postgres
```

**Resolution:**
1. Verify secret exists in AWS Secrets Manager
2. Check secret path format: `goldenpath/<env>/<app>/postgres`
3. Run Terraform to create missing secrets:
   ```bash
   make rds-apply ENV=dev
   ```

### Issue: Connection Timeout

**Symptom:**
```
RuntimeError: Failed to connect to RDS: connection timed out
```

**Resolution:**
1. Verify VPC/security group allows connection from your IP
2. Check RDS endpoint is correct in master secret
3. Verify RDS instance is running:
   ```bash
   aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]'
   ```

### Issue: Permission Denied

**Symptom:**
```
psycopg2.errors.InsufficientPrivilege: permission denied to create role
```

**Resolution:**
1. Verify master credentials have CREATE ROLE privilege
2. Check master user is not restricted:
   ```sql
   SELECT rolcreaterole FROM pg_roles WHERE rolname = 'platform_admin';
   ```

### Issue: Database Exists with Wrong Owner

**Symptom:**
```
[WARNING] Database keycloak exists but owner is postgres, expected keycloak_user
```

**Resolution:**
1. This is a warning, not an error - database exists
2. To change owner (if safe):
   ```sql
   ALTER DATABASE keycloak OWNER TO keycloak_user;
   ```
3. Or accept current owner if intentional

### Issue: Role Already Exists

**Symptom:**
```
[NO_CHANGE] Password updated for existing role: keycloak_user
```

**Resolution:**
- This is normal idempotent behavior
- Password is updated to match Secrets Manager value
- No action needed

## Audit Records

Provisioning emits CSV audit records to stdout:

```csv
timestamp_utc,environment,build_id,run_id,database,username,action,status,duration_ms,message
2026-01-16T10:30:00Z,dev,16-01-26-01,12345678,keycloak,keycloak_user,create_role,success,45,Role created
```

Status values:
- `success`: Resource created
- `no_change`: Resource already exists (idempotent)
- `warning`: Resource exists but needs attention
- `error`: Operation failed
- `dry_run`: Preview only, no changes made

## Related Documentation

- [PRD-0001: RDS User and Database Provisioning](../../20-contracts/prds/PRD-0001-rds-user-db-provisioning.md)
- [ADR-0165: Automated RDS Provisioning](../../adrs/ADR-0165-rds-user-db-provisioning-automation.md)
- [RB-0029: RDS Manual Secret Rotation](./RB-0029-rds-manual-secret-rotation.md)
- [RB-0030: RDS Break-Glass Deletion](./RB-0030-rds-break-glass-deletion.md)

## Script Reference

**Script**: `scripts/rds_provision.py`

**Full CLI Usage**:
```bash
python3 scripts/rds_provision.py \
  --env dev \
  --tfvars envs/dev-rds/terraform.tfvars \
  --master-secret goldenpath/dev/rds/master \
  --build-id 16-01-26-01 \
  --run-id 12345678 \
  --region eu-west-2 \
  [--dry-run] \
  [--require-approval]
```

**Arguments**:
- `--env`: Environment (dev, test, staging, prod)
- `--tfvars`: Path to terraform.tfvars with application_databases
- `--master-secret`: Secrets Manager path for master credentials
- `--build-id`: Build ID for audit trail (default: manual)
- `--run-id`: CI run ID for audit trail (default: local)
- `--region`: AWS region (default: eu-west-2)
- `--dry-run`: Preview without executing
- `--require-approval`: Require ALLOW_DB_PROVISION=true for non-dev
