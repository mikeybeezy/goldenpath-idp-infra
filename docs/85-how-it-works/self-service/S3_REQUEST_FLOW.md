---
id: S3_REQUEST_FLOW
title: 'How It Works: S3 Bucket Request Flow'
type: documentation
relates_to:
  - ADR-0170
  - CATALOG_SYSTEMS
  - CL-0146
  - CONTRACT_DRIVEN_ARCHITECTURE
  - RB-0035-s3-request
  - SCRIPT-0037
  - agent_session_summary
  - s3-catalog
  - session-2026-01-17-s3-request-flow-planning
---
## How It Works: S3 Bucket Request Flow

This document explains the technical lifecycle of an S3 bucket request, from the developer form in Backstage to a fully provisioned, secured bucket in AWS.

## 0. High-Level Architecture

The platform uses a contract-driven approach to S3 provisioning. Each bucket request creates a contract file that drives validation, approval, and Terraform execution.

```text
+---------------+       +-----------------------+
|   Backstage   | ----> | GitHub Actions Dispatch|
+---------------+       +-----------------------+
                                  |
                      ( 1. Calculate S3-XXXX ID )
                      ( 2. Derive bucket name   )
                      ( 3. Apply guardrails     )
                                  |
          +-----------------------+-------+-----------------------+
          |                               |                       |
+-----------------------+       +-----------------------+   +-----------------------+
|  Create S3 Contract   |       |  Validate Contract    |   |  Generate PR Body     |
+-----------------------+       +-----------------------+   +-----------------------+
          |                               |                       |
          +-----------------------+-------+-----------------------+
                                  |
                        ( 4. Create PR )
                                  |
+-----------------------+         |
| CI Validation         | <-------+
| (s3-approval-guard)   |
+-----------------------+
          |
          | (PR Merged)
          v
+-----------------------+
| S3 Apply Workflow     |
+-----------------------+
          |
          +---------------+---------------+
          |                               |
  +---------------+             +-------------------+
  | S3 Bucket     |             | CloudWatch Alarm  |
  +---------------+             +-------------------+
```

## 1. Trigger: Backstage Template

Application teams use the **"Request S3 Bucket"** template in the Backstage Software Catalog. The template collects:

| Field | Description | Example |
|-------|-------------|---------|
| `application` | Application name | `payments-api` |
| `purposeType` | Bucket purpose | `logs`, `uploads`, `backups`, `data-lake`, `static-assets` |
| `purposeDescription` | Detailed description | "User file uploads for payment receipts" |
| `owner` | Owning team | `app-team` |
| `requester` | Requesting user | `daniel-deans` |
| `environment` | Target environment | `dev`, `test`, `staging`, `prod` |
| `costCenter` | Cost allocation | `payments-123` |
| `costAlertGb` | Storage threshold for alert | `100` |
| `storageClass` | S3 storage class | `standard`, `intelligent-tiering`, `standard-ia`, `glacier` |
| `versioning` | Enable versioning | `true` |
| `corsEnabled` | Enable CORS | `false` |
| `retentionType` | Data retention strategy | `indefinite`, `time-bounded`, `compliance-driven` |
| `retentionRationale` | Why this retention policy | "User data retained for account lifetime" |
| `publicAccess` | Public access setting | `blocked`, `exception-approved` |

The template triggers `create-s3-bucket.yml` via `github:actions:dispatch`.

## 2. Processing: Workflow Execution

The GitHub Actions workflow performs automated operations:

### 2.1 ID Calculation

```bash
# Find existing S3 requests and calculate next ID
EXISTING=$(find docs/20-contracts/s3-requests -name 'S3-*.yaml' | \
  sed 's/.*S3-\([0-9]*\)\.yaml/\1/' | sort -n | tail -1)
NEXT=$((${EXISTING:-0} + 1))
ID=$(printf "S3-%04d" $NEXT)
# Result: S3-0001, S3-0002, etc.
```

### 2.2 Bucket Name Derivation

```bash
BUCKET="goldenpath-${ENV}-${APP}-${PURPOSE}"
# Example: goldenpath-dev-payments-api-uploads
```

### 2.3 Environment-Specific Guardrails

The workflow auto-applies security guardrails based on environment:

| Environment | Encryption | Access Logging | Notes |
|-------------|------------|----------------|-------|
| dev | SSE-S3 | Optional | Developer flexibility |
| test | SSE-S3 | Optional | Developer flexibility |
| staging | **SSE-KMS** | **Required** | Pre-production security |
| prod | **SSE-KMS** | **Required** | Full production security |

```bash
# Staging/Prod automatically get:
encryption:
  type: sse-kms
  kmsKeyAlias: alias/goldenpath-${ENV}-s3

accessLogging:
  enabled: true
  targetBucket: goldenpath-${ENV}-logs
```

### 2.4 Contract Generation

Creates `docs/20-contracts/s3-requests/{env}/S3-XXXX.yaml`:

```yaml
apiVersion: goldenpath.io/v1
kind: S3BucketRequest
id: S3-0001
environment: dev
owner: app-team
application: payments-api
requester: daniel-deans

spec:
  bucketName: goldenpath-dev-payments-api-uploads

  purpose:
    type: uploads
    description: "User file uploads for payment receipts"

  storageClass: standard

  encryption:
    type: sse-s3

  versioning: true
  publicAccess: blocked

  retentionPolicy:
    type: indefinite
    rationale: "User data retained for account lifetime"

  accessLogging:
    enabled: false

  costAlertGb: 100
  corsEnabled: false

  tags:
    costCenter: payments-123
```

