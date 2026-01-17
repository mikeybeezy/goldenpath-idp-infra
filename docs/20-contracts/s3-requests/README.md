---
id: s3-requests-index
title: S3 Bucket Requests
type: index
domain: platform-core
owner: platform-team
lifecycle: active
relates_to:
  - ADR-0170-s3-self-service-request-system
  - schemas/requests/s3.schema.yaml
  - SCRIPT-0037
  - CL-0146
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
5. **Catalog**: Bucket added to `resource-catalogs/s3-catalog.yaml`

## Contract Schema

All requests must follow the schema defined in `schemas/requests/s3.schema.yaml`.

### Required Fields

| Field | Description |
|-------|-------------|
| `id` | Unique ID (S3-XXXX format) |
| `environment` | Target environment |
| `bucket_name` | Following `goldenpath-{env}-{app}-{purpose}` convention |
| `purpose.type` | logs, uploads, backups, data-lake, static-assets |
| `purpose.description` | Human-readable explanation |
| `encryption.type` | sse-s3 or sse-kms |
| `retention_policy.type` | indefinite, time-bounded, compliance-driven |
| `retention_policy.rationale` | Explanation for retention choice |
| `cost_alert_gb` | CloudWatch alarm threshold |
| `tags.cost-center` | Cost allocation tag |
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
  bucket_name: goldenpath-dev-payments-api-uploads
  purpose:
    type: uploads
    description: "User-uploaded documents for payment verification"
  storage_class: standard
  encryption:
    type: sse-s3
  versioning: true
  public_access: blocked
  retention_policy:
    type: indefinite
    rationale: "User documents must be retained indefinitely for compliance"
  access_logging:
    enabled: false
  cost_alert_gb: 50
  cors_enabled: false
  tags:
    cost-center: payments
```

## Governance

- **ADR**: [ADR-0170](../../adrs/ADR-0170-s3-self-service-request-system.md)
- **Schema**: [s3.schema.yaml](../../../schemas/requests/s3.schema.yaml)
- **Parser**: SCRIPT-0037 (`scripts/s3_request_parser.py`)
- **Changelog**: [CL-0146](../../changelog/entries/CL-0146-s3-request-system.md)
