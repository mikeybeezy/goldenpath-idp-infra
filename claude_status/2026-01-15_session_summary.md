# Claude Session Summary - 2026-01-15

**Last Updated:** 2026-01-15T~14:00:00Z
**Status:** COMPLETED - All tasks finished

---

## Session Overview

This session focused on implementing a **Standalone RDS Bounded Context** for the Goldenpath IDP platform. The RDS is designed as persistent infrastructure that survives cluster rebuilds, with intentionally difficult deletion (console-only).

---

## Completed Tasks

### 1. Created Standalone RDS Terraform Root (`envs/dev-rds/`)

**Files Created:**
- `envs/dev-rds/main.tf` - RDS instance, security groups, secrets, CloudWatch alarms
- `envs/dev-rds/variables.tf` - Region-agnostic configuration
- `envs/dev-rds/outputs.tf` - Outputs for debugging
- `envs/dev-rds/terraform.tfvars` - Dev environment values
- `envs/dev-rds/rotation_lambda/lambda_function.py` - Lambda code (deferred to V1.1)

**Key Features:**
- VPC discovery via tags (not direct Terraform reference)
- `deletion_protection = true` (AWS-level)
- `prevent_destroy = true` lifecycle (Terraform-level)
- SSL required via parameter group
- Multi-tenant: keycloak + backstage databases
- CloudWatch alarms for CPU, memory, storage, connections, latency

### 2. Simplified V1 - Deferred Lambda Rotation to V1.1

- Removed Lambda-based automatic rotation from `main.tf`
- Added comments explaining V1 manual rotation approach
- Lambda code kept in `rotation_lambda/` for V1.1

### 3. Created Secret Rotation CI Enforcement

**Scheduled Alert Workflow** (`.github/workflows/secret-rotation-check.yml`):
- Runs daily at 06:00 UTC
- Checks secrets in dev, staging, prod
- Creates GitHub issues when secrets are OVERDUE
- Posts warnings when approaching deadline (5 days default)

