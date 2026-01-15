# Claude Session Summary - 2026-01-15

**Last Updated:** 2026-01-15T15:30:00Z
**Status:** IN PROGRESS - Fixing terraform plan error
**Branch:** `feature/tooling-apps-config`
**Latest Commit:** `9ff1a099` - fix: resolve RDS, Backstage, and workflow inconsistencies

---

## Session Overview

This session has three phases:

1. **Phase 1 (Morning)**: Implemented Standalone RDS Bounded Context, Backstage self-service templates, and governance registry sync
2. **Phase 2 (Afternoon)**: Comprehensive code review identifying and fixing 12 issues across RDS, Backstage, and workflow configurations
3. **Phase 3 (Current)**: ADR-0160 RDS Toggle Integration, Test Framework Compliance, Terraform Plan Error Fix

---

## Phase 3: RDS Toggle & Terraform Fix (Current Session)

### 1. ADR-0160: RDS Optional Toggle Integration

**Created:** `docs/adrs/ADR-0160-rds-optional-toggle-integration.md`

Extends ADR-0158 to support TWO deployment options:
- **Option A (Existing)**: Standalone RDS in `envs/dev-rds/` - wired to Backstage
- **Option B (New)**: Coupled RDS with EKS via `rds_config.enabled` toggle

**Key Insight:** Users can deploy EKS with/without RDS, and add RDS later if needed.

### 2. Test Framework Compliance (SCRIPT-0034)

**Created test artifacts per PR gate requirements:**
- `tests/scripts/rds-request-parser/test-plan.md` - 16 test cases
- `tests/scripts/rds-request-parser/test-record-20260115.md` - 100% pass rate
- `tests/scripts/rds-request-parser/actual-output.txt` - Raw pytest output
- Updated `tests/README.md` dashboard with Script Unit Tests section

**Result:** 16/16 tests passed for RDS Request Parser

### 3. Terraform Plan Error (IN PROGRESS)

**Error:**
```
Error: Failed to construct REST client

  with kubernetes_manifest.cluster_secret_store[0],
  on main.tf line 464, in resource "kubernetes_manifest" "cluster_secret_store":
 464: resource "kubernetes_manifest" "cluster_secret_store" {

cannot create REST client: no client config
```

**Root Cause:** The `kubernetes_manifest` resource validates against the Kubernetes API during `terraform plan`, not just apply. When no cluster exists, this fails.

**Fix:** Replace `kubernetes_manifest` with `kubectl_manifest` (gavinbunney/kubectl provider) which doesn't require cluster access during plan phase.

### Files Modified/Created in Phase 3

```
docs/adrs/ADR-0160-rds-optional-toggle-integration.md     # NEW - RDS toggle architecture
docs/changelog/entries/CL-0130-rds-optional-toggle-integration.md  # NEW
tests/scripts/rds-request-parser/test-plan.md             # NEW - Test plan
tests/scripts/rds-request-parser/test-record-20260115.md  # NEW - Test record
tests/scripts/rds-request-parser/actual-output.txt        # NEW - Raw output
tests/README.md                                           # UPDATED - Dashboard
envs/dev/main.tf                                          # IN PROGRESS - kubectl fix
```

---

---

## Phase 2: Code Review & Bug Fixes (This Session)

### Issues Identified and Fixed

#### CRITICAL Fixes (3)

| Issue | File | Fix |
|-------|------|-----|
| **Duplicate RDS config** | `envs/dev/main.tf:528-576` | Removed `module.platform_rds` block that violated ADR-0158 standalone architecture |
| **Missing required field** | `backstage-catalog/templates/rds-request.yaml:23` | Added `domain` to required fields list - was causing workflow failures |
| **Wrong var-file path** | `.github/workflows/secret-request-pr.yml:130` | Fixed path from `../../.tmp/generated/$SERVICE/$ID.auto.tfvars.json` to `../../.tmp/generated/$ENV/secrets/generated/$SERVICE/$ID.auto.tfvars.json` |

#### HIGH Priority Fix (1)

| Issue | File | Fix |
|-------|------|-----|
| **Dead code** | `governance-registry-writer.yml:168-189` | Removed PR comment step that could never execute (workflow only triggers on push, not PR) |

#### MEDIUM Priority Fixes (3)

| Issue | File | Fix |
|-------|------|-----|
| **Inconsistent domain enums** | ECR + RDS templates | Added `application` domain to ECR, added `test` environment to RDS, removed `unknown` owner |
| **Redundant password fields** | `envs/dev-rds/main.tf:304-312` | Removed `postgres-password`, `admin-password`, `dbInstanceIdentifier` from app secrets |
| **Legacy RDS config** | `envs/dev/terraform.tfvars:233-245` | Set `enabled = false` with migration note pointing to standalone config |

### Files Modified in Phase 2

