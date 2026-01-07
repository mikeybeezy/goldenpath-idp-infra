# Test Record Template

**Test Name:** [Descriptive name]  
**Date:** YYYY-MM-DD  
**Tester:** [Your name]  
**Test Type:** Unit / Feature / Integration / Smoke  
**Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL / 🚧 BLOCKED

---

## Executive Summary

[2-3 sentences summarizing what was tested and the outcome]

**Quick Stats:**
- **Total Test Cases:** X
- **Passed:** X (X%)
- **Failed:** X (X%)
- **Blocked:** X (X%)

---

## Test Plan Reference

**Test Plan:** [Link to test-plan.md]  
**Original Objectives:** [Brief restatement]  
**Changes from Plan:** [Any deviations from original plan]

---

## Environment Details

### System Information
- **OS:** [e.g., macOS 14.1, Ubuntu 22.04]
- **Python Version:** [e.g., 3.11.5]
- **Git Commit:** [e.g., abc1234]
- **Branch:** [e.g., feature/new-tests]

### Dependencies
```bash
# List installed versions
pip freeze | grep -E "yaml|requests|pytest"
```

### Environment Variables
- `VAR_NAME`: value
- `ANOTHER_VAR`: value

---

## Pre-Test Baseline

**Captured:** YYYY-MM-DD HH:MM:SS

[Document state before testing began]
- Files modified: None
- Services running: [List]
- Data state: [Baseline description]

---

## Test Execution

### Test Case 1: [Name]
**Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL / 🚧 BLOCKED  
**Duration:** XX seconds  
**Priority:** Critical / High / Medium / Low

**Steps Executed:**
1. [Action taken]
   ```bash
   command executed
   ```

2. [Action taken]
   ```bash
   command executed
   ```

**Expected Result:**
[What should have happened]

**Actual Result:**
[What actually happened]

**Evidence:**
- Screenshot: [Link or filename]
- Log file: [Link or filename]
- Output: [Inline or link]

**Pass Criteria Met:**
- [x] Criterion 1
- [x] Criterion 2
- [ ] Criterion 3 (If failed, explain why)

---

### Test Case 2: [Name]
[Repeat structure above for each test case]

---

## Results Summary

### Overall Results

| Category | Count | Percentage |
|----------|-------|------------|
| Total Test Cases | X | 100% |
| Passed | X | X% |
| Failed | X | X% |
| Blocked | X | X% |
| Skipped | X | X% |

### Critical Path Status
- [ ] All critical test cases passed
- [ ] No blocking issues found
- [ ] Success criteria met

---

## Issues Found

### Issue 1: [Title]
**Severity:** Critical / High / Medium / Low  
**Status:** [ ] Open [ ] Fixed [ ] Deferred  
**GitHub Issue:** #XXX

**Description:**
[Detailed description of the issue]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]

**Expected vs Actual:**
- **Expected:** [What should happen]
- **Actual:** [What actually happened]

**Workaround:**
[If available]

**Fix Required:**
[What needs to change]

---

### Issue 2: [Title]
[Repeat structure for each issue]

---

## Evidence Archive

### Logs
- `test-execution-full.log` - Complete execution log
- `error.log` - Error messages only
- `debug.log` - Debug output

### Screenshots
- `screenshot-1-baseline.png` - Initial state
- `screenshot-2-execution.png` - During test
- `screenshot-3-result.png` - Final state

### Output Files
- `output/test-case-1-result.json` - Test case 1 output
- `output/test-case-2-result.json` - Test case 2 output

### Raw Data
```
[Include key output inline if short, or link to file if long]
```

---

## Performance Metrics

[If applicable]

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Response Time | < 1s | 0.5s | ✅ |
| Memory Usage | < 500MB | 320MB | ✅ |
| CPU Usage | < 50% | 35% | ✅ |

---

## Deviations from Plan

### Changes Made During Execution
1. [Change 1] - Reason: [Why]
2. [Change 2] - Reason: [Why]

### Test Cases Skipped
- [Test case name] - Reason: [Why skipped]

### Additional Tests Added
- [Test case name] - Reason: [Why added]

---

## Lessons Learned

### What Went Well
- [Thing 1]
- [Thing 2]

### What Could Be Improved
- [Improvement 1]
- [Improvement 2]

### Discoveries
- [Unexpected finding 1]
- [Unexpected finding 2]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

---

## Follow-up Actions

- [ ] [Action 1] - Assigned to: [Name] - Due: YYYY-MM-DD
- [ ] [Action 2] - Assigned to: [Name] - Due: YYYY-MM-DD
- [ ] [Action 3] - Assigned to: [Name] - Due: YYYY-MM-DD

---

## Post-Test Cleanup

**Cleanup Completed:** YYYY-MM-DD HH:MM:SS

- [ ] Test data removed
- [ ] Temporary files deleted
- [ ] Environment restored to baseline
- [ ] Resources released

```bash
# Cleanup commands executed
cleanup command 1
cleanup command 2
```

---

## Verification & Sign-off

### Self-Review Checklist
- [ ] All test cases documented
- [ ] All evidence attached
- [ ] Issues filed in GitHub
- [ ] Results match success criteria
- [ ] Documentation complete

### Peer Review
**Reviewed By:** _______________  
**Review Date:** YYYY-MM-DD  
**Review Status:** [ ] Approved [ ] Changes Requested

**Reviewer Comments:**
[Comments here]

### Final Sign-off
**Test Complete:** [ ] Yes [ ] No  
**Ready for Production:** [ ] Yes [ ] No [ ] N/A  
**Signed Off By:** _______________  
**Date:** YYYY-MM-DD

---

## Related Documentation

- **Test Plan:** [Link]
- **ADR:** [Link]
- **GitHub Issues:** [Links]
- **Previous Test Records:** [Links]
- **Related Features:** [Links]

---

## Appendix

### Additional Notes
[Any other relevant information]

### Raw Commands Log
```bash
# Complete command history
command 1
command 2
command 3
```

### Configuration Files
[If test required special config, include or link here]
