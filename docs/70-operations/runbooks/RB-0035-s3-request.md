---
id: RB-0035-s3-request
title: S3 Bucket Request Operations (Runbook)
type: runbook
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: low
reliability:
  rollback_strategy: terraform-destroy
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0170
  - CL-0146
  - EC-0003-kong-backstage-plugin
  - EC-0004-backstage-copilot-plugin
  - RB-0007-tf-state-force-unlock
  - S3_REQUEST_FLOW
  - SCRIPT-0037
  - s3-catalog
  - session-2026-01-17-s3-request-flow-planning
category: runbooks
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:aws_s3
  - script:s3_request_parser
breaking_change: false
---
## S3 Bucket Request Operations (Runbook)

This runbook covers operational procedures for the S3 self-service request system.

## Overview

The S3 request flow follows contract-driven architecture:

```
Backstage Template → PR with Contract → CI Validation → Approval (if needed) → Apply Workflow → Terraform
```

**Key Files:**
- Schema: `schemas/requests/s3.schema.yaml`
- Parser: `scripts/s3_request_parser.py` (SCRIPT-0037)
- Contracts: `docs/20-contracts/s3-requests/{env}/S3-XXXX.yaml`
- Terraform: `modules/aws_s3/`
- State: `envs/{env}/s3/{id}/terraform.tfstate`

## Common Operations

### 1. Request a New S3 Bucket (Standard Path)

**Via Backstage (Recommended):**

1. Navigate to Backstage → Create → "Request S3 Bucket"
2. Fill in required fields:
   - Application name
   - Purpose type (logs, uploads, backups, data-lake, static-assets)
   - Environment (dev, test, staging, prod)
   - Owner team
   - Cost center
3. Submit → Workflow creates PR automatically
4. PR gets validated by CI
5. For dev + blocked access: auto-approvable
6. For staging/prod or exceptions: add `platform-approved` label
7. Merge PR
8. Run Apply workflow

### 2. Manual Contract Creation

If Backstage is unavailable:

```bash
# 1. Find next ID
NEXT_ID=$(find docs/20-contracts/s3-requests -name 'S3-*.yaml' 2>/dev/null | \
  sed 's/.*S3-\([0-9]*\)\.yaml/\1/' | sort -n | tail -1 || echo "0")
NEW_ID=$(printf "S3-%04d" $((${NEXT_ID:-0} + 1)))
echo "New ID: $NEW_ID"

# 2. Create contract file
ENV=dev
mkdir -p "docs/20-contracts/s3-requests/${ENV}"
cat > "docs/20-contracts/s3-requests/${ENV}/${NEW_ID}.yaml" << 'EOF'
apiVersion: goldenpath.io/v1
kind: S3BucketRequest
id: S3-0002
environment: dev
owner: app-team
application: my-app
requester: your-username

spec:
  bucketName: goldenpath-dev-my-app-uploads

  purpose:
    type: uploads
    description: "User file uploads for my-app"

  storageClass: standard

  encryption:
    type: sse-s3

  versioning: true
  publicAccess: blocked

  retentionPolicy:
    type: indefinite
    rationale: "User data must be retained for account lifetime"

  accessLogging:
    enabled: false

  costAlertGb: 100
  corsEnabled: false

  tags:
    costCenter: my-cost-center
EOF

# 3. Validate
python3 scripts/s3_request_parser.py \
  --mode validate \
  --input-files "docs/20-contracts/s3-requests/${ENV}/${NEW_ID}.yaml"
```

### 3. Validate a Contract

```bash
# Single file
python3 scripts/s3_request_parser.py \
  --mode validate \
  --input-files docs/20-contracts/s3-requests/dev/S3-0001.yaml

# All contracts in environment
python3 scripts/s3_request_parser.py \
  --mode validate \
  --input-files docs/20-contracts/s3-requests/dev/*.yaml

# Using Make target
make s3-validate S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml
```

### 4. Generate Terraform Variables (Dry Run)

```bash
# Dry run - prints output without writing
python3 scripts/s3_request_parser.py \
  --mode generate \
  --input-files docs/20-contracts/s3-requests/dev/S3-0001.yaml \
  --output-root envs \
  --dry-run

# Actual generation
python3 scripts/s3_request_parser.py \
  --mode generate \
  --input-files docs/20-contracts/s3-requests/dev/S3-0001.yaml \
  --output-root envs

# Using Make target
make s3-generate S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml
```

**Generated Files:**
- `envs/{env}/s3/generated/{id}.auto.tfvars.json` - Terraform variables
- `envs/generated/iam/{app}-s3-policy.json` - IAM policy for application access
- `docs/20-contracts/resource-catalogs/s3-catalog.yaml` - S3 catalog entry (post-apply)
- `governance/{env}/s3_request_audit.csv` - Audit record (post-apply)

### 5. Apply S3 Bucket (Create)

**Via GitHub Workflow (Recommended):**

1. Navigate to Actions → "S3 Requests (Apply)"
2. Click "Run workflow"
3. Enter:
   - `request_file`: `docs/20-contracts/s3-requests/dev/S3-0001.yaml`
   - `platform_approved`: Check if required (non-dev, public access, static-assets)
   - `allow_non_dev`: Check for staging/prod
   - `dry_run`: Check to validate without applying
4. Run workflow

**Via Make (Local):**

```bash
# Requires AWS credentials and backend config
make s3-apply \
  S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml \
  S3_STATE_BUCKET=goldenpath-idp-dev-bucket \
  S3_LOCK_TABLE=goldenpath-idp-dev-locks \
  S3_STATE_REGION=ap-southeast-2
```

