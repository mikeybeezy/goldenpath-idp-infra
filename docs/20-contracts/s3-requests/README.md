<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: s3-requests-index
title: S3 Bucket Requests
type: documentation
relates_to:
  - ADR-0170
  - CL-0146
  - SCRIPT-0037
  - session-2026-01-17-s3-request-flow-planning
---

# S3 Bucket Requests

This directory contains S3 bucket request contracts organized by environment.

## Directory Structure

```
s3-requests/
├── README.md           # This file
├── dev/                # Development environment requests
│   └── S3-XXXX.yaml
├── staging/            # Staging environment requests
│   └── S3-XXXX.yaml
└── prod/               # Production environment requests
    └── S3-XXXX.yaml
```

## Request Flow

1. **Request**: Team submits via Backstage template or creates YAML manually
2. **Validate**: CI validates against `schemas/requests/s3.schema.yaml`
3. **Review**: PR requires platform-approval for prod/public access
4. **Apply**: Approved PRs trigger `s3-request-apply.yml` workflow
5. **Catalog + Audit**: Bucket added to `resource-catalogs/s3-catalog.yaml` and audit record appended

## Contract Schema

All requests must follow the schema defined in `schemas/requests/s3.schema.yaml`.

### Required Fields

| Field | Description |
|-------|-------------|
| `id` | Unique ID (S3-XXXX format) |
| `environment` | Target environment |
| `bucketName` | Following `goldenpath-{env}-{app}-{purpose}` convention |
| `purpose.type` | logs, uploads, backups, data-lake, static-assets |
| `purpose.description` | Human-readable explanation |
| `encryption.type` | sse-s3 or sse-kms |
| `retentionPolicy.type` | indefinite, time-bounded, compliance-driven |
| `retentionPolicy.rationale` | Explanation for retention choice |
| `costAlertGb` | CloudWatch alarm threshold |
| `tags.costCenter` | Cost allocation tag |
| `owner` | Owning team |
| `application` | Application name |
| `requester` | Requester name |

## Guardrails

| Environment | Encryption | Access Logging | Public Access |
|-------------|------------|----------------|---------------|
| dev/test | SSE-S3 (default) | Optional | Blocked |
| staging | SSE-KMS required | Required | Blocked |
| prod | SSE-KMS required | Required | Blocked (exception path available) |

## Purpose Tags

| Purpose | Typical Use | Defaults |
|---------|-------------|----------|
| `logs` | Application/audit logs | Lifecycle enabled, versioning off |
| `uploads` | User file uploads | Versioning on |
| `backups` | Database/config backups | Glacier transition |
| `data-lake` | Analytics data | Intelligent-tiering |
| `static-assets` | CDN content | Requires platform review |

## Example Request

```yaml
# S3-0001.yaml
apiVersion: goldenpath.io/v1
kind: S3BucketRequest
id: S3-0001
environment: dev
owner: payments-team
application: payments-api
requester: payments-team

metadata:
  title: "Payments API Uploads"
  description: "User document uploads for payments processing"
  created: "2026-01-17"

spec:
  bucketName: goldenpath-dev-payments-api-uploads
  purpose:
    type: uploads
    description: "User-uploaded documents for payment verification"
  storageClass: standard
  encryption:
    type: sse-s3
  versioning: true
  publicAccess: blocked
  retentionPolicy:
    type: indefinite
    rationale: "User documents must be retained indefinitely for compliance"
  accessLogging:
    enabled: false
  costAlertGb: 50
  corsEnabled: false
  tags:
    costCenter: payments
```

## Governance

- **ADR**: [ADR-0170](../../adrs/ADR-0170-s3-self-service-request-system.md)
- **Catalog**: [S3 Catalog](../resource-catalogs/s3-catalog.yaml)
- **Audit Trail**: `governance/{environment}/s3_request_audit.csv`
- **Schema**: [s3.schema.yaml](../../../schemas/requests/s3.schema.yaml)
- **Parser**: SCRIPT-0037 (`scripts/s3_request_parser.py`)
- **Changelog**: [CL-0146](../../changelog/entries/CL-0146-s3-request-system.md)
