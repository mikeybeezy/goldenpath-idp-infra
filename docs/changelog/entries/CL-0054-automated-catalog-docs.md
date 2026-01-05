---
id: CL-0054-automated-catalog-docs
title: 'CL-0054: Automated Registry Catalog Documentation'
type: changelog
category: governance
version: '1.0'
owner: platform-team
status: active
dependencies:
  - python3
  - pyyaml
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-05
  breaking_change: false
relates_to:
  - ADR-0094
  - ADR-0092
  - CL-0054
---

# CL-0054: Automated Registry Catalog Documentation

**Date:** 2026-01-05
**Type:** Feature
**Category:** Governance
**Status:** Active

## Summary

Created automated script to generate human-readable markdown documentation from the YAML registry catalog.

## Changes

### New Files
- `scripts/generate_catalog_docs.py` - Catalog documentation generator
- `docs/adrs/ADR-0094-automated-catalog-docs.md` - Decision record

### Script Features

**Input:** `docs/registry-catalog.yaml` (machine-readable)
**Output:** `docs/REGISTRY_CATALOG.md` (human-readable)

**Generated Documentation Includes:**
- Summary statistics (total, active, deprecated, risk distribution)
- Registry inventory table (sortable, filterable)
- Detailed registry cards with:
  - Metadata (ID, owner, risk, status)
  - AWS details (region, URL, ARN)
  - Governance settings (scanning, encryption, lifecycle)
  - Image list with latest tags
  - Links to runbooks and ADRs
- Risk-based grouping (high/medium/low sections)

**Usage:**
```bash
python scripts/generate_catalog_docs.py [--catalog FILE] [--output FILE] [--verbose]
```

## Impact

### Platform Team
- Quick reference for all registries
- Easy to find registry details
- Auto-generated (no manual sync)

### Application Teams
- Discover available registries
- Understand registry configuration
- Find related documentation

## Implementation Status

- ✅ Script created
- ✅ ADR documented
- ⏳ GitHub Action automation (future)
- ⏳ Initial catalog YAML (pending)

## Next Steps

1. Create initial `docs/registry-catalog.yaml`
2. Run script to generate first catalog
3. Add GitHub Action to auto-generate on catalog changes
4. Test with existing registries

## Testing

- [ ] Script runs successfully
- [ ] Generated markdown is well-formatted
- [ ] All registry details included
- [ ] Links work correctly
- [ ] Risk grouping accurate

## Related
- [ADR-0094: Automated Catalog Documentation](../adrs/ADR-0094-automated-catalog-docs.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
- [Policy Governance README](../policies/README.md)
