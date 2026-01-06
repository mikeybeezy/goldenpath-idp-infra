---
id: ADR-0071
title: 'ADR-0071: Standardized Documentation Taxonomy'
type: adr
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
  - ADR-0071
---

# ADR-0071: Standardized Documentation Taxonomy

## Status

Accepted

## Context

The documentation structure has grown organically, leading to scattered "product-like" definitions (Requirements, Catalog, SLAs) and ambiguous homes for operational policies (Upgrade/Deprecation rules).

New files were introduced without a clear home:

- `production-readiness-gates/ROADMAP.md` (formerly `V1_03_TODO.md`)
- `production-readiness-gates/READINESS_CHECKLIST.md` (formerly `V1_05_DUE_DILIGENCE_SCORECARD.md`)

We need a standardized taxonomy to ensure every document has a predictable, discoverable location that aligns with the "Dewey Decimal" system (e.g., `20-contracts`, `70-operations`).

## Decision

We will restructure the documentation as follows:

1. **Foundations (`00-foundations`)**: Hosts high-level Product Requirements.
2. **Contracts (`20-contracts`)**: Hosts Service Agreements (SLAs) and Service Catalogs.
3. **Operations (`70-operations`)**: Hosts Lifecycle Policies (Upgrades/Deprecation).
4. **Readiness (`production-readiness-gates`)**: Renamed to clearer filenames (`ROADMAP.md`, `READINESS_CHECKLIST.md`) but kept as a distinct folder for visibility.

We will strictly enforce this taxonomy via `DOC_INDEX.md`.

## Consequences

- **Positive:** clearer navigation for users; less "folder sprawl" at the root level.
- **Negative:** Existing links might break (though we are fixing `DOC_INDEX.md` immediately).
