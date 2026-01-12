---
id: CL-0057-domain-based-catalogs
title: 'CL-0057: Domain-Based Resource Catalogs'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
version: '1.0'
dependencies:
  - terraform
  - github-actions
lifecycle: active
relates_to:
  - ADR-0097
  - ADR-0092
  - ADR-0094
supported_until: 2028-01-05
breaking_change: true
---

# CL-0057: Domain-Based Resource Catalogs

**Date:** 2026-01-05
**Type:** Refactor
**Category:** Architecture
**Status:** Active
**Breaking Change:** Yes

## Summary

Refactored from single platform-wide catalog to domain-based catalogs, where each resource type (ECR, RDS, S3) has its own YAML file for better scalability and ownership.

## Changes

### New Structure
```
docs/20-contracts/catalogs/
├── README.md              # Catalog index
├── ecr-catalog.yaml       # Container registries
├── rds-catalog.yaml       # Databases (future)
└── s3-catalog.yaml        # Storage (future)
```

### Created Files
- `docs/20-contracts/catalogs/README.md` - Index of all catalogs
- `docs/20-contracts/catalogs/ecr-catalog.yaml` - ECR registry catalog
- `docs/adrs/ADR-0097-domain-based-resource-catalogs.md` - Decision record

### Modified Files (Pending)
- `.github/workflows/create-ecr-registry.yml` - Update catalog path
- `scripts/generate_catalog_docs.py` - Update catalog path

### Removed Files (Pending)
- `docs/registry-catalog.yaml` - Replaced by `docs/20-contracts/catalogs/ecr-catalog.yaml`

## Rationale

**Why domain-based?**
- **Scalability:** Small focused files vs one huge file
- **Ownership:** Different teams own different catalogs
- **Blast radius:** Changes isolated to domain
- **Performance:** Terraform only reads needed catalog

## Migration Path

### Phase 1: Structure ✅
- [x] Create `docs/20-contracts/catalogs/` directory
- [x] Create `docs/20-contracts/catalogs/README.md` index
- [x] Create `docs/20-contracts/catalogs/ecr-catalog.yaml`

### Phase 2: Update References
- [ ] Update `.github/workflows/create-ecr-registry.yml`
- [ ] Update `scripts/generate_catalog_docs.py`
- [ ] Update runbooks

### Phase 3: Cleanup
- [ ] Remove old `docs/registry-catalog.yaml`
- [ ] Verify all references updated

## Impact

### Breaking Changes
- **Catalog path changed:** `docs/registry-catalog.yaml` → `docs/20-contracts/catalogs/ecr-catalog.yaml`
- **Workflows need update:** Self-service workflows must point to new path
- **Scripts need update:** Catalog generator must read new path

### Mitigation
- No production usage yet (safe to break)
- All changes in single PR
- Clear migration path documented

## Benefits

**Immediate:**
- Clear domain separation
- Better organization
- Future-proof structure

**Long-term:**
- Easy to add new resource types
- Team ownership per domain
- Reduced merge conflicts
- Better scalability

## Related
- [ADR-0097: Domain-Based Resource Catalogs](../adrs/ADR-0097-domain-based-resource-catalogs.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0094: Automated Catalog Documentation](../adrs/ADR-0094-automated-catalog-docs.md)
