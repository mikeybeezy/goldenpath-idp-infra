---
id: CL-0076-metadata-inheritance-active-governance-and-leak-protection
title: 'CL-0076: Metadata Inheritance, Active Governance, and Leak Protection'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0134-metadata-inheritance-active-governance-and-leak-protection
  - CL-0076-metadata-inheritance-active-governance-and-leak-protection
  - CL-0076-metadata-inheritance-and-active-governance
  - METADATA_INHERITANCE_STRATEGY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---

## CL-0076: Metadata Inheritance, Active Governance, and Leak Protection

## Goal

Implement a robust, versioned, and cascading metadata engine that enables high-velocity onboarding while maintaining a continuous governance loop and production safety.

## Changes

### Core Engine

* **MetadataConfig**: Upgraded with parent-lookup, inheritance merging, and redundant field pruning logic.
* **Safety Valve**: Introduced `exempt: true` support in schemas to bypass governance for scratchpads.
* **Leak Protection**: Implemented strict PR blocks to prevent `exempt` assets from reaching `envs/prod`.

### Governance Loop

* **audit_metadata.py**: Created automated reaper for repo-wide compliance snapshots.
* **Governance Vocabulary**: Auto-generated human-readable dictionary from `enums.yaml`.
* **Standardizer**: Refactored to merge local data with parent context and prune redundant sidecar entries.

### Developer Experience (DX)

* **bin/governance**: Created a lightweight local helper for `check`, `heal`, and `vocab` commands.

### Policy Updates

* **[METADATA_INHERITANCE_STRATEGY.md](../../10-governance/METADATA_INHERITANCE_STRATEGY.md)**: Formally defined the cascading control plane and "Zero-Touch" loops.
* **[ADR-0134](../../adrs/ADR-0134-metadata-inheritance-active-governance-and-leak-protection.md)**: Documented the architectural shift toward versioned, cascading governance with leak protection.

## Verification

* **Unit Tests**: Verified cascading logic (parent-lookup, overrides, identity-stripping) in `tests/unit/test_metadata_inheritance.py`.
* **Manual Verification**: Confirmed `bin/governance check` works locally.
* **Leak Protection**: Verified that `exempt: true` triggers a block if filepath contains `/prod/`.

```text