### 6. Check Bucket Status

```bash
# Via AWS CLI
BUCKET=goldenpath-dev-my-app-uploads

# Check if bucket exists
aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null && echo "Exists" || echo "Not found"

# Get bucket configuration
aws s3api get-bucket-versioning --bucket "$BUCKET"
aws s3api get-bucket-encryption --bucket "$BUCKET"
aws s3api get-public-access-block --bucket "$BUCKET"
aws s3api get-bucket-logging --bucket "$BUCKET"
```

## Troubleshooting

### CI Validation Fails

**Error: "Missing required field"**

```
Check contract YAML for required fields:
- id, environment, owner, application, requester
- spec.bucketName, spec.purpose.type, spec.purpose.description
- spec.storageClass, spec.encryption.type
- spec.retentionPolicy.type, spec.retentionPolicy.rationale
- spec.costAlertGb
```

**Error: "Invalid bucket name format"**

```
Bucket name must match: goldenpath-{env}-{app}-{purpose}
Example: goldenpath-dev-payments-api-uploads
```

**Error: "SSE-KMS required for staging/prod"**

```yaml
# Fix: Use SSE-KMS with KMS alias
encryption:
  type: sse-kms
  kmsKeyAlias: alias/goldenpath-staging-s3
```

**Error: "Access logging required for staging/prod"**

```yaml
# Fix: Enable access logging
accessLogging:
  enabled: true
  targetBucket: goldenpath-staging-logs
```

### Apply Workflow Fails

**Error: "Platform approval is required"**

```
Conditions requiring approval:
- Non-dev environment (staging, prod)
- publicAccess: exception-approved
- purpose.type: static-assets

Solution: Check "platform_approved" when running workflow
```

**Error: "Non-dev apply requires allow_non_dev=true"**

```
For staging/prod environments:
- Check "allow_non_dev" input
- Ensure you have platform team authorization
```

**Error: "Terraform state lock"**

```bash
# Check for stuck lock
aws dynamodb scan \
  --table-name goldenpath-idp-dev-locks \
  --filter-expression "contains(LockID, :bucket)" \
  --expression-attribute-values '{":bucket":{"S":"s3/S3-0001"}}'

# If stuck, use force-unlock (see RB-0007)
terraform -chdir=envs/dev force-unlock LOCK_ID
```

### Bucket Creation Issues

**Error: "Bucket already exists"**

```
S3 bucket names are globally unique. If name collision:
1. Check if bucket is in another account
2. Modify application name to create unique bucket
3. Update contract with new bucket name
```

**Error: "KMS key not found"**

```bash
# Verify KMS alias exists
aws kms describe-key --key-id alias/goldenpath-dev-s3

# If missing, create via platform Terraform
```

## Approval Matrix

| Condition | Auto-Approve | Platform Approval Required |
|-----------|--------------|---------------------------|
| dev + blocked access | Yes | No |
| test + blocked access | Yes | No |
| staging environment | No | Yes |
| prod environment | No | Yes |
| publicAccess: exception-approved | No | Yes |
| purpose: static-assets | No | Yes |

**Approval Labels:** `platform-approved` or `s3-approved`

## Bucket Deletion (Break-Glass)

S3 bucket deletion is NOT automated. Follow this procedure:

### Pre-Deletion Checklist

- [ ] All objects in bucket have been removed or archived
- [ ] No active applications depend on bucket
- [ ] Final inventory exported (if needed)
- [ ] Approval from bucket owner
- [ ] Approval from platform team (for staging/prod)

### Step 1: Empty the Bucket

```bash
BUCKET=goldenpath-dev-my-app-uploads

# List objects (verify before deletion)
aws s3 ls "s3://${BUCKET}" --recursive

# Empty bucket (DESTRUCTIVE)
aws s3 rm "s3://${BUCKET}" --recursive

# If versioning enabled, also delete versions
aws s3api list-object-versions --bucket "$BUCKET" --output json | \
  jq -r '.Versions[]? | "--delete \"Objects=[{Key=\(.Key),VersionId=\(.VersionId)}]\""' | \
  xargs -I {} aws s3api delete-objects --bucket "$BUCKET" {}
```

### Step 2: Remove Terraform State

```bash
ENV=dev
S3_ID=S3-0001

cd envs/${ENV}
terraform state rm module.s3_bucket["${S3_ID}"]
```

### Step 3: Delete Bucket

```bash
aws s3api delete-bucket --bucket "$BUCKET"
```

### Step 4: Clean Up Contract

```bash
# Archive or delete the contract file
git rm "docs/20-contracts/s3-requests/${ENV}/${S3_ID}.yaml"
git commit -m "chore(s3): remove ${S3_ID} contract (bucket deleted)"
```

## Cost Monitoring

Buckets include cost alert thresholds. CloudWatch alarms are created:

```
Alarm Name: s3-cost-alert-{bucket-name}
Metric: BucketSizeBytes
Threshold: costAlertGb (converted to bytes)
```

**Check alarms:**

```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix "s3-cost-alert-goldenpath-dev"
```

## Related Resources

- [ADR-0170: S3 Self-Service Request System](../../adrs/ADR-0170-s3-self-service-request-system.md)
- [S3 Request Flow](../../85-how-it-works/self-service/S3_REQUEST_FLOW.md)
- [S3 Catalog](../../20-contracts/resource-catalogs/s3-catalog.yaml)
- [S3 Schema](../../../schemas/requests/s3.schema.yaml)
- [RB-0007: Terraform State Force Unlock](RB-0007-tf-state-force-unlock.md)
