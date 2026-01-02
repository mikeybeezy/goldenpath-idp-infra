# CL-0021: Documentation Taxonomy Refactor

Date: 2026-01-02
Owner: platform
Scope: docs
Related: docs/adrs/ADR-0071-doc-taxonomy-refactor.md, PR #112

## Summary

Restructured the documentation layout to standardize where "Product", "Contracts", and "Lifecycle" documents live.

## Changes

### Added

- `docs/00-foundations/10_PLATFORM_REQUIREMENTS.md`: Placeholder for product requirements.
- `docs/20-contracts/01_PLATFORM_SERVICE_AGREEMENT.md`: Placeholder for SLAs.
- `docs/20-contracts/10_SERVICE_CATALOG.md`: Placeholder for service catalog.
- `docs/70-operations/01_LIFECYCLE_POLICY.md`: Placeholder for upgrade/deprecation policies.
- `docs/adrs/ADR-0071-doc-taxonomy-refactor.md`: Decision record for this change.

### Changed

- Renamed `docs/production-readiness-gates/V1_03_TODO.md` → `ROADMAP.md`.
- Renamed `docs/production-readiness-gates/V1_05_DUE_DILIGENCE_SCORECARD.md` → `READINESS_CHECKLIST.md`.
- Updated `docs/90-doc-system/00_DOC_INDEX.md` with new paths.

## Validation

- Verified via `scripts/check-doc-freshness.py`.