### 2.5 Contract Validation

Before creating the PR, the workflow validates the contract:

```bash
python3 scripts/s3_request_parser.py \
  --mode validate \
  --input-files "docs/20-contracts/s3-requests/${ENV}/${ID}.yaml"
```

## 3. Review: Pull Request

The workflow creates a PR with comprehensive details:

- Bucket configuration summary
- Environment-specific settings
- Approval requirements based on conditions
- Links to S3 catalog and ADR-0170

### Approval Matrix

| Condition | Auto-Approve | Platform Approval |
|-----------|--------------|-------------------|
| dev + blocked access | Yes | No |
| test + blocked access | Yes | No |
| staging environment | No | Required |
| prod environment | No | Required |
| `publicAccess: exception-approved` | No | Required |
| `purpose: static-assets` | No | Required |

**Approval Labels:** `platform-approved` or `s3-approved`

### CI Guards

Two workflows enforce approval:

1. **`ci-s3-request-validation.yml`**: Validates contract schema and guardrails
2. **`s3-approval-guard.yml`**: Blocks PR until approval label added (when required)

## 4. Execution: Apply Workflow

After PR approval and merge, run the apply workflow:

**Via GitHub Actions (Recommended):**

1. Navigate to Actions → "S3 Requests (Apply)"
2. Enter request file path: `docs/20-contracts/s3-requests/dev/S3-0001.yaml`
3. Check approval boxes if required
4. Run workflow

**Via Make (Local):**

```bash
make s3-apply \
  S3_REQUEST=docs/20-contracts/s3-requests/dev/S3-0001.yaml \
  S3_STATE_BUCKET=goldenpath-idp-dev-bucket \
  S3_LOCK_TABLE=goldenpath-idp-dev-locks \
  S3_STATE_REGION=ap-southeast-2
```

### Apply Workflow Steps

1. **Validate** contract with parser
2. **Generate** Terraform tfvars + IAM policy
3. **Commit** generated files to repo
4. **Init** Terraform with per-bucket state isolation
5. **Apply** Terraform to create bucket
6. **Update** S3 catalog + append audit trail

### Per-Bucket State Isolation

Each bucket has isolated Terraform state:

```text
State Key: envs/{env}/s3/{id}/terraform.tfstate
Example:   envs/dev/s3/S3-0001/terraform.tfstate
```

This prevents state collisions and reduces blast radius.

## 5. What Gets Created

### S3 Bucket

| Feature | Configuration |
|---------|---------------|
| Name | `goldenpath-{env}-{app}-{purpose}` |
| Encryption | SSE-S3 (dev/test) or SSE-KMS (staging/prod) |
| Versioning | Per request (default: enabled) |
| Public Access | Blocked by default |
| Access Logging | Required for staging/prod |
| Lifecycle | Per retention policy |

### CloudWatch Alarm

```text
Alarm Name: s3-cost-alert-{bucket-name}
Metric: BucketSizeBytes
Threshold: costAlertGb (converted to bytes)
```

### IAM Policy (Generated)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::goldenpath-dev-payments-api-uploads",
        "arn:aws:s3:::goldenpath-dev-payments-api-uploads/*"
      ]
    }
  ]
}
```

For SSE-KMS buckets, includes KMS permissions with encryption context.

### Catalog + Audit Trail

- **Catalog**: `docs/20-contracts/resource-catalogs/s3-catalog.yaml`
- **Audit CSV**: `governance/{environment}/s3_request_audit.csv`

## 6. Lifecycle: Purpose-Based Defaults

| Purpose | Typical Settings |
|---------|------------------|
| `logs` | Lifecycle enabled, versioning off, transition to Glacier |
| `uploads` | Versioning on, lifecycle optional |
| `backups` | Cross-region replication (V2), glacier transition |
| `data-lake` | Intelligent-tiering, no lifecycle |
| `static-assets` | Requires public access exception, CDN review |

## 7. Summary: The Value Loop

By abstracting S3 bucket complexity, the platform provides:

| Benefit | Description |
|---------|-------------|
| **Zero Bottlenecks** | Teams request buckets without waiting for platform |
| **100% Governance** | Every bucket is tagged with owner, purpose, and cost center |
| **Security by Default** | Encryption, public access block, logging auto-applied |
| **Cost Visibility** | CloudWatch alerts on storage thresholds |
| **Audit Trail** | Contracts provide full request history |
| **Environment Isolation** | Per-environment buckets with appropriate guardrails |

Audit records are appended to `governance/{environment}/s3_request_audit.csv` after successful apply.

## Related Documentation

- [ADR-0170: S3 Self-Service Request System](../../adrs/ADR-0170-s3-self-service-request-system.md)
- [S3 Catalog](../../20-contracts/resource-catalogs/s3-catalog.yaml)
- [RB-0035: S3 Request Operations](../../70-operations/runbooks/RB-0035-s3-request.md)
- [S3 Schema](../../../schemas/requests/s3.schema.yaml)
- [Contract-Driven Architecture](CONTRACT_DRIVEN_ARCHITECTURE.md)
