# Platform Testing Standards & Protocols

**Version:** 1.0  
**Last Updated:** 2026-01-07  
**Owner:** Platform Team  
**Purpose:** Standardize testing approach across all platform components

---

## Testing Philosophy

### Core Principles
1. **Predictability:** Every test follows the same structure
2. **Repeatability:** Test results are consistent across runs
3. **Traceability:** Every test links back to requirements/ADRs
4. **Documentation:** Test process is as important as test results

### Test Types We Use

| Type | When | Format | Automation |
|------|------|--------|------------|
| **Unit Tests** | Testing individual functions/modules | Python unittest | CI (GitHub Actions) |
| **Feature Tests** | Testing complete features end-to-end | Manual + Documentation | Manual |
| **Integration Tests** | Testing system interactions | Mixed | Planned |
| **Smoke Tests** | Quick health checks | Scripts | Planned |

---

## Standard Test Process

### The 5-Phase Testing Model

```
1. PLAN → 2. SETUP → 3. EXECUTE → 4. DOCUMENT → 5. VERIFY
```

Every test, regardless of type, follows this sequence.

---

## Phase 1: PLAN

### Test Planning Checklist

```markdown
## Test Planning

- [ ] **What are we testing?** (Feature/Component name)
- [ ] **Why are we testing it?** (Links to ADR/Requirement)
- [ ] **What's the success criteria?** (Specific, measurable)
- [ ] **What's the failure criteria?** (What would indicate failure)
- [ ] **Dependencies:** (What needs to exist first)
- [ ] **Environment:** (dev/staging/prod, local/CI)
- [ ] **Test type:** (unit/feature/integration)
- [ ] **Estimated time:** (How long will this take)
- [ ] **Risk level:** (What could break if test fails)
```

### Planning Document Template
Use: `tests/templates/TEST_PLAN_TEMPLATE.md`

---

## Phase 2: SETUP

### Setup Checklist

```markdown
## Test Setup

- [ ] **Environment prepared** (Dependencies installed, data seeded)
- [ ] **Test data created** (Fixtures, mocks, sample data)
- [ ] **Baseline captured** (Current state documented)
- [ ] **Tools verified** (All testing tools working)
- [ ] **Rollback plan defined** (How to undo if needed)
```

### Setup Documentation
- Document exact environment state
- Capture versions of all dependencies
- List all commands run during setup

---

## Phase 3: EXECUTE

### Execution Checklist

```markdown
## Test Execution

- [ ] **Pre-conditions verified** (Everything ready)
- [ ] **Test steps executed** (Follow documented steps)
- [ ] **Output captured** (Logs, screenshots, error messages)
- [ ] **Results recorded** (Pass/fail for each step)
- [ ] **Anomalies documented** (Unexpected behavior noted)
```

### Execution Standards
- **Always capture:** Command input, full output, timestamps
- **Always record:** Expected vs. actual results
- **Always note:** Deviations from plan

---

## Phase 4: DOCUMENT

### Documentation Checklist

```markdown
## Test Documentation

- [ ] **Test record created** (Using standard template)
- [ ] **Results summarized** (Executive summary)
- [ ] **Evidence attached** (Logs, screenshots, outputs)
- [ ] **Issues filed** (If failures found)
- [ ] **Lessons captured** (What we learned)
```

### Documentation Standards
- Use standard templates (see `/tests/templates/`)
- Include raw output files
- Link to related ADRs/Issues
- Tag with date and tester

---

## Phase 5: VERIFY

### Verification Checklist

```markdown
## Test Verification

- [ ] **Results reviewed** (Peer review or self-review)
- [ ] **Success criteria met** (Matches original plan)
- [ ] **Documentation complete** (All sections filled)
- [ ] **Test repeatable** (Someone else can run it)
- [ ] **Index updated** (Test added to main index)
```

### Verification Standards
- Tests aren't "done" until documented
- Someone else should be able to repeat your test
- Results must be verifiable (not "it worked")

---

## Template Library

### Available Templates

| Template | Use For | Location |
|----------|---------|----------|
| `TEST_PLAN_TEMPLATE.md` | Planning any test | `/tests/templates/` |
| `UNIT_TEST_TEMPLATE.py` | Python unit tests | `/tests/templates/` |
| `FEATURE_TEST_TEMPLATE.md` | Feature testing | `/tests/templates/` |
| `TEST_RECORD_TEMPLATE.md` | Documenting results | `/tests/templates/` |
| `INTEGRATION_TEST_TEMPLATE.md` | Integration tests | `/tests/templates/` |

---

## Naming Conventions

### File Naming Standards

```bash
# Feature Tests (directories)
tests/feature-tests/[feature-name]/
  ├── test-plan.md           # What we're testing
  ├── test-record-YYYYMMDD.md  # Results
  ├── test-data/             # Input fixtures
  └── test-output/           # Actual results

# Unit Tests (files)
tests/unit/test_[module_name].py

# Integration Tests (directories)
tests/integration/[workflow-name]/
  ├── test-plan.md
  └── test-record-YYYYMMDD.md
```

### Test Case Naming

