---
id: test-plan
title: metadata
type: test-suite
---

# Test Plan: ECR Registry Single Source of Truth

**ID:** TEST-ECR-001
**Related ADR:** ADR-0129
**Owner:** Platform Team
**Status:** DRAFT

---

## 1. PLAN

### Objectives
- **What are we testing?** The `scripts/sync_ecr_catalog.py` reconciliation logic.
- **Why are we testing it?** To ensure the Backstage catalog is a high-fidelity mirror of AWS ECR state and governance intent.
- **Success Criteria:**
    - Script correctly identifies "Ghosts" (defined in catalog, missing in AWS).
    - Script correctly identifies "Orphans" (existing in AWS, missing in catalog).
    - Script correctly generates/updates the Backstage `Resource` entity.
- **Failure Criteria:**
    - Script misses a discrepancy.
    - Script generates invalid YAML.
    - Script errors out due to missing metadata.

### System Details
- **Test Type:** Feature Test (End-to-End)
- **Environment:** Local / Advisory (Mock AWS CLI)
- **Risk Level:** Medium (Governance visibility)

---

## 2. SETUP

### Requirements
- Python 3.x
- `PyYAML` installed
- Access to `docs/20-contracts/catalogs/ecr-catalog.yaml`

### Steps
1. Create a baseline snapshot of the catalog.
2. Inject a "Ghost" repository into the catalog.
3. (Simulated) Inject an "Orphan" by mocking AWS CLI response.

---

## 3. EXECUTE

### Scenario 1: Ghost Detection
1. Add `phantom-test-repo` to `ecr-catalog.yaml`.
2. Run `python3 scripts/sync_ecr_catalog.py`.
3. Verify output contains "Ghosts: X" including `phantom-test-repo`.

### Scenario 2: Backstage Parity
1. Verify `backstage-helm/catalog/resources/ecr-registry.yaml` is updated.
2. Check description contains the new repo.
3. Check `platform/last-sync` timestamp is current.

---

## 4. DOCUMENT
- Capture stdout to `test-output/reconciliation.log`.
- Capture generated YAML to `test-output/ecr-registry.yaml`.

---

## 5. VERIFY
- [ ] Results reviewed by Platform Lead
- [ ] Success criteria met
- [ ] Documentation complete
- [ ] Index updated in `tests/README.md`
