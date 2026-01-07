# Feature Test Template

**Feature Name:** [Name of the feature being tested]  
**Test Date:** YYYY-MM-DD  
**Tester:** [Your name]  
**Status:** [ ] Planning [ ] In Progress [ ] Complete

---

## Feature Overview

### What is this feature?
[Brief description of the feature's purpose and functionality]

### Why are we testing it?
- **Trigger:** [New feature / Bug fix / Compliance requirement]
- **Related:** [Link to ADR, GitHub Issue, or Requirement]

---

## Test Scope

### What We're Testing
- [ ] [Specific capability 1]
- [ ] [Specific capability 2]
- [ ] [Specific capability 3]

### What We're NOT Testing
- [ ] [Out of scope item 1]
- [ ] [Out of scope item 2]

---

## Success Criteria

Feature is considered working when:
- [ ] [Criterion 1 - Specific and measurable]
- [ ] [Criterion 2 - Specific and measurable]
- [ ] [Criterion 3 - Specific and measurable]

---

## Test Environment

**Directory Structure:**
```
tests/feature-tests/[feature-name]/
├── test-plan.md           ← This file (optional if using template)
├── test-record-YYYYMMDD.md  ← Results
├── test-data/             ← Input fixtures
│   └── sample-input.yaml
├── expected-output/       ← What should happen
│   └── expected-result.yaml
└── actual-output/         ← What actually happened
    └── actual-result.yaml
```

**Environment Setup:**
```bash
# Commands to prepare environment
cd /path/to/goldenpath-idp-infra
# Additional setup commands
```

---

## Test Data

### Input Data
**Location:** `test-data/`

**Description:**
[Describe the test data being used]

**Sample:**
```yaml
# Example of input data
key: value
```

### Expected Output
**Location:** `expected-output/`

**Description:**
[Describe what the expected output should look like]

**Sample:**
```yaml
# Example of expected output
result: success
```

---

## Test Procedures

### Pre-Test Checklist
- [ ] Environment prepared
- [ ] Test data in place
- [ ] Dependencies installed
- [ ] Baseline state captured

### Test Steps

#### Step 1: [Description]
**Command:**
```bash
command to execute
```

**Expected Outcome:**
[What should happen]

**How to Verify:**
[How to tell if it worked - specific file, output, behavior]

---

#### Step 2: [Description]
**Command:**
```bash
command to execute
```

**Expected Outcome:**
[What should happen]

**How to Verify:**
[How to tell if it worked]

---

#### Step 3: [Description]
[Repeat for each step]

---

### Post-Test Checklist
- [ ] Actual output captured
- [ ] Results compared to expected
- [ ] Differences documented
- [ ] Screenshots taken (if applicable)
- [ ] Test data preserved

---

## Verification

### How to Verify Success

1. **Compare Outputs:**
   ```bash
   diff expected-output/result.yaml actual-output/result.yaml
   ```

2. **Visual Inspection:**
   [If applicable, describe what to look for]

3. **Automated Checks:**
   ```bash
   # Any automated verification scripts
   ./verify-results.sh
   ```

---

## Results Template

### Test Execution

| Step | Status | Notes |
|------|--------|-------|
| 1. [Step name] | ✅ / ❌ | [Brief note] |
| 2. [Step name] | ✅ / ❌ | [Brief note] |
| 3. [Step name] | ✅ / ❌ | [Brief note] |

### Overall Result
**Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

**Summary:** [1-2 sentences on outcome]

---

## Issue Tracking

### Issues Found

**Issue 1:** [Description]
- **Severity:** Critical / High / Medium / Low
- **Status:** Open / Fixed / Deferred
- **GitHub Issue:** #XXX

---

## Evidence

### Screenshots
- `screenshot-1-before.png` - [Description]
- `screenshot-2-during.png` - [Description]
- `screenshot-3-after.png` - [Description]

### Log Files
- `execution.log` - Full execution log
- `error.log` - Error messages

### Output Files
- `actual-output/result.yaml` - [Description]

---

## Notes

### Observations
[Anything unexpected or noteworthy]

### Recommendations
[Suggestions for improvement]

---

## Sign-off

- [ ] **Test Executed:** YYYY-MM-DD
- [ ] **Results Documented:** Yes / No
- [ ] **Issues Filed:** Yes / No / N/A
- [ ] **Ready for Production:** Yes / No

**Tested By:** _______________  
**Verified By:** _______________  
**Date:** YYYY-MM-DD
