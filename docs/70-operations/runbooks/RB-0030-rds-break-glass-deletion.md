---
id: RB-0030-rds-break-glass-deletion
title: RDS Break-Glass Deletion Procedure (Runbook)
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: critical
  security_risk: high
  coupling_risk: high
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
  maturity: 1
schema_version: 1
relates_to:
  - 30_PLATFORM_RDS_ARCHITECTURE
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0160
  - CAPABILITY_LEDGER
  - CL-0140
  - DOCS_RUNBOOKS_README
  - EC-0001-knative-integration
  - RB-0029-rds-manual-secret-rotation
  - RB-0032
  - RB-0033-persistent-cluster-teardown
  - RDS_REQUEST_FLOW
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:rds
  - module:terraform
breaking_change: false
---

## RDS Break-Glass Deletion Procedure (Runbook)

This runbook documents the intentionally difficult process for deleting platform RDS instances.

**IMPORTANT:** RDS deletion is intentionally difficult and confirmation-gated. Use the
break-glass steps below when deletion is required.

## Why Manual Deletion?

Per ADR-0158, platform RDS is designed to be:

- **Persistent**: Survives cluster rebuilds
- **Protected**: Multiple layers prevent accidental deletion
- **Auditable**: Deletion requires human verification

## Protection Layers

1. **Terraform `deletion_protection = true`**: AWS-level protection
2. **Terraform `prevent_destroy` lifecycle**: Terraform refuses to destroy
3. **No standard destroy target**: Only `rds-destroy-break-glass` exists and requires explicit approval
4. **No CI workflow**: No automated destroy pipeline

## Pre-Deletion Checklist

Before proceeding, verify ALL of the following:

- [ ] All dependent applications are stopped or migrated
- [ ] Final backup has been created and verified
- [ ] All application data has been exported (if needed)
- [ ] Approval obtained from data owner
- [ ] Approval obtained from security team
- [ ] Incident ticket created documenting deletion reason
- [ ] Post-deletion cleanup plan documented

## Step 1: Create Final Snapshot

```bash
ENVIRONMENT=dev
make rds-init ENV=${ENVIRONMENT}
IDENTIFIER="$(aws rds describe-db-instances \
  --region eu-west-2 \
  --query 'DBInstances[].DBInstanceIdentifier' \
  --output text | awk '{print $1}' | tr -cd '[:alnum:]-')"

SNAPSHOT_NAME="$(printf '%s-final-%s' "${IDENTIFIER}" "$(date +%Y%m%d-%H%M%S)" | tr -cd '[:alnum:]-')"

aws rds create-db-snapshot \
  --db-instance-identifier "${IDENTIFIER}" \
  --db-snapshot-identifier "${SNAPSHOT_NAME}" \
  --region eu-west-2

# Wait for snapshot
aws rds wait db-snapshot-available \
  --db-snapshot-identifier "${SNAPSHOT_NAME}" \
  --region eu-west-2

echo "Final snapshot created: ${SNAPSHOT_NAME}"
```

## Step 2: Disable Deletion Protection (CLI or Console)

Preferred CLI path:

```bash
make rds-allow-delete ENV=dev CONFIRM_RDS_DELETE=yes
```

Console fallback:

1. Navigate to AWS Console > RDS > Databases
2. Select the database instance
3. Click "Modify"
4. Uncheck "Enable deletion protection"
5. Click "Continue"
6. Select "Apply immediately"
7. Click "Modify DB instance"
8. Wait for modification to complete

## Step 3: Allow Terraform Destroy (Prevent Destroy Toggle)

You can either toggle `prevent_destroy` temporarily or use the break-glass target.

**Option A: Manual toggle (main.tf)**

```bash
# Edit envs/dev-rds/main.tf
prevent_destroy = false
```

Restore `prevent_destroy = true` after the destroy completes.

**Option B: Use break-glass target (recommended)**

```bash
make rds-destroy-break-glass ENV=dev CONFIRM_DESTROY_DATABASE_PERMANENTLY=YES
```

Note: The break-glass target temporarily sets `skip_final_snapshot = true` to
avoid snapshot identifier collisions. Use Step 1 to create the final snapshot.

If destroy fails with `DBSnapshotAlreadyExists`, it usually means an older
snapshot with the default identifier still exists and Terraform is reusing it
because `final_snapshot_identifier` is in `ignore_changes`. Delete the stale
snapshot and retry:

```bash
aws rds delete-db-snapshot \
  --db-snapshot-identifier goldenpath-dev-platform-dev-final-snapshot \
  --region eu-west-2

aws rds wait db-snapshot-deleted \
  --db-snapshot-identifier goldenpath-dev-platform-dev-final-snapshot \
  --region eu-west-2
```

## Step 4: Destroy RDS Instance (Terraform)

If you toggled in `main.tf`:

```bash
terraform -chdir=envs/dev-rds destroy -auto-approve
```

If you used the break-glass target, the destroy is already executed.

## Step 5: Clean Up Related Resources

After RDS deletion, clean up related resources:

### Secrets Manager

```bash
ENVIRONMENT=dev

# Delete secrets (with recovery window or force)
for SECRET in \
  "goldenpath/${ENVIRONMENT}/rds/master" \
  "goldenpath/${ENVIRONMENT}/keycloak/postgres" \
  "goldenpath/${ENVIRONMENT}/backstage/postgres"; do

  aws secretsmanager delete-secret \
    --secret-id "${SECRET}" \
    --recovery-window-in-days 7  # Or --force-delete-without-recovery
done
```

### Security Groups

```bash
# Remove from Terraform state first, then delete manually if needed
```

### Subnet Groups

```bash
# These are usually deleted when RDS is deleted
# Verify and clean up if orphaned
```

## Step 6: Document Deletion

Update the incident ticket with:

- Timestamp of deletion
- Final snapshot identifier
- Any issues encountered
- Confirmation of cleanup completion

## Recovery From Snapshot

If you need to restore the RDS instance:

```bash
SNAPSHOT_NAME="goldenpath-platform-db-dev-final-YYYYMMDD-HHMMSS"
NEW_IDENTIFIER="goldenpath-platform-db-dev"

aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier "${NEW_IDENTIFIER}" \
  --db-snapshot-identifier "${SNAPSHOT_NAME}" \
  --db-instance-class db.t3.micro \
  --region eu-west-2

# Then re-import into Terraform state
cd envs/dev-rds
terraform import aws_db_instance.platform "${NEW_IDENTIFIER}"
```

## Related Resources

- [ADR-0158: Platform RDS Bounded Context](../../../docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md)
- [Platform RDS Architecture](../30_PLATFORM_RDS_ARCHITECTURE.md)
- [RB-0029: Manual Secret Rotation](RB-0029-rds-manual-secret-rotation.md)
