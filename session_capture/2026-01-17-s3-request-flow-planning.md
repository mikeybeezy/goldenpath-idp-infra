---
id: session-2026-01-17-s3-request-flow-planning
title: S3 Request Flow Planning
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: in_progress
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - session_capture_template
---
# S3 Request Flow Planning

## Session metadata

**Agent:** Codex
**Date:** 2026-01-17
**Timestamp:** 2026-01-17T22:25:26Z
**Branch:** feature/infra-apply-rds-provision

## Scope

- Plan S3 request flow to complete the RDS/ECR/S3 core trio.
- Define guardrails, schema, and workflow approach for S3 requests.
- Capture naming conventions for contracts and scripts.

## Work Summary

- Proposed S3 request flow (contract + catalog + schema + parser + workflows + Backstage).
- Identified initial guardrails for security and cost.
- Recorded naming conventions: contracts use CamelCase; Python uses snake_case.

## Artifacts Touched (links)

### Referenced / Executed

- `session_capture/session_capture_template.md`

## Validation

- Not run (planning only).

## Current State / Follow-ups

- Awaiting decisions on S3 bucket scope (per-env vs global), encryption defaults, and required access logging/versioning.

Signed: Codex (2026-01-17T22:25:26Z)

---

## Updates (append as you go)

### Update - 2026-01-17T22:26:58Z

**Proposal: S3 Request Flow (V1)**

**Artifacts**
- Contract: `docs/20-contracts/s3-requests/<env>/S3-0001.yaml`
- Catalog: `docs/20-contracts/resource-catalogs/s3-catalog.yaml`
- Schema: `schemas/requests/s3.schema.yaml`
- Parser: `scripts/s3_request_parser.py`
- Backstage template: `backstage-helm/backstage-catalog/templates/s3-request.yaml`
- CI validation: `.github/workflows/ci-s3-request-validation.yml`
- Apply workflow: `.github/workflows/s3-request-apply.yml`
- How-it-works: `docs/85-how-it-works/self-service/S3_REQUEST_FLOW.md`

**Guardrails (V1 defaults)**
- Block public access by default; exceptions require platform approval label.
- Default encryption: SSE-S3 in dev/test; SSE-KMS required in staging/prod.
- Versioning enabled by default for all buckets.
- Lifecycle rules required for non-dev (e.g., expire objects after N days).
- Naming: `<org>-<env>-<app>-<purpose>` (validated in schema).

**Enums (new or extended)**
- `s3_environments`: `dev`, `test`, `staging`, `prod`
- `s3_storage_class`: `standard`, `intelligent-tiering`, `standard-ia`, `glacier`
- `s3_encryption`: `sse-s3`, `sse-kms`
- `s3_access`: `private`, `org-shared`, `public-exception`

**Open decisions**
- Bucket scope: per-env buckets vs global bucket with env prefixes.
- Access logs required in all envs vs non-dev only.
- KMS key strategy: shared platform key vs per-domain key.

Signed: Codex (2026-01-17T22:26:58Z)

### Review Feedback (Claude Opus 4.5 — 2026-01-17T19:45:00Z)

#### What Works Well

| Aspect | Status | Notes |
|--------|--------|-------|
| Follows established patterns | ✅ | Mirrors EKS/RDS/Secret request flows |
| Complete artifact list | ✅ | Contract, catalog, schema, parser, Backstage, workflows all identified |
| Security-first defaults | ✅ | Block public access, encryption, versioning |
| Naming convention | ✅ | `<org>-<env>-<app>-<purpose>` is clear and enforceable |
| Guardrails scoped by env | ✅ | Different encryption for dev vs prod is sensible |

#### Issues and Gaps

| Issue | Priority | Recommendation |
|-------|----------|----------------|
| Missing script ID | P1 | Assign SCRIPT-0037 (next after eks_request_parser SCRIPT-0036) |
| No ADR reference | P1 | Plan for ADR-0170 or similar to document S3 self-service decision |
| Bucket scope undecided | P2 | Recommend **per-env buckets** for isolation and simpler teardown |
| KMS key strategy unclear | P2 | Recommend **shared platform key** for V1, per-domain for V2 |
| No cost guardrail | P2 | Add storage quota or alert threshold for runaway costs |
| Missing relates_to entries | P3 | Add `ADR-0002` (Kong/ingress), `EC-0002` (shared parser) if relevant |
| No changelog entry planned | P3 | Reserve CL-0146 for S3 request system |