**Soft PR Gate** (`.github/workflows/pr-secret-rotation-warning.yml`):
- Triggers on infrastructure PRs (envs/**, modules/**, etc.)
- Posts warning comment (non-blocking)
- Updates existing comment on subsequent pushes

### 4. Added Makefile RDS Targets

Added to `Makefile`:
```makefile
make rds-init ENV=dev     # Initialize RDS Terraform
make rds-plan ENV=dev     # Plan RDS changes
make rds-apply ENV=dev    # Apply RDS
make rds-status ENV=dev   # Show RDS outputs
# NO rds-destroy - intentional per ADR-0158
```

### 5. Created Operational Runbooks

- `docs/70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md`
  - Step-by-step manual rotation procedure
  - AWS CLI commands for password generation, DB update, secrets update
  - Rollback procedure

- `docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md`
  - Intentionally difficult deletion process
  - Pre-deletion checklist
  - Console-only steps (no CLI deletion)
  - Snapshot creation and cleanup

### 6. Updated Documentation

- `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
  - Reflects standalone bounded context approach
  - Updated deployment sequence
  - Added secret rotation section
  - Added CloudWatch alarms table
  - Links to new runbooks

### 7. Added to Capability Ledger & Features List

- `docs/00-foundations/product/CAPABILITY_LEDGER.md`
  - Added **Capability #22: Standalone Platform RDS (Persistent Data Layer)**
  - Documents bounded context architecture, multi-layer deletion protection, CI-enforced rotation
  - Added "Data Layer: AWS RDS PostgreSQL" to Technical Foundation

- `docs/00-foundations/product/FEATURES.md`
  - Added **Standalone Platform RDS** to Delivery & Self-Service section

---

## Architecture Decisions

### ADR-0158: Platform Standalone RDS Bounded Context

**Key Principles:**
1. **Persistent**: RDS survives cluster rebuilds
2. **Separate State**: Own Terraform root (`envs/{env}-rds/`)
3. **Protected**: Multiple layers prevent accidental deletion
4. **Region Agnostic**: No hardcoded regions

**Deployment Order:**
```bash
# 1. Deploy RDS first (persistent)
make rds-apply ENV=dev

# 2. Deploy EKS cluster (ephemeral)
make apply ENV=dev BUILD_ID=xx-xx-xx-xx

# 3. Bootstrap
make bootstrap ENV=dev
```

---

## Files Modified/Created Summary

### New Files
```
envs/dev-rds/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
└── rotation_lambda/
    └── lambda_function.py

.github/workflows/
├── secret-rotation-check.yml
├── pr-secret-rotation-warning.yml
└── create-rds-database.yml           # Backstage workflow for RDS requests

docs/70-operations/runbooks/
├── RB-0029-rds-manual-secret-rotation.md
└── RB-0030-rds-break-glass-deletion.md

backstage-helm/catalog/templates/
└── rds-request.yaml                  # Backstage self-service template
```

### Modified Files
```
Makefile                                          # Added rds-* targets
docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md  # Updated for bounded context
docs/00-foundations/product/CAPABILITY_LEDGER.md  # Added capability #22
docs/00-foundations/product/FEATURES.md           # Added RDS feature
backstage-helm/catalog/all.yaml                   # Registered RDS template
```

---

## Backstage Catalog on Governance Registry

The Backstage catalog is now synced to the `governance-registry` branch for stable, environment-agnostic access:

- **Catalog URL**: `https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/governance-registry/backstage-catalog/all.yaml`
- **Sync Workflow**: `governance-registry-writer.yml` copies catalog on every push to development/main
- **Schema Update**: `govreg.schema.yaml` updated to allow `backstage-catalog/` directory

Benefits:

- All environments (dev/staging/prod) point to same stable catalog
- Template changes flow through PR review before reaching registry
- No need to update Backstage config per environment

---

## Backstage Self-Service RDS Template

### Template: `backstage-helm/catalog/templates/rds-request.yaml`

Teams can now request RDS databases via Backstage self-service. The template:

- Collects database name, username, owner, domain, environment, risk level
- Triggers `.github/workflows/create-rds-database.yml`
- Workflow updates:
  - `docs/20-contracts/catalogs/rds-catalog.yaml` (governance catalog)
  - `envs/{env}-rds/terraform.tfvars` (Terraform configuration)
- Creates a PR for platform team review

### Flow

1. Developer fills form in Backstage
2. Template dispatches `create-rds-database.yml` workflow
3. Workflow updates catalog + tfvars idempotently
4. PR created with full details and security controls
5. After merge: `make rds-apply ENV={env}` provisions database
6. Credentials available in AWS Secrets Manager

---

## What Was NOT Done (Future Work)

1. **Remove RDS from envs/dev/main.tf** - Skipped because the standalone RDS is a NEW addition, not a migration from existing code

2. **Lambda-based automatic rotation (V1.1)** - Deferred for simplicity. Lambda code exists in `rotation_lambda/` but is not deployed

3. **Staging/Prod RDS environments** - Only dev-rds created. Staging/prod follow same pattern

---

## Key Configuration Values

### Dev Environment
- Instance Class: `db.t3.micro`
- Engine: PostgreSQL 15.4
- Storage: 20-50 GB (autoscaling)
- Multi-AZ: false
- Backup Retention: 7 days
- Secret Rotation: 30 days
- Applications: keycloak, backstage

### Secret Paths
- Master: `goldenpath/dev/rds/master`
- Keycloak: `goldenpath/dev/keycloak/postgres`
- Backstage: `goldenpath/dev/backstage/postgres`

---

## Previous Session Context (2026-01-14)

The previous session covered:
1. Local development overlays for Kind cluster
2. Local values files for all tooling apps (keycloak, backstage, kong, etc.)
3. Initial RDS architecture documentation
4. ADR-0157 (superseded by ADR-0158)
5. Secrets lifecycle documentation

---

## If Continuing This Work

1. **To test RDS deployment:**
   ```bash
   cd /Users/mikesablaze/Documents/relaunch/goldenpath-idp-infra
   make rds-init ENV=dev
   make rds-plan ENV=dev
   ```

2. **To verify CI workflows:**
   - Check `.github/workflows/secret-rotation-check.yml`
   - Check `.github/workflows/pr-secret-rotation-warning.yml`

3. **To implement V1.1 Lambda rotation:**
   - Uncomment Lambda resources in `envs/dev-rds/main.tf`
   - Package `rotation_lambda/lambda_function.py` into zip
   - Add `rotation_lambda.zip` to the deploy

4. **To create staging/prod RDS:**
   - Copy `envs/dev-rds/` to `envs/staging-rds/` and `envs/prod-rds/`
   - Update `terraform.tfvars` for each environment

---

## Contact/References

- ADR: `docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md`
- Architecture: `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
- Runbooks: `docs/70-operations/runbooks/RB-0029-*.md` and `RB-0030-*.md`
