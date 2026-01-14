---
id: test-plan
title: 'Test Plan: ECR Catalog Generator'
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
status: active
category: platform
version: '1.0'
supported_until: '2028-01-01'
breaking_change: false
---

# Test Plan: ECR Catalog Generator

**Feature:** Risk-Based Security Controls Display
**Date:** 2026-01-05
**Tester:** Platform Team
**Status:** ✅ Passed

---

## Objective

Validate that `generate_catalog_docs.py` correctly displays risk-based security controls in the generated markdown documentation.

---

## What We're Testing

**Feature:** Catalog generator shows different security controls based on registry risk level

**Expected Behavior:**
- High-risk registries show: KMS encryption, IMMUTABLE tags, 50 image retention
- Medium-risk registries show: AES256 encryption, MUTABLE tags, 30 image retention
- Low-risk registries show: AES256 encryption, MUTABLE tags, 20 image retention

---

## Test Setup

### Prerequisites
- `scripts/generate_catalog_docs.py` updated with risk-based policy mapping
- `docs/20-contracts/catalogs/ecr-catalog.yaml` contains sample registries

### Test Data
Created 3 sample registries in `docs/20-contracts/catalogs/ecr-catalog.yaml`:
1. `wordpress-platform` (high risk)
2. `staging-api` (medium risk)
3. `test-app-dev` (low risk)

---

## Test Steps

1. **Update script** with risk-based policy mapping
2. **Add test data** to catalog (3 registries)
3. **Run script:**
   ```bash
   python scripts/generate_catalog_docs.py --verbose
   ```
4. **Verify output** in `docs/REGISTRY_CATALOG.md`

---

## Success Criteria

- ✅ Script runs without errors
- ✅ Generates `docs/REGISTRY_CATALOG.md`
- ✅ Shows 3 registries (1 high, 1 medium, 1 low)
- ✅ Each registry displays correct security controls
- ✅ Controls match risk level (KMS for high, AES256 for low/medium)
- ✅ Retention counts correct (50/30/20)
- ✅ Tag mutability correct (IMMUTABLE for high, MUTABLE for low/medium)

---

## Related Files

- Script: `scripts/generate_catalog_docs.py`
- Input: `docs/20-contracts/catalogs/ecr-catalog.yaml`
- Output: `docs/REGISTRY_CATALOG.md`
- Policy mapping: `modules/aws_ecr/locals.tf`
