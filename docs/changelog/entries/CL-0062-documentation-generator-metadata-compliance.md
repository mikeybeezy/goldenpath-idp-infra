<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0062-documentation-generator-metadata-compliance
title: Documentation Generator Metadata Compliance
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - CL-0062-documentation-generator-metadata-compliance
  - REGISTRY_CATALOG
  - standardized-image-delivery
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
breaking_change: false
---

# CL-0062: Documentation Generator Metadata Compliance

Resolved the "metadata limbo" issue where auto-generated Markdown files lacked platform frontmatter, making them invisible to governance and validation tools.

## Changes

### Script Updates

#### `generate_catalog_docs.py`
- **Added Frontmatter Injection**: The script now automatically injects complete platform metadata into generated catalog files
- **Self-Referencing**: Uses `Path(__file__).name` to dynamically include the script filename in `relates_to`
- **Generated Files**: `docs/REGISTRY_CATALOG.md` now includes:
  - Unique ID: `CAT_CONTAINER_REGISTRIES`
  - Full risk profile and lifecycle metadata
  - Traceability links to ADR-0097, ADR-0100, and the generator script

#### `platform_health.py`
- **Self-Referencing**: Uses `os.path.basename(__file__)` to dynamically include the script filename in `relates_to`
- **Generated Files**: `PLATFORM_HEALTH.md` now explicitly lists `platform_health.py` as its source

### Documentation Updates
- **[ADR-0100](../adrs/ADR-0100-standardized-ecr-lifecycle-and-documentation.md)**: Added sections 7 & 8 documenting the "Atomic Documentation Sync" and "Metadata Inheritance & Governance" principles
- **[Catalog README](../catalogs/README.md)**: Updated the workflow diagram to show when documentation synchronization occurs
- **[Standardized Image Delivery Guide](../guides/standardized-image-delivery.md)**: Created comprehensive guide for OIDC-based image delivery

## Impact

**Before:**
```markdown
# Container Registries Catalog    ← No metadata!

> Auto-generated from ecr-catalog.yaml
```

**After:**
```yaml
---
id: CAT_CONTAINER_REGISTRIES
title: Container Registries Catalog
type: documentation
category: catalogs
owner: platform-team
relates_to:
  - ADR-0097
  - ADR-0100
  - generate_catalog_docs.py    ← Traceable!
---
```

## Benefits
- ✅ All generated documentation is now tracked by `validate_metadata.py`
- ✅ Generated docs appear in `PLATFORM_HEALTH.md` compliance reports
- ✅ Complete audit trail from generated file → source script
- ✅ Self-referencing is maintenance-proof (survives script renames)

## Verification
```bash
# Verify catalog includes metadata
python3 scripts/generate_catalog_docs.py
head -n 25 docs/REGISTRY_CATALOG.md

# Verify health report includes self-reference
python3 scripts/platform_health.py
grep -A 2 "relates_to:" PLATFORM_HEALTH.md
```
