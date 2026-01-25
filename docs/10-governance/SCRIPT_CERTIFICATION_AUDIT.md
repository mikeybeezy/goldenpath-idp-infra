---
id: SCRIPT_CERTIFICATION_AUDIT
title: Platform Scripts Certification Audit Matrix
type: governance
relates_to:
  - ADR-0084-platform-enhanced-metadata-schema
  - ADR-0088-automated-metadata-remediation
  - ADR-0094-automated-catalog-docs
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - ADR-0102
  - ADR-0103-automated-workflow-docs
  - ADR-0126
  - ADR-0143
  - ADR-0145
  - CONFIDENCE_MATRIX
  - SCRIPT_CERTIFICATION_MATRIX
date: 2026-01-12
---

# Platform Scripts Certification Audit Matrix

**Purpose:** Track certification progress of all platform automation scripts
**Target:** Achieve ⭐⭐⭐ (Validated) or higher for all scripts
**Audit Date:** 2026-01-12

---

## 📊 Audit Summary

**Live Status Dashboard**: See [SCRIPT_CERTIFICATION_MATRIX.md](./SCRIPT_CERTIFICATION_MATRIX.md) for the automated, real-time certification status of all scripts.

**Migration Progress (Manual Tracker):**
**Total Scripts:** 43
**Certified (⭐⭐⭐):** 1 (Standardize Metadata)
**Validated (⭐⭐):** 42 (Backfilled)

**Target Completion:** 2026-02-15 (5 weeks)

---

## 🎯 Certification Matrix

| # | Script | Unit Test | Dry-Run | ADR Link | VQ | Stars | Priority | Owner |
|---|--------|-----------|---------|----------|----|----|----------|-------|
| 1 | validate_metadata.py | ✅ |  | ADR-0084 | 🔴 HV/HQ | ⭐⭐ | P0 | platform-team |
| 2 | secret_request_parser.py | ✅ |  | ADR-0143 | 🔴 HV/HQ | ⭐⭐ | P0 | platform-team |
| 3 | vq_logger.py | ✅ | N/A | ADR-0126 | 🟢 LV/HQ | ⭐⭐⭐ | ✅ DONE | platform-team |
| 4 | metadata_config.py | ✅ | N/A | ADR-0084 | 🟢 LV/HQ | ⭐⭐⭐ | ✅ DONE | platform-team |
| 5 | backfill_metadata.py |  | ✅ | ADR-0088 | 🟡 HV/MQ | ⭐⭐ | P1 | platform-team |
| 6 | extract_relationships.py |  | ✅ | ADR-0084 | 🟡 MV/MQ | ⭐⭐ | P2 | platform-team |
| 7 | platform_health.py |  |  | ADR-0145 | 🔴 HV/HQ | ⭐⭐ | P0 | platform-team |
| 8 | standardize_metadata.py | ✅ | ✅ | ADR-0088 | 🔴 HV/HQ | ⭐⭐⭐ | P0 | platform-team |
| 9 | pr_guardrails.py |  |  | ADR-0102 | 🔴 HV/HQ | ⭐⭐ | P0 | platform-team |
| 10 | validate_govreg.py |  | N/A | ADR-0145 | 🔴 HV/HQ | ⭐⭐ | P1 | platform-team |
| 11 | aws_inventory.py |  |  | - | 🟡 MV/MQ | ⭐ | P2 | platform-team |
| 12 | sync_ecr_catalog.py |  | ✅ | ADR-0097 | 🟡 MV/MQ | ⭐⭐ | P2 | platform-team |
| 13 | sync_backstage_entities.py |  |  | ADR-0094 | 🟡 MV/MQ | ⭐ | P2 | platform-team |
| 14 | generate_adr_index.py |  | N/A | ADR-0103 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 15 | generate_backstage_docs.py |  | N/A | ADR-0094 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 16 | generate_catalog_docs.py |  | N/A | ADR-0097 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 17 | generate_governance_vocab.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 18 | generate_script_index.py |  | N/A | ADR-0103 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 19 | generate_workflow_index.py |  | N/A | ADR-0103 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 20 | validate_enums.py |  | N/A | - | 🟢 LV/HQ | ⭐ | P2 | platform-team |
| 21 | validate_routing_compliance.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 22 | check_compliance.py |  | N/A | ADR-0084 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 23 | check_doc_freshness.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 24 | check_doc_index_contract.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 25 | check_script_traceability.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 26 | audit_metadata.py |  |  | ADR-0084 | 🟡 MV/MQ | ⭐ | P2 | platform-team |
| 27 | enforce_emoji_policy.py |  | ✅ | - | 🟢 LV/LQ | ⭐ | P3 | platform-team |
| 28 | scaffold_doc.py |  |  | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 29 | scaffold_ecr.py |  | ✅ | ADR-0100 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 30 | scaffold_test.py |  |  | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 31 | render_template.py |  |  | - | 🟢 LV/LQ | ⭐ | P3 | platform-team |
| 32 | fix_yaml_syntax.py |  |  | - | 🟢 LV/LQ | ⭐ | P3 | platform-team |
| 33 | format_docs.py |  |  | - | 🟢 LV/LQ | ⭐ | P3 | platform-team |
| 34 | migrate_partial_metadata.py |  |  | ADR-0084 | 🟡 MV/MQ | ⭐ | P2 | platform-team |
| 35 | test_hotfix.py |  | N/A | - | 🟢 LV/LQ | ⭐ | P3 | platform-team |
| 36 | test_platform_health.py |  | N/A | - | 🟢 LV/LQ | ⭐ | P3 | platform-team |
| 37 | generate_backstage_ecr.py |  | N/A | ADR-0094 | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 38 | generate_doc_system_map.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 39 | check-policy-compliance.py |  | N/A | - | 🟢 LV/MQ | ⭐ | P3 | platform-team |
| 40 | cost_logger.py |  | N/A | ADR-0126 | 🟢 LV/HQ | ⭐ | P2 | platform-team |

