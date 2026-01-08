---
id: AGENT_INSTRUCTIONS
title: Agent Instructions
type: documentation
owner: platform-team
status: active
category: testing
---

# 🤖 Platform Agent Testing Instructions


> [!IMPORTANT]
> **START HERE**: All AI Agents (Antigravity or others) must follow this protocol for every code change to ensure platform integrity and traceability.

---

## 🛠️ The Mandatory Agent Workflow

Every task that involves code modification MUST end with this pipeline:

### 1. **SCAFFOLD** (Forethought)
If you are creating a new feature or script, run the scaffolding utility immediately after the plan is approved:
```bash
python3 scripts/scaffold_test.py --feature "new-feature-name"
# OR
python3 scripts/scaffold_test.py --script "scripts/new_utility.py"
```

### 2. **EXECUTE & CAPTURE**
Run your tests and capture **Raw Output** and **Evidence**:
- **Raw Output**: `command 2>&1 | tee actual-output.txt`
- **Evidence**: Artifact logs or screenshots (using `generate_image` if UI is affected).

### 3. **RECORD** (Traceability)
Populate the [**`TEST_RECORD_TEMPLATE.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/tests/templates/TEST_RECORD_TEMPLATE.md) in the test folder.
- Link to the **ADR** and **Changelog**.
- Assign a **Confidence Rating** based on the [**Confidence Matrix**](../TESTING_STANDARDS.md#maturity-rating-scale).

### 4. **DASHBOARD SYNC**
Update the top-level [**`tests/README.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/tests/README.md) with your results.

---

## Required Artifacts for Every Test

| Artifact | Location | Purpose |
| :--- | :--- | :--- |
| **Test Plan** | `test-plan.md` | Defines success/failure criteria BEFORE execution. |
| **Test Record** | `test-record-YYYYMMDD.md` | The evidence of execution and final sign-off. |
| **Raw Output** | `actual-output.txt` | The unformatted proof of the test run. |
| **Dashboard Entry** | `tests/README.md` | Surfaces results to the rest of the team. |

---

## ⭐ Confidence Certification

When documenting a test, you MUST certify the maturity of the component:

| Rating | Required Evidence |
| :--- | :--- |
| **⭐** | Lint logs passing. |
| **⭐⭐** | Metadata exists with `owner` and `ADR` link. |
| **⭐⭐⭐** | Unit tests passing + Idempotency verified. |
| **⭐⭐⭐⭐** | Feature test record created by a human/agent combo. |
| **⭐⭐⭐⭐⭐** | Verified across Multi-environment PR gates. |

---

## 🚫 Common Agent Pitfalls (Do Not Do These)
-  **Do not skip the Test Plan.** Testing is a forethought, not an afterthought.
-  **Do not swallow error logs.** Every failure must be surfaced and analyzed.
-  **Do not "Drill Down" in silence.** If you find a bug during testing, notify the user immediately.
-  **Do not forget the Dashboard.** If it isn't on the dashboard, it didn't happen.

---

**Certified By:** Platform Governance Office
**Last Updated:** 2026-01-07
