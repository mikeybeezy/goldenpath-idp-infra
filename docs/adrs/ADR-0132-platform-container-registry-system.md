---
id: ADR-0132
title: 'ADR-0132: Model ECR Registry as a Dedicated Backstage System'
type: adr
status: accepted
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - ADR-0128
  - ADR-0129
  - CL-0092
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-09
version: 1.0
breaking_change: false
---

# ADR-0132: Model ECR Registry as a Dedicated Backstage System

- **Status:** Accepted
- **Date:** 2026-01-09
- **Owners:** `platform-team`
- **Decision type:** Architecture | Governance

---

## Context

The ECR registry powers build, publish, and deploy workflows across the platform
and creates downstream operational effects (promotion, rollbacks, and catalog
visibility). Today, the ECR registry is either tied to an unrelated system or
left without a clear system boundary, which weakens ownership and catalog
grouping in Backstage.

We need a durable, explicit system boundary to model registry ownership and
downstream effects, while keeping the catalog coherent as the registry workflow
expands.

## Decision

We will model ECR as a dedicated Backstage System named `container-registry`
under the `delivery` domain. ECR components and resources will reference this
system, and the catalog will include a matching `delivery` domain entity to
avoid missing relations.

## Scope

**Applies to:**
- Backstage catalog entities for ECR (System, Component, Resource).
- ECR catalog sync output (`backstage-helm/backstage-catalog/resources/ecr-registry.yaml`).

**Does not apply to:**
- AWS infrastructure configuration or Terraform modules.
- Runtime ECR policy or access controls.

## Consequences

### Positive
- Clear ownership boundary for registry capabilities.
- Improved catalog grouping for registry-related workflows.
- Scales as more registry automation (scanning, lifecycle, replication) lands.

### Tradeoffs / Risks
- Adds a new catalog entity to maintain.
- Requires explicit domain taxonomy alignment (`delivery` domain).

### Operational impact
- Add the `container-registry` system and `delivery` domain to the catalog.
- Update ECR component/resource references to the new system.
- Keep the sync script aligned with the system boundary.

## Alternatives considered

1. **Keep ECR under `audio-playback`** (rejected: incorrect ownership model).
2. **Keep ECR unassigned to a system** (rejected: weak catalog grouping).
3. **Model under `platform-core`** (rejected: delivery-specific ownership is
   clearer).

## Follow-ups

- Add `container-registry` system entity and `delivery` domain entity.
- Update `backstage-helm/backstage-catalog/components/ecr-registry.yaml`.
- Update `scripts/sync_ecr_catalog.py` output to use the new system.
- Document the sync process in a runbook.