---

## 🎯 Prioritization Strategy

### P0 - Critical (🔴 HV/HQ without tests/dry-run)
**Impact:** These scripts can cause production incidents if they fail
**Timeline:** Complete by Week 2 (2026-01-24)

| Script | Why Critical | Action Needed |
|--------|-------------|---------------|
| validate_metadata.py | Gates every PR, corrupted metadata = broken platform | Add dry-run mode |
| secret_request_parser.py | Generates Terraform, wrong output = failed deploys | Add integration test |
| platform_health.py | Drives governance decisions, bad data = wrong choices | Add dry-run + unit tests |
| standardize_metadata.py | Mass-edits files, bug = corrupted headers everywhere | Add dry-run mode |
| pr_guardrails.py | Blocks PRs, false positive = developer friction | Add unit tests |

### P1 - High (Missing one dimension)
**Impact:** Partial safety, needs completion
**Timeline:** Complete by Week 3 (2026-01-31)

| Script | Current State | Gap |
|--------|--------------|-----|
| backfill_metadata.py | Has dry-run ✅ | Needs unit tests |
| validate_govreg.py | Validates registry ✅ | Needs unit tests |

### P2 - Medium (🟡 MV/MQ or utility scripts)
**Impact:** Lower blast radius, but still important
**Timeline:** Complete by Week 4 (2026-02-07)

### P3 - Low (🟢 LV or generators)
**Impact:** Read-only or low-risk operations
**Timeline:** Complete by Week 5 (2026-02-15)

---

## Implementation Roadmap

### Week 1 (2026-01-13 to 2026-01-19): Foundation
- [ ] Create `tests/unit/test_platform_health.py`
- [ ] Create `tests/unit/test_pr_guardrails.py`
- [ ] Create `tests/unit/test_standardize_metadata.py`
- [ ] Add `--dry-run` to `validate_metadata.py`
- [ ] Add `--dry-run` to `platform_health.py`

### Week 2 (2026-01-20 to 2026-01-26): Critical Scripts
- [ ] Add `--dry-run` to `standardize_metadata.py`
- [ ] Add integration test for `secret_request_parser.py`
- [ ] Create `tests/unit/test_validate_govreg.py`
- [ ] Create `tests/unit/test_backfill_metadata.py`

### Week 3 (2026-01-27 to 2026-02-02): Medium Priority
- [ ] Add tests for AWS inventory
- [ ] Add tests for sync scripts
- [ ] Add dry-run to audit scripts

### Week 4-5 (2026-02-03 to 2026-02-15): Cleanup \u0026 Documentation
- [ ] Add tests for generator scripts
- [ ] Update CONFIDENCE_MATRIX.md with results
- [ ] Document dry-run patterns in runbook

### Future Scope: Infrastructure Governance (Post-Feb 15)
- [ ] **Terraform Certification**: Extend "Born Governed" to `infra/modules/`.
- [ ] **Contract**: Define metadata standard for TF modules (e.g., inside `versions.tf`).
- [ ] **Validation**: Enforce `tflint`, `checkov`, and `terraform validate` presence.
- [ ] **Matrix**: Include Terraform modules in the central Certification Matrix.

---

## 🛠️ Dry-Run Implementation Template

```python
#!/usr/bin/env python3
"""
Script: example_script.py
Purpose: [Description]
VQ: [🔴/🟡/🟢] [HV/MV/LV]/[HQ/MQ/LQ]
Maturity: ⭐⭐⭐ (Validated)
"""
import argparse

def main(dry_run=False):
    if dry_run:
        print("[DRY-RUN] Would perform action X")
        print("[DRY-RUN] Would modify files: a.txt, b.txt")
        return

    # Actual logic here
    perform_action()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without writing")
    args = parser.parse_args()

    main(dry_run=args.dry_run)
```

---

## 📈 Success Metrics

**Target State (2026-02-15):**
- ✅ 100% of 🔴 HV/HQ scripts have unit tests
- ✅ 100% of state-modifying scripts have dry-run mode
- ✅ Mean Confidence Score: ⭐⭐⭐ (3.0) or higher
- ✅ Zero scripts at ⭐ (Experimental) level

**Current State:**
- Mean Confidence Score: ⭐⭐ (2.0)
- Scripts at ⭐⭐⭐+: 10%

---

## Weekly Review Process

Every Friday:
1. Update this matrix with progress
2. Triage any new scripts added during the week
3. Adjust priorities based on lessons learned
4. Celebrate wins

---

**Last Updated:** 2026-01-12
**Next Review:** 2026-01-17
