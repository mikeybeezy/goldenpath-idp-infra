<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0130
title: 'ADR-0130: Zoned Defense for Catalog Ingestion Security'
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0129
  - ADR-0130
  - CL-0086-catalog-security-modernization
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-08
version: 1.0
breaking_change: true
---

## ADR-0130: Zoned Defense for Catalog Ingestion Security

- **Status:** Accepted
- **Date:** 2026-01-08
- **Owners:** `platform-team`
- **Decision type:** Security | Governance

---

## Context

The previous catalog configuration allowed any registered location (even user-contributed ones) to define security-sensitive entities like `Domain`, `Group`, and `User`. This created a "Shadow IT" risk where external repositories could shadow or hijack organizational hierarchy.

## Decision

We will implement a **"Zoned Defense"** model for catalog ingestion.

1. **Global Sandbox (Least Privilege)**: The global `catalog.rules` will only allow low-risk entities (`Component`, `API`).
2. **Trusted Zones**: Full permissions (`Domain`, `Group`, `User`, `System`, `Resource`) will be granted *only* to verified infrastructure repositories within their specific `locations` block.

## Consequences

### Positive

- **Integrity**: Prevents unauthorized users from defining groups or domains.
- **Security**: Hardens the portal against malicious data injection from external locations.

### Tradeoffs / Risks

- **Complexity**: Configuration is split between global rules and per-location rules.
- **Strictness**: Developers cannot test new Domains or Groups in their own repositories; they must be added to the official platform repository.

---

## Follow-ups

- [ ] Refactor `values-local.yaml` to move permissive rules inside the GoldenPath location block.