```
envs/dev/main.tf                                    # Removed module.platform_rds block
envs/dev/terraform.tfvars                           # Disabled rds_config with migration note
envs/dev-rds/main.tf                                # Cleaned up redundant secret fields
backstage-helm/backstage-catalog/templates/rds-request.yaml    # Added domain to required, test env
backstage-helm/backstage-catalog/templates/ecr-request.yaml    # Added application domain, removed unknown owner
.github/workflows/secret-request-pr.yml             # Fixed var-file paths
.github/workflows/governance-registry-writer.yml    # Removed dead PR comment step
```

### Commit

```
git commit -m "fix: resolve RDS, Backstage, and workflow inconsistencies"
git push origin feature/tooling-apps-config
```

---

## Phase 1 Summary (Earlier Today)

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

### 2. Created Secret Rotation CI Enforcement

**Scheduled Alert Workflow** (`.github/workflows/secret-rotation-check.yml`):
- Runs daily at 06:00 UTC
- Creates GitHub issues when secrets are OVERDUE

**Soft PR Gate** (`.github/workflows/pr-secret-rotation-warning.yml`):
- Posts warning comment (non-blocking)

### 3. Added Makefile RDS Targets

```makefile
make rds-init ENV=dev     # Initialize RDS Terraform
make rds-plan ENV=dev     # Plan RDS changes
make rds-apply ENV=dev    # Apply RDS
make rds-status ENV=dev   # Show RDS outputs
# NO rds-destroy - intentional per ADR-0158
```

### 4. Created Operational Runbooks

- `docs/70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md`
- `docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md`

### 5. Backstage Self-Service Templates

- `backstage-helm/backstage-catalog/templates/rds-request.yaml` - RDS database requests
- `.github/workflows/create-rds-database.yml` - Workflow triggered by template

### 6. Governance Registry Sync

- Modified `governance-registry-writer.yml` to sync Backstage catalog
- Updated `backstage-helm/charts/backstage/values.yaml` to point to registry branch
- Created ADR-0159 and CL-0129

### 7. Directory Renames (Clarity)

- `docs/catalogs/` → `docs/20-contracts/secret-requests/`
- `backstage-helm/catalog/` → `backstage-helm/backstage-catalog/`
- Created `docs/85-how-it-works/governance/CATALOG_SYSTEMS.md` explaining two-catalog architecture

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

### ADR-0159: Backstage Catalog Registry Sync

- Backstage catalog synced to `governance-registry` branch
- Stable URL for all environments
- Template changes flow through PR review

---

## Testing Checklist

### 1. RDS Standalone
```bash
make rds-init ENV=dev
make rds-plan ENV=dev
make rds-apply ENV=dev
make rds-status ENV=dev
```

### 2. EKS Cluster
```bash
make init ENV=dev
make plan ENV=dev
make apply ENV=dev BUILD_ID=15-01-26-09
make bootstrap ENV=dev
```

### 3. Backstage Templates
- RDS Request: Fill form, verify workflow triggers and PR created
- ECR Request: Verify `application` domain available, `unknown` owner removed

### 4. Secret Request Workflows
```bash
# Manual request
gh workflow run request-app-secret.yml --ref development -f environment=dev ...

# Verify PR workflow uses correct paths
# Verify apply workflow commits generated files
```

### 5. Governance Registry
```bash
git fetch origin governance-registry
git show origin/governance-registry:backstage-catalog/all.yaml
```

### 6. Quick Smoke Tests
```bash
terraform -chdir=envs/dev validate                    # Success
terraform fmt -check -recursive                       # No changes needed
grep "module.platform_rds" envs/dev/main.tf           # No results
grep -A10 "required:" backstage-helm/backstage-catalog/templates/rds-request.yaml | grep domain  # Found
```

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

## What Was NOT Done (Future Work)

1. **Lambda-based automatic rotation (V1.1)** - Deferred for simplicity
2. **Staging/Prod RDS environments** - Only dev-rds created
3. **ADR index gaps** - adr-0091, adr-0105-0109 missing from Backstage index (intentional gaps)

---

## If Continuing This Work

1. **To test full deployment:**
   ```bash
   make rds-init ENV=dev
   make rds-plan ENV=dev
   # If VPC exists:
   make rds-apply ENV=dev
   make apply ENV=dev BUILD_ID=15-01-26-09
   make bootstrap ENV=dev
   ```

2. **To create staging/prod RDS:**
   - Copy `envs/dev-rds/` to `envs/staging-rds/` and `envs/prod-rds/`
   - Update `terraform.tfvars` for each environment

3. **To implement V1.1 Lambda rotation:**
   - Uncomment Lambda resources in `envs/dev-rds/main.tf`
   - Package `rotation_lambda/lambda_function.py`

---

## Contact/References

- ADR-0158: `docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md`
- ADR-0159: `docs/adrs/ADR-0159-backstage-catalog-registry-sync.md`
- Architecture: `docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md`
- Catalog Systems: `docs/85-how-it-works/governance/CATALOG_SYSTEMS.md`
- Runbooks: `docs/70-operations/runbooks/RB-0029-*.md` and `RB-0030-*.md`
