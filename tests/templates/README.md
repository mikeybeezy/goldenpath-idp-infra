# Testing Templates - Quick Start Guide

**Purpose:** Standardized templates for consistent, repeatable testing
**Last Updated:** 2026-01-07

---

## Available Templates

| Template | Use For | Copy Command |
|----------|---------|--------------|
| `TEST_PLAN_TEMPLATE.md` | Planning any test | `cp tests/templates/TEST_PLAN_TEMPLATE.md tests/feature-tests/my-test/test-plan.md` |
| `TEST_RECORD_TEMPLATE.md` | Documenting results | `cp tests/templates/TEST_RECORD_TEMPLATE.md tests/feature-tests/my-test/test-record-$(date +%Y%m%d).md` |
| `UNIT_TEST_TEMPLATE.py` | Python unit tests | `cp tests/templates/UNIT_TEST_TEMPLATE.py tests/unit/test_my_module.py` |
| `FEATURE_TEST_TEMPLATE.md` | Feature testing | `cp tests/templates/FEATURE_TEST_TEMPLATE.md tests/feature-tests/my-feature/README.md` |

---

## Quick Start

### I Want to Write a Unit Test

1. **Copy the template:**
   ```bash
   cp tests/templates/UNIT_TEST_TEMPLATE.py tests/unit/test_my_module.py
   ```

2. **Replace placeholders:**
   - `your_module` → actual module name
   - `your_function` → actual function name
   - `TestYourModule` → descriptive class name

3. **Write tests using AAA pattern:**
   - **Arrange:** Set up test data
   - **Act:** Call the function
   - **Assert:** Verify results

4. **Run your tests:**
   ```bash
   python3 tests/unit/test_my_module.py -v
   ```

---

### I Want to Test a Feature

1. **Create directory:**
   ```bash
   mkdir -p tests/feature-tests/my-feature
   cd tests/feature-tests/my-feature
   ```

2. **Copy template:**
   ```bash
   cp ../../templates/FEATURE_TEST_TEMPLATE.md README.md
   ```

3. **Create structure:**
   ```bash
   mkdir -p test-data expected-output actual-output
   ```

4. **Fill in the template:**
   - What are you testing?
   - What's the expected output?
   - Document test steps

5. **Execute and document:**
   - Run your test steps
   - Save output to `actual-output/`
   - Compare with `expected-output/`
   - Create test record

---

### I Want to Document Test Results

1. **Copy template:**
   ```bash
   cp tests/templates/TEST_RECORD_TEMPLATE.md tests/feature-tests/my-test/test-record-20260107.md
   ```

2. **Fill in all sections:**
   - Executive summary
   - Environment details
   - Execution steps
   - Results
   - Evidence
   - Sign-off

3. **Attach evidence:**
   - Copy logs to test directory
   - Include screenshots
   - Link to GitHub issues

---

## Template Customization

### When to Modify Templates

✅ **DO modify** templates for your specific test:
- Replace [placeholders] with actual values
- Remove sections that don't apply
- Add custom sections if needed

 **DON'T modify** the source templates in `/tests/templates/`:
- These are your starting point
- Keep them generic
- Your changes would affect everyone

### Suggesting Template Improvements

If you find the templates lacking:
1. Note what's missing
2. Propose addition in #platform-team
3. Update template with team approval

---

## Best Practices

### Unit Tests
1. **One test, one thing:** Each test should verify one specific behavior
2. **Use descriptive names:** `test_function_with_invalid_input_raises_error`
3. **AAA Pattern:** Arrange, Act, Assert (clearly separated)
4. **Clean up:** Use `tearDown()` to clean resources
5. **Don't test external APIs:** Mock them instead

### Feature Tests
1. **Document everything:** Someone should be able to reproduce your test
2. **Save all evidence:** Logs, screenshots, outputs
3. **Compare outputs:** Use `diff` or visual comparison
4. **Test the happy path first:** Then edge cases and errors

### Test Records
1. **Be specific:** "Returns 200" not "works"
2. **Include raw output:** Either inline or as attached file
3. **Link to issues:** If test found bugs
4. **Sign off:** Don't leave incomplete records

---

## Examples

### Good Unit Test Name
```python
def test_verify_injection_with_governance_block_returns_true():
    """Test that verify_injection detects Helm values governance block"""
```

### Bad Unit Test Name
```python
def test_1():
    """Test injection"""
```

### Good Feature Test Directory
```
tests/feature-tests/ecr-catalog-generator/
├── README.md                    # Test plan
├── test-record-20260105.md      # Results
├── test-data/
│   └── sample-catalog.yaml      # Input
├── expected-output/
│   └── expected-doc.md          # What should generate
└── actual-output/
    └── generated-doc.md         # What actually generated
```

### Bad Feature Test Directory
```
tests/feature-tests/test1/
└── notes.txt
```

---

## Checklist: "Is My Test Complete?"

Before marking a test as "done":

- [ ] Test plan exists (or test is clearly documented)
- [ ] Test has been executed
- [ ] Results are documented
- [ ] Evidence is attached
- [ ] Issues are filed (if any found)
- [ ] Test record is signed off
- [ ] Test is added to main index (`tests/README.md`)
- [ ] Someone else could reproduce this test

---

## Getting Help

| Question | Resource |
|----------|----------|
| How do I structure a test? | Read the template |
| What should I test? | See [TESTING_STANDARDS.md](../TESTING_STANDARDS.md) |
| How do I run tests? | See [tests/unit/QUICK_REFERENCE.md](../unit/QUICK_REFERENCE.md) |
| Template doesn't fit my need | Ask in #platform-team Slack |

---

## Updating This Guide

If you find these templates unclear or incomplete:
1. Document what confused you
2. Propose improvement
3. Submit PR with updates

**Remember:** Good templates make testing easier for everyone!