```python
# Unit tests
def test_[function]_[scenario]_[expected_result]():
    """Test description in plain English"""
    
# Examples:
def test_verify_injection_with_governance_block_returns_true():
def test_extract_metadata_with_missing_file_returns_error():
```

---

## Test Execution Commands

### Standard Commands

```bash
# Unit Tests - Always run from repo root
python3 -m unittest discover -s tests/unit -p "test_*.py" -v

# Feature Tests - Follow test-plan.md in each directory
cd tests/feature-tests/[feature-name]
cat test-plan.md  # Read the plan first
# Then follow documented steps

# Integration Tests - Follow workflow documentation
cd tests/integration/[workflow-name]
./run-test.sh  # If automated
```

---

## Quality Gates

### Before Merging Code

```markdown
## PR Test Requirements

- [ ] **Affected unit tests pass** (If modifying tested code)
- [ ] **New tests added** (If adding new functionality)
- [ ] **Test documentation updated** (If changing test approach)
- [ ] **CI passes** (GitHub Actions green)
```

### Before Declaring Feature "Done"

```markdown
## Feature Completion Requirements

- [ ] **Feature test plan created**
- [ ] **Feature test executed**
- [ ] **Test record documented**
- [ ] **Known issues logged**
- [ ] **Test added to index**
```

---

## Test Documentation Standards

### Required Sections in Every Test Record

1. **Executive Summary** (2-3 sentences)
2. **Test Metadata** (Date, tester, version, status)
3. **Test Plan Reference** (Link to original plan)
4. **Environment Details** (Exact configuration)
5. **Execution Steps** (What was done)
6. **Results** (What happened - pass/fail per step)
7. **Evidence** (Logs, screenshots, outputs)
8. **Issues Found** (If any)
9. **Lessons Learned** (What we discovered)
10. **Sign-off** (Who verified, status)

### Markdown Template Structure

```markdown
# [Feature/Component] Test Record

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL
**Test Type:** Unit / Feature / Integration

---

## Executive Summary
[2-3 sentence summary]

## Test Plan
[Link to test-plan.md or describe objectives]

## Environment
- OS: 
- Python Version:
- Dependencies:
- Git Commit:

## Execution
### Step 1: [Description]
**Command:** `command here`
**Expected:** [Expected result]
**Actual:** [Actual result]
**Status:** ✅ / ❌

[Repeat for each step]

## Results Summary
- Total Steps: X
- Passed: X
- Failed: X
- Pass Rate: X%

## Evidence
- [Link to logs]
- [Link to screenshots]
- [Attach output files]

## Issues Found
1. [Issue description] - [Link to GitHub issue]

## Lessons Learned
[What we discovered during testing]

## Sign-off
**Reviewed by:** [Name]
**Verified:** ✅ Yes / ❌ No
**Ready for Production:** ✅ Yes / ❌ No
```

---

## Test Index Maintenance

### Updating the Main Index

After completing any test:

1. Open `tests/README.md`
2. Add entry to appropriate section
3. Include: Name, Status, Date, What was tested
4. Link to test record

Example entry:
```markdown
### ECR Catalog Generator
**Location:** [feature-tests/ecr-catalog-generator](./feature-tests/ecr-catalog-generator/)
**Status:** ✅ Passed
**Date:** 2026-01-05
**What:** Tests catalog generator displays risk-based security controls
**Record:** [test-record-20260105.md](./feature-tests/ecr-catalog-generator/test-record-20260105.md)
```

---

## Continuous Improvement

### Monthly Test Review

- Review all test records from past month
- Identify patterns in failures
- Update templates based on learnings
- Archive outdated tests

### Quarterly Standards Review

- Assess if standards are being followed
- Update templates based on feedback
- Add new test types as needed
- Retire unused templates

---

## Quick Reference Card

### "I Need To..."

| Need | Template | Command |
|------|----------|---------|
| Write a unit test | `UNIT_TEST_TEMPLATE.py` | Copy template, modify |
| Test a new feature | `FEATURE_TEST_TEMPLATE.md` | Follow 5-phase process |
| Document test results | `TEST_RECORD_TEMPLATE.md` | Fill in all sections |
| Run existing unit tests | N/A | `python3 -m unittest discover -s tests/unit -p "test_*.py" -v` |
| Add test to index | N/A | Edit `tests/README.md` |

---

## Compliance

### Mandatory Standards
- ✅ Every test MUST have a test plan
- ✅ Every test MUST have a test record
- ✅ Every test MUST update the index
- ✅ Every unit test MUST follow naming conventions
- ✅ Every test MUST be repeatable by someone else

### Recommended Standards
- 📋 Use templates whenever possible
- 📋 Include screenshots for visual changes
- 📋 Link to related ADRs
- 📋 Tag test records with metadata
- 📋 Review tests quarterly

---

## Getting Help

### Resources
- **Templates:** `/tests/templates/`
- **Examples:** All existing tests in `/tests/`
- **Questions:** Ask in #platform-team Slack channel
- **Issues:** File in GitHub with `testing` label

---

**Remember:** Consistent testing builds confidence. Following these standards makes our platform more reliable and our team more efficient.
