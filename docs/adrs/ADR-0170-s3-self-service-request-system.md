---
id: ADR-0170
title: S3 Self-Service Request System
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0143-secret-request-contract
  - ADR-0144-intent-to-projection-parser
  - ADR-0168-eks-request-parser-and-mode-aware-workflows
  - ADR-0169-secret-request-system-generated-ids
  - EC-0002-shared-parser-library
  - CL-0146
  - SCRIPT-0037
supersedes: []
superseded_by: []
tags:
  - s3
  - self-service
  - governance
  - contracts
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 4.0
supported_until: '2028-01-01'
date: 2026-01-17
deciders:
  - platform-team
---

## Status

Accepted

## Context

S3 buckets are the third pillar of the core infrastructure trio (RDS, ECR, S3). Currently, bucket provisioning requires direct Terraform access or manual requests, creating inconsistent configurations and governance gaps.

The platform already has proven patterns for self-service infrastructure:
- **SecretRequest** (ADR-0143): Contract-driven secrets with risk tiers
- **EKSRequest** (ADR-0168): Namespace and workload provisioning
- **RDSRequest**: Database instance configuration

S3 needs the same contract-driven approach to maintain governance consistency while enabling developer self-service.

## Decision

Implement S3 self-service using the established contract → validation → apply pattern.

### Core Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bucket scope | **Per-environment** | Simpler IAM, cleaner teardown, environment isolation |
| KMS strategy | **Shared platform key (V1)** | Simplicity; per-domain keys can be added in V2 |
| Access logging | **Required staging/prod, optional dev** | Compliance without dev overhead |
| Lifecycle rules | **Optional with retention rationale** | Buckets are long-lived; capture intent, not arbitrary rules |
| Tier system | **No** - use purpose tags | Purpose (logs/uploads/backups/data-lake) is more meaningful |

### Contract Shape

```yaml
apiVersion: goldenpath.io/v1
kind: S3BucketRequest
id: S3-XXXX
metadata:
  owner: team-name
  environment: dev | test | staging | prod
  application: app-name
spec:
  bucket_name: goldenpath-{env}-{app}-{purpose}
  purpose:
    type: logs | uploads | backups | data-lake | static-assets
    description: "Human-readable explanation"
  storage_class: standard | intelligent-tiering | standard-ia | glacier
  encryption:
    type: sse-s3 | sse-kms
    kms_key_alias: alias/platform-s3  # Only if sse-kms
  versioning: true | false
  public_access: blocked | exception-approved
  retention_policy:
    type: indefinite | time-bounded | compliance-driven
    rationale: "Required explanation for retention choice"
  lifecycle:  # Optional - only if retention_policy.type != indefinite
    expire_days: 90
    transition_to_ia_days: 30
    transition_to_glacier_days: 60
  access_logging:
    enabled: true | false
    target_bucket: goldenpath-{env}-logs  # If enabled
  cost_alert_gb: 100  # CloudWatch alarm threshold
  cors_enabled: false  # Blocked by default
  tags:
    cost-center: team-cost-center
```

### Guardrails (V1)

| Guardrail | Environment | Default | Enforcement |
|-----------|-------------|---------|-------------|
| Public access | All | `blocked` | Schema + CI guard |
| Encryption | dev/test | `sse-s3` | Schema enum |
| Encryption | staging/prod | `sse-kms` | CI guard |
| Versioning | All | `true` | Schema default |
| Access logging | staging/prod | Required | CI guard |
| Access logging | dev/test | Optional | Schema |
| CORS | All | `false` | Schema default |
| Static website | All | Blocked | No field (future exception path) |
| Naming | All | `^goldenpath-[a-z]+-[a-z0-9-]+-[a-z0-9-]+$` | Schema regex |
| Cost alert | All | Required | Schema |

### Artifacts

| Artifact | Path | ID |
|----------|------|-----|
| Contract template | `docs/20-contracts/s3-requests/{env}/S3-XXXX.yaml` | — |
| Resource catalog | `docs/20-contracts/resource-catalogs/s3-catalog.yaml` | — |
| JSON Schema | `schemas/requests/s3.schema.yaml` | — |
| Parser | `scripts/s3_request_parser.py` | SCRIPT-0037 |
| Backstage template | `backstage-helm/backstage-catalog/templates/s3-request.yaml` | — |
| CI validation | `.github/workflows/ci-s3-request-validation.yml` | — |
| Apply workflow | `.github/workflows/s3-request-apply.yml` | — |
| How-it-works | `docs/85-how-it-works/self-service/S3_REQUEST_FLOW.md` | — |
| Changelog | `docs/changelog/entries/CL-0146-s3-request-system.md` | CL-0146 |

### Parser Outputs

The parser (SCRIPT-0037) generates:

1. **Terraform tfvars** for S3 module invocation
2. **IAM policy snippet** granting app role access to the bucket
3. **Audit record** for governance-registry

### Audit Trail

All S3 requests logged to `governance-registry`:

```csv
# environments/{env}/latest/s3_request_audit.csv
timestamp_utc,request_id,bucket_name,owner,environment,purpose,action,approver,status
```

### Not Included in V1

- Cross-region replication (add in V2 for prod DR)
- Per-domain KMS keys (add in V2)
- Static website hosting (requires separate exception flow)
- Bucket deletion workflow (manual for V1)
- Kyverno policies (deferred to EC-0005 Crossplane adoption)

## Consequences

### Positive

- **Consistency**: S3 follows same pattern as Secrets/EKS/RDS requests
- **Self-service**: Teams can request buckets without platform tickets
- **Governance**: All buckets tracked, audited, and policy-compliant
- **Security**: Public access blocked by default, encryption enforced
- **Cost visibility**: Mandatory cost-center tags and alert thresholds

### Negative

- **No bucket deletion**: V1 requires manual teardown (acceptable for long-lived buckets)
- **Shared KMS key**: Less isolation than per-domain keys (acceptable for V1)
- **CI-based validation**: Not as immediate as Kyverno admission control (deferred to EC-0005)

### Neutral

- Parser adds maintenance overhead (mitigated by EC-0002 shared library patterns)
- Backstage template requires sync with schema (standard practice)

## Alternatives Considered

### 1. Direct Terraform Access

Rejected: No governance, inconsistent configurations, audit gap.

### 2. Crossplane/ACK for S3

Deferred to EC-0005. Requires K8s operator framework adoption first.

### 3. Tier-based System (like Secrets)

Rejected: S3 buckets don't have inherent risk tiers. Purpose-based classification is more meaningful.

## Implementation Plan

| Phase | Deliverables |
|-------|-------------|
| 1 | Schema + Contract template + Catalog |
| 2 | Parser (SCRIPT-0037) + Tests |
| 3 | CI validation workflow |
| 4 | Terraform S3 module (if needed) |
| 5 | Apply workflow with approval gate |
| 6 | Backstage scaffolder template |
| 7 | Documentation (how-it-works, runbook) |

## References

- [ADR-0143: Secret Request Contract](ADR-0143-secret-request-contract.md)
- [ADR-0168: EKS Request Parser](ADR-0168-eks-request-parser-and-mode-aware-workflows.md)
- [EC-0002: Shared Parser Library](../extend-capabilities/EC-0002-shared-parser-library.md)
- [S3 Planning Session](../../session_capture/2026-01-17-s3-request-flow-planning.md)