#### Recommendations

| Priority | Action | Effort |
|----------|--------|--------|
| P1 | Reserve SCRIPT-0037, ADR-0170, CL-0146 | Low |
| P1 | Decide on bucket scope (recommend per-env) | Decision |
| P2 | Add cost guardrail: max storage tier or alert | Medium |
| P2 | Define KMS strategy: shared platform key for V1 | Decision |
| P2 | Add access log requirement (non-dev minimum) | Low |
| P3 | Consider reusing shared parser library (EC-0002) patterns | Medium |

#### Open Questions - Suggested Answers

| Question | Recommendation | Rationale |
|----------|---------------|-----------|
| Bucket scope | Per-env buckets | Simpler IAM, cleaner teardown, env isolation |
| Access logs | Required in staging/prod, optional in dev | Compliance without dev overhead |
| KMS key strategy | Shared platform key (V1) | Simplicity; can add per-domain keys later |

#### Contract Example (Suggested Shape)

```yaml
# docs/20-contracts/s3-requests/dev/S3-0001.yaml
apiVersion: goldenpath.io/v1
kind: S3BucketRequest
id: S3-0001
metadata:
  owner: payments-team
  environment: dev
  application: payments-api
spec:
  bucket_name: goldenpath-dev-payments-api-uploads
  purpose: User file uploads
  storage_class: standard
  encryption: sse-s3
  versioning: true
  public_access: blocked  # or: exception-approved
  lifecycle:
    expire_days: 90
  access_logging: false  # optional in dev
  tags:
    cost-center: payments
```

#### Next Steps

1. Decide on bucket scope and KMS strategy
2. Reserve SCRIPT-0037, ADR-0170, CL-0146
3. Create `schemas/requests/s3.schema.yaml` based on contract shape
4. Implement parser following `eks_request_parser.py` pattern
5. Add Backstage scaffolder template

**Overall Assessment**: Solid planning document. Follows established patterns well. Main gaps are artifact ID reservations and a few pending architectural decisions. Ready to proceed once bucket scope and KMS strategy are decided.

Signed: Claude Opus 4.5 (claude-opus-4-5-20251101) — 2026-01-17T19:45:00Z

### Update - 2026-01-17T23:45:00Z

**Decisions Finalized**

All open decisions resolved and documented in ADR-0170:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bucket scope | **Per-environment** | Simpler IAM, cleaner teardown, env isolation |
| KMS strategy | **Shared platform key (V1)** | Simplicity; per-domain keys in V2 |
| Access logging | **Required staging/prod, optional dev** | Compliance without dev overhead |
| Lifecycle rules | **Optional with retention rationale** | Buckets are long-lived; capture intent |
| Tier system | **None - use purpose tags** | Purpose (logs/uploads/backups/data-lake) more meaningful |

**Artifacts Created**

- ADR: `docs/adrs/ADR-0170-s3-self-service-request-system.md`
- Changelog: `docs/changelog/entries/CL-0146-s3-request-system.md`

**Reserved IDs**

| Type | ID | Purpose |
|------|-----|---------|
| Script | SCRIPT-0037 | `s3_request_parser.py` |
| ADR | ADR-0170 | S3 self-service decision |
| Changelog | CL-0146 | S3 request system |

**Implementation Matrix**

| Phase | Task | Artifact | Status |
|-------|------|----------|--------|
| 1 | Create JSON schema | `schemas/requests/s3.schema.yaml` | ⏳ Pending |
| 1 | Create contract template | `docs/20-contracts/s3-requests/{env}/` | ⏳ Pending |
| 1 | Create resource catalog | `docs/20-contracts/resource-catalogs/s3-catalog.yaml` | ⏳ Pending |
| 2 | Implement parser | `scripts/s3_request_parser.py` (SCRIPT-0037) | ⏳ Pending |
| 2 | Add parser tests | `tests/scripts/test_script_0037.py` | ⏳ Pending |
| 3 | CI validation workflow | `.github/workflows/ci-s3-request-validation.yml` | ⏳ Pending |
| 4 | Terraform S3 module | `modules/aws_s3/` (if needed) | ⏳ Pending |
| 5 | Apply workflow | `.github/workflows/s3-request-apply.yml` | ⏳ Pending |
| 5 | Approval guard | `.github/workflows/s3-approval-guard.yml` | ⏳ Pending |
| 6 | Backstage template | `backstage-helm/backstage-catalog/templates/s3-request.yaml` | ⏳ Pending |
| 7 | How-it-works doc | `docs/85-how-it-works/self-service/S3_REQUEST_FLOW.md` | ⏳ Pending |
| 7 | Runbook | `docs/70-operations/runbooks/RB-0032-s3-request.md` | ⏳ Pending |

