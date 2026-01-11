---
id: TESTS_ROOT
title: Testing Strategy
type: documentation
owner: platform-team
status: active
category: testing
---

# 📊 Platform Testing Dashboard


**Status:** ✅ 100% Pass Rate | **Automation Maturity:**  (Validated) | **Latest Update:** 2026-01-07

---

## 🏗️ Testing-as-a-Forethought
Testing is a proactive part of our development loop. Use the scaffolding utility to initialize new tests:

```bash
# Scaffold a NEW test suite
python3 scripts/scaffold_test.py --feature "new-capability"

# Scaffold a NEW unit test
python3 scripts/scaffold_test.py --script "scripts/my_script.py"
```

> [!TIP]
> **AGENTS**: Start with the [**Agent Instructions**](./AGENT_INSTRUCTIONS.md) (The "START HERE" guide).

---

## Automation Confidence Matrix
*Every component is certified using the [Five-Star Approval Scale](./TESTING_STANDARDS.md#maturity-rating-scale).*

| Rating | Certification | Requirements |
| :--- | :--- | :--- |
|  | **Experimental** | Passes linter (`ruff`/`yamllint`). |
|  | **Documented** | Linked to ADR/CL; has explicit owner. |
|  | **Validated** | Supports Idempotency + unit tests pass. |
|  | **Certified** | Verified via manual/automated "Field Test". |
|  | **Golden Core** | Immutable, observable, multi-env verified. |

---

## Current Test Scenarios

### **Core Scenarios** (High-Fidelity)
| Scenario | Status | Maturity | Focus |
| :--- | :--- | :--- | :--- |
| [**ECR Catalog Generator**](./features/ecr_catalog_generator/) | ✅ PASS |  | Risk-based security controls documentation. |
| [**Doc Auto-Healing**](./features/doc_auto_healing/) | ✅ PASS |  | Frontmatter normalization & link repair. |
| [**Governance Traceability**](./features/governance_traceability/) | ✅ PASS |  | Hard-gate link between code and ADRs. |
| [**Enum Consistency**](./features/enum_consistency/) | ✅ PASS |  | Intelligence-ready metadata validation. |
| [**Secret Request Flow**](./feature-tests/secret-request-flow/) | ✅ PASS |  | End-to-end camelCase secret lifecycle. |

### **Operational Suites**
| Suite | Type | Status | Coverage |
| :--- | :--- | :--- | :--- |
| [**Unit Tests**](./unit/) | Logic | ✅ 13/13 | Core Python governance utilities. |
| [**Templates**](./templates/) | Scaffolding | ✅ Active | Standardized plans and records. |

### Planned & In-Progress
- [ ] **Risk-Based Policies**: Terraform control validation.
- [ ] **Self-Service Workflow**: End-to-end registry creation.
- [ ] **Leak Protection**: Secret-scanning integration verification.

---

## Protocols & Standards
-  [**Testing Standards**](./TESTING_STANDARDS.md): The "Testing Bible" (5-Phase Model).
-  [**Quick Reference**](./unit/QUICK_REFERENCE.md): Command cheat sheet for operators.

---

## Performance Metrics
- **Mean Confidence Score:** .2
- **Test Execution Time (Total):** 0.12s
- **CI Reliability:** 99.8%

---

---

## Maintenance
Every Friday, the `platform-team` performs a **Maturity Audit** to ensure all feature tests remain valid and unit test coverage is expanded for new utilities.

**Rules of Engagement:**
1. ✅ No PR is merged without corresponding tests.
2. ✅ All tests MUST produce a signed-off record.
3. ✅ "Red" statuses must be resolved within 2 hours.
