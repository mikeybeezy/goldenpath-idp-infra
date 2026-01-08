---
id: TEST_PLAN_TEMPLATE
title: Test Plan Template
type: template
owner: platform-team
status: active
category: testing
---

# Test Plan Template


**Feature/Component:** [Name of what you're testing]
**Created:** YYYY-MM-DD
**Created By:** [Your name]
**Test Type:** [ ] Unit [ ] Feature [ ] Integration [ ] Smoke
**Status:** [ ] Draft [ ] Ready [ ] In Progress [ ] Complete

---

## 1. Executive Summary

[2-3 sentences describing what you're testing and why]

---

## 2. Test Objectives

### What We're Testing
[Specific feature, function, or workflow]

### Why We're Testing It
- **Primary Reason:** [Main driver - new feature, bug fix, compliance]
- **Related Documentation:** [Link to ADR, Issue, or Requirement]
- **Risk if Not Tested:** [What could go wrong]

---

## 3. Scope

### In Scope
- [ ] [Specific item1]
- [ ] [Specific item 2]
- [ ] [Specific item 3]

### Out of Scope
- [ ] [What's explicitly NOT being tested]
- [ ] [What's being deferred]

---

## 4. Prerequisites

### Environment Requirements
- **OS:** [macOS, Linux, etc.]
- **Python Version:** [e.g., 3.11+]
- **Dependencies:** [List all required packages]
- **Access:** [Any special permissions needed]

### Data Requirements
- [ ] Test data prepared
- [ ] Fixtures created
- [ ] Sample inputs available

### Setup Steps
```bash
# List exact commands to prepare environment
step 1
step 2
```

---

## 5. Test Cases

### Test Case 1: [Description]
**Objective:** [What this case validates]
**Priority:** [ ] Critical [ ] High [ ] Medium [ ] Low

**Steps:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Expected Result:**
[What should happen]

**Pass Criteria:**
- [ ] [Specific measurable criterion 1]
- [ ] [Specific measurable criterion 2]

**Fail Criteria:**
- [ ] [What would indicate failure]

---

### Test Case 2: [Description]
[Repeat structure above for each test case]

---

## 6. Success Criteria

### Overall Success Defined As
- [ ] All critical test cases pass
- [ ] No blocking issues found
- [ ] Performance acceptable (if applicable)
- [ ] Documentation complete

### Acceptable Failure Rate
[e.g., "0 failures for critical paths, up to 10% for edge cases"]

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to avoid] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to avoid] |

---

## 8. Timeline

- **Test Start Date:** YYYY-MM-DD
- **Estimated Duration:** [X hours/days]
- **Test End Date:** YYYY-MM-DD
- **Reporting Date:** YYYY-MM-DD

---

## 9. Rollback Plan

If test fails or environment breaks:
```bash
# Commands to restore to baseline
rollback command 1
rollback command 2
```

---

## 10. Test Execution Log

| Date | Tester | Status | Notes |
|------|--------|--------|-------|
| YYYY-MM-DD | [Name] | Planned | Test plan created |
| YYYY-MM-DD | [Name] | In Progress | Execution started |
| YYYY-MM-DD | [Name] | Complete | Results documented |

---

## 11. Approvals

- [ ] **Test Plan Reviewed By:** _______________
- [ ] **Ready for Execution:** Yes / No
- [ ] **Approved By:** _______________

---

## Notes

[Any additional context, assumptions, or considerations]

---

**Related Documents:**
- Test Record: [Link when created]
- ADR: [Link]
- GitHub Issue: [Link]
