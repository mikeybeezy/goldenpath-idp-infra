---
id: CL-0076-metadata-inheritance-active-governance-and-leak-protection
title: 'CL-0076: Metadata Inheritance, Active Governance, and Leak Protection'
type: changelog
---

# CL-0076: Metadata Inheritance, Active Governance, and Leak Protection

## Goal
Implement a robust, versioned, and cascading metadata engine that enables high-velocity onboarding while maintaining a continuous governance loop and production safety.

## Changes

### Core Engine
*   **MetadataConfig**: Upgraded with parent-lookup, inheritance merging, and redundant field pruning logic.
*   **Safety Valve**: Introduced `exempt: true` support in schemas to bypass governance for scratchpads.
*   **Leak Protection**: Implemented strict PR blocks to prevent `exempt` assets from reaching `envs/prod`.

### Governance Loop
*   **audit_metadata.py**: Created automated reaper for repo-wide compliance snapshots.
*   **Governance Vocabulary**: Auto-generated human-readable dictionary from `enums.yaml`.
*   **Standardizer**: Refactored to merge local data with parent context and prune redundant sidecar entries.

### Developer Experience (DX)
*   **bin/governance**: Created a lightweight local helper for `check`, `heal`, and `vocab` commands.

### Policy Updates
*   **[METADATA_INHERITANCE_STRATEGY.md](file:///Users/mikesablaze/goldenpath-idp-infra/docs/10-governance/METADATA_INHERITANCE_STRATEGY.md)**: Formally defined the cascading control plane and "Zero-Touch" loops.
*   **[ADR-0120](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0120-metadata-inheritance-active-governance-and-leak-protection.md)**: Documented the architectural shift toward versioned, cascading governance with leak protection.

## Verification
* **Unit Tests**: Verified cascading logic (parent-lookup, overrides, identity-stripping) in `tests/unit/test_metadata_inheritance.py`.
* **Manual Verification**: Confirmed `bin/governance check` works locally.
* **Leak Protection**: Verified that `exempt: true` triggers a block if filepath contains `/prod/`.
```
