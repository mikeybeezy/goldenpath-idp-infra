---
id: ADR-0083-platform-metadata-backfill-protocol
title: Metadata Backfill Campaign Protocol
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0082
  - ADR-0083
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

## ADR-0083: Metadata Backfill Campaign Protocol

Date: 2026-01-03
Status: Proposed
Owners: platform

## Context

We are adopting a metadata strategy that enables traceability and automated
governance. The validator currently enforces metadata on a subset of docs, and
Terraform tags are not yet validated automatically. We need a deterministic,
auditable protocol for backfilling metadata without introducing risk or noise.

## Decision

Adopt a single runbook-driven campaign with these rules:

1. A deterministic backfill runbook governs the process.
2. Changes are batched and committed in small increments.
3. Audit artifacts are retained for each batch.
4. Terraform tags are updated with safe merges only.
5. Source-code headers are deferred until validation exists.

## Consequences

**Positive**

- Consistent backfill process with clear rollback.
- Reduced friction for future metadata enforcement.
- Better provenance for AI-assisted governance.

**Negative**

- Some metadata gaps will remain until code-header validation is added.
- Requires operator discipline to maintain audit notes.
