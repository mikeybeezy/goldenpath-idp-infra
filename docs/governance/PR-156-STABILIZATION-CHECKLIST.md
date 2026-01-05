---
id: PR-156-CHECKLIST
title: 'PR #156: Stabilization & Compliance Checklist'
type: documentation
category: governance
version: '1.0'
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
relates_to:
  - ADR-0098
  - CL-0059
  - 24_PR_GATES
---

# PR #156: Stabilization & Compliance Checklist

This checklist documents the validation steps required for **PR #156** to ensure the ECR registry pipeline is stable and all governance gates pass deterministically.

## 1. Metadata Core Stabilization
- [ ] **Shallow Copy Fix:** Verify `scripts/standardize_metadata.py` uses `copy.deepcopy()` to prevent metadata key truncation.
- [ ] **Schema Compliance:** Run `python3 scripts/validate_metadata.py --path docs/` and confirm 100% pass rate.
- [ ] **Header Injection:** Confirm all 388+ markdown files have valid YAML frontmatter.

## 2. CI/CD Workflow Alignment
- [ ] **Pull Request Triggers:** Verify `.github/workflows/` files (Guardrails, ADR Policy, Changelog Policy, Metadata Validation) trigger on both `main` AND `development`.
- [ ] **Guardrail Enforcement:** Confirm PR body contains the mandatory checklist selections from `.github/pull_request_template.md`.
- [ ] **Branch Policy Guard:** Ensure `fix/metadata-compliance-dev` successfully targets `development`.

## 3. YAML & Linting Quality
- [ ] **Duplicate Key Audit:** Confirm `enforcement:` block is consolidated in `docs/policies/POL-ECR-*.yaml`.
- [ ] **Catalog Indentation:** Verify `docs/catalogs/*.yaml` comments use standardized 0-indentation to satisfy `yamllint`.
- [ ] **Test Results:** Confirm `yamllint docs/policies/ docs/catalogs/` returns "ALL GREEN" locally.

## 4. Onboarding & Documentation
- [ ] **ADR-0098:** Verify decision record created for Standardized PR Gates.
- [ ] **CL-0059:** Verify changelog entry captures stabilization fixes.
- [ ] **CONTRIBUTING.md:** Confirm branching strategy updated to `development -> main` flow.
- [ ] **Walkthrough:** Confirm walkthrough documents the risk-based ECR controls and domain-based catalogs.

## 5. Verification Command Summary
```bash
# Validate metadata
python3 scripts/validate_metadata.py --path docs/

# Validate YAML linting
yamllint docs/policies/POL-ECR-*.yaml docs/catalogs/*.yaml

# Check branch current status
git branch --show-current
```
