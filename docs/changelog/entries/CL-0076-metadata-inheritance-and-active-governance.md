---
id: CL-0076-metadata-inheritance-and-active-governance
title: 'CL-0076: Metadata Inheritance, Versioning, and Active Governance'
type: changelog
---

# CL-0076: Metadata Inheritance, Versioning, and Active Governance

## Goal
Implement a robust, versioned metadata engine that enables high-velocity onboarding while maintaining a continuous governance loop.

## Changes

### Core Engine
*   **MetadataConfig**: Upgraded with parent-lookup and inheritance merging logic.
*   **Contract Versioning**: Introduced `version` tracking in all schemas and enums.
*   **Schema Validator**: New capability to validate the integrity of governance schemas themselves.

### Governance Loop
*   **audit_metadata.py**: Created automated reaper for repo-wide compliance snapshots.
*   **Migration Framework**: Established `scripts/migrations/` for first-class schema evolution.

### Policy Updates
*   **[METADATA_INHERITANCE_STRATEGY.md](docs/10-governance/METADATA_INHERITANCE_STRATEGY.md)**: Formally defined the cascading control plane.
*   **[ADR-0120](docs/adrs/ADR-0120-metadata-inheritance-and-active-governance.md)**: Documented the architectural shift toward versioned, cascading governance.

## Verification
* CI gates updated to enforce inheritance-aware validation.
* Validated schema-to-schema integrity (no broken enum references).
