---
id: CL-0146
title: S3 Self-Service Request System
type: changelog
status: planned
date: 2026-01-17
author: platform-team
category: feature
relates_to:
  - ADR-0170-s3-self-service-request-system
  - SCRIPT-0037
  - EC-0002-shared-parser-library
---

# CL-0146: S3 Self-Service Request System

## Summary

Introduces contract-driven S3 bucket provisioning via Backstage, completing the
core infrastructure trio (RDS, ECR, S3). Teams can request buckets through a
self-service flow with built-in guardrails for security, encryption, and cost.

## Changes

### Added

- Contract schema: `schemas/requests/s3.schema.yaml`
- Contract template: `docs/20-contracts/s3-requests/{env}/S3-XXXX.yaml`
- Resource catalog: `docs/20-contracts/resource-catalogs/s3-catalog.yaml`
- Parser: `scripts/s3_request_parser.py` (SCRIPT-0037)
- CI validation: `.github/workflows/ci-s3-request-validation.yml`
- Apply workflow: `.github/workflows/s3-request-apply.yml`
- Backstage template: `backstage-helm/backstage-catalog/templates/s3-request.yaml`
- How-it-works: `docs/85-how-it-works/self-service/S3_REQUEST_FLOW.md`
- ADR: `docs/adrs/ADR-0170-s3-self-service-request-system.md`

## Key Decisions

| Decision | Choice |
|----------|--------|
| Bucket scope | Per-environment (simpler IAM, cleaner teardown) |
| KMS strategy | Shared platform key (V1) |
| Access logging | Required staging/prod, optional dev |
| Lifecycle rules | Optional with retention rationale |
| Tier system | None - use purpose tags instead |

## Guardrails

- Public access blocked by default
- SSE-KMS required in staging/prod
- Versioning enabled by default
- Cost alert threshold required
- Naming convention enforced: `goldenpath-{env}-{app}-{purpose}`

## Purpose Tags

Instead of abstract tiers, buckets are classified by purpose:
- `logs` - Application/audit logs
- `uploads` - User file uploads
- `backups` - Database/config backups
- `data-lake` - Analytics data
- `static-assets` - CDN/website assets (requires exception)

## Notes

- Bucket deletion remains manual in V1
- Cross-region replication deferred to V2
- Kyverno policies deferred to EC-0005 adoption