**Guardrails Summary**

| Guardrail | Environment | Enforcement |
|-----------|-------------|-------------|
| Public access blocked | All | Schema + CI guard |
| SSE-S3 encryption | dev/test | Schema default |
| SSE-KMS encryption | staging/prod | CI guard |
| Versioning enabled | All | Schema default |
| Access logging required | staging/prod | CI guard |
| Cost alert threshold | All | Schema required field |
| Naming convention | All | Schema regex |

**Purpose Tags (replaces tier system)**

| Purpose | Typical Settings |
|---------|------------------|
| `logs` | Lifecycle enabled, versioning off |
| `uploads` | Versioning on, lifecycle optional |
| `backups` | Cross-region replication (V2), glacier transition |
| `data-lake` | Intelligent-tiering, no lifecycle |
| `static-assets` | Requires public access exception path |

**Next Steps**

Ready to begin Phase 1 implementation:
1. Create `schemas/requests/s3.schema.yaml`
2. Create contract directory structure
3. Create resource catalog

Signed: Claude Opus 4.5 (claude-opus-4-5-20251101) — 2026-01-17T23:45:00Z

### Update - 2026-01-18T00:15:00Z

**Phase 1 Complete**

All Phase 1 artifacts created and pushed to `feature/s3-request-flow-planning`:

| Artifact | Path | Status |
|----------|------|--------|
| JSON Schema | `schemas/requests/s3.schema.yaml` | ✅ Created |
| Contract README | `docs/20-contracts/s3-requests/README.md` | ✅ Created |
| Contract directories | `docs/20-contracts/s3-requests/{dev,staging,prod}/` | ✅ Created |
| Example contract | `docs/20-contracts/s3-requests/dev/S3-0001.yaml` | ✅ Created |
| Resource catalog | `docs/20-contracts/resource-catalogs/s3-catalog.yaml` | ✅ Updated |

**Schema Highlights**

- Purpose-based classification: logs, uploads, backups, data-lake, static-assets
- Retention policy with rationale capture (not forced lifecycle rules)
- Environment-specific conditional rules for encryption and logging
- Cost alert threshold as required field
- Approval routing based on environment and public access settings

**Updated Implementation Matrix**

| Phase | Task | Artifact | Status |
|-------|------|----------|--------|
| 1 | Create JSON schema | `schemas/requests/s3.schema.yaml` | ✅ Complete |
| 1 | Create contract template | `docs/20-contracts/s3-requests/{env}/` | ✅ Complete |
| 1 | Create resource catalog | `docs/20-contracts/resource-catalogs/s3-catalog.yaml` | ✅ Complete |
| 2 | Implement parser | `scripts/s3_request_parser.py` (SCRIPT-0037) | ⏳ Pending |
| 2 | Add parser tests | `tests/scripts/test_script_0037.py` | ⏳ Pending |
| 3 | CI validation workflow | `.github/workflows/ci-s3-request-validation.yml` | ⏳ Pending |
| 4 | Terraform S3 module | `modules/aws_s3/` (if needed) | ⏳ Pending |
| 5 | Apply workflow | `.github/workflows/s3-request-apply.yml` | ⏳ Pending |
| 5 | Approval guard | `.github/workflows/s3-approval-guard.yml` | ⏳ Pending |
| 6 | Backstage template | `backstage-helm/backstage-catalog/templates/s3-request.yaml` | ⏳ Pending |
| 7 | How-it-works doc | `docs/85-how-it-works/self-service/S3_REQUEST_FLOW.md` | ⏳ Pending |
| 7 | Runbook | `docs/70-operations/runbooks/RB-0032-s3-request.md` | ⏳ Pending |

**Next Steps**

Ready for Phase 2: Parser implementation (SCRIPT-0037).

Signed: Claude Opus 4.5 (claude-opus-4-5-20251101) — 2026-01-18T00:15:00Z
