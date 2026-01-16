---
id: test-plan
title: RDS Request Parser Test Plan
type: test-plan
category: testing
relates_to:
  - SCRIPT-0034
  - ADR-0160
---

## Test Plan: RDS Request Parser (SCRIPT-0034)

**Feature/Component:** RDS Request Parser (`scripts/rds_request_parser.py`)
**Created:** 2026-01-15
**Created By:** Platform Team (AI-assisted)
**Test Type:** [x] Unit [ ] Feature [ ] Integration [ ] Smoke
**Status:** [x] Complete

---

## 1. Executive Summary

Testing the RDS request parser which transforms YAML contract files into Terraform tfvars and Kubernetes ExternalSecret manifests. This parser follows the contract-driven architecture pattern established in ADR-0160.

---

## 2. Test Objectives

### What We're Testing

- YAML parsing and validation
- Enum validation against `schemas/metadata/enums.yaml`
- Conditional business rules (environment-specific constraints)
- Terraform tfvars generation
- ExternalSecret manifest generation

### Why We're Testing It

- **Primary Reason:** New feature - self-service RDS provisioning
- **Related Documentation:** ADR-0160, CL-0130
- **Risk if Not Tested:** Invalid configurations could be deployed to AWS

---

## 3. Scope

### In Scope

- [x] Request parsing from YAML
- [x] Required field validation
- [x] Enum validation (size, environment, domain, owner, risk)
- [x] Conditional rules (dev size limits, prod backup requirements)
- [x] Tfvars generation with correct structure
- [x] ExternalSecret generation with correct structure

### Out of Scope

- [ ] Actual Terraform apply
- [ ] AWS resource creation
- [ ] Secrets Manager integration

---

## 4. Prerequisites

### Environment Requirements

- **OS:** macOS/Linux
- **Python Version:** 3.11+
- **Dependencies:** pytest, pyyaml

### Setup Steps

```bash
pip install pytest pyyaml
```

---

## 5. Test Cases

### Test Case 1: Parse Valid Request

**Objective:** Verify parser extracts all fields correctly
**Priority:** [x] Critical

**Pass Criteria:**

- [x] All required fields extracted
- [x] Optional fields use defaults when missing

### Test Case 2: Missing Required Fields

**Objective:** Verify parser raises errors for missing required fields
**Priority:** [x] Critical

**Pass Criteria:**

- [x] KeyError raised for missing `rds_id`
- [x] KeyError raised for missing `spec` section

### Test Case 3: Enum Validation

**Objective:** Verify invalid enum values are rejected
**Priority:** [x] Critical

**Pass Criteria:**

- [x] Invalid `size` raises ValueError
- [x] Invalid `environment` raises ValueError
- [x] Invalid `domain` raises ValueError

### Test Case 4: Conditional Rules

**Objective:** Verify environment-specific business rules
**Priority:** [x] High

**Pass Criteria:**

- [x] Dev environment only allows small/medium sizes
- [x] Prod environment requires 14+ day backup retention
- [x] Max storage must exceed allocated storage

### Test Case 5: Tfvars Generation

**Objective:** Verify correct Terraform output structure
**Priority:** [x] Critical

**Pass Criteria:**

- [x] All required keys present
- [x] Size mapped to instance class correctly
- [x] Values match input request

### Test Case 6: ExternalSecret Generation

**Objective:** Verify correct K8s manifest structure
**Priority:** [x] High

**Pass Criteria:**

- [x] apiVersion correct
- [x] Secret store reference correct
- [x] Data keys match expected structure

---

## 6. Success Criteria

### Overall Success Defined As

- [x] All 16 test cases pass
- [x] No blocking issues found
- [x] 100% pass rate

### Acceptable Failure Rate

0 failures for all test cases

---

## 7. Test Execution Log

| Date | Tester | Status | Notes |
| --- | --- | --- | --- |
| 2026-01-15 | Platform Team | Complete | 16/16 tests passed |

---

## 8. Approvals

- [x] **Test Plan Reviewed By:** Platform Team
- [x] **Ready for Execution:** Yes
- [x] **Approved By:** Platform Team

---

**Related Documents:**

- Test Record: [test-record-20260115.md](./test-record-20260115.md)
- ADR: [ADR-0160](../../../docs/adrs/ADR-0160-rds-optional-toggle-integration.md)
- Unit Tests: [test_script_0034.py](../test_script_0034.py)
