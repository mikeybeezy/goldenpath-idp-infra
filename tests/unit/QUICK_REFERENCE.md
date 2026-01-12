---
id: UNIT_TEST_REF
title: Unit Test Quick Reference
type: documentation
applies_to: []
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: none
  maturity: 1
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: testing
---

# Quick Reference: Running Python Unit Tests

## One-Line Commands

```bash
# Run all unit tests (from repo root)
python3 -m unittest discover -s tests/unit -p "test_*.py" -v

# Run all unit tests (quiet mode)
python3 -m unittest discover -s tests/unit -p "test_*.py"

# Run specific test module
python3 tests/unit/test_metadata_inheritance.py -v

# Run single test class
python3 -m unittest tests.unit.test_validate_metadata.TestMetadataValidation -v

# Run single test case
python3 -m unittest tests.unit.test_vq_logger.TestVQLogger.test_get_total_reclaimed_hours_returns_number
```

## Test Modules

| Module | Tests | What It Tests |
|--------|-------|---------------|
| `test_metadata_inheritance.py` | 3 | MetadataConfig inheritance engine |
| `test_validate_metadata.py` | 7 | Injection verification, YAML/MD extraction |
| `test_vq_logger.py` | 3 | ROI tracking and value ledger |

## Expected Output

### Success
```
test_find_parent_metadata ... ok
test_get_effective_metadata_merging ... ok
...
----------------------------------------------------------------------
Ran 13 tests in 0.119s

OK
```

### Failure
```
test_something ... FAIL

======================================================================
FAIL: test_something
----------------------------------------------------------------------
...
FAILED (failures=1)
```

## CI Integration

The tests run automatically via GitHub Actions on:
- Pull requests that modify `scripts/**/*.py` or `tests/**/*.py`
- Pushes to `main` branch with Python changes

**Workflow:** `.github/workflows/python-tests.yml`

## Troubleshooting

### Import Errors
```bash
# Ensure you're in repo root
cd /path/to/goldenpath-idp-infra

# Check Python path
python3 -c "import sys; print('\\n'.join(sys.path))"

# Verify pyyaml is installed
python3 -c "import yaml; print(yaml.__version__)"
```

### Test Failures
1. Check if you're in the correct directory (repo root)
2. Verify dependencies: `pip install pyyaml`
3. Check for modified core scripts that broke contracts
4. Review test output for specific error messages

### CI Failures
1. Check GitHub Actions logs
2. Verify Python version is 3.11
3. Ensure `pyyaml` installation succeeded
4. Compare local vs CI environment

## Adding New Tests

### Template for New Test Module

```python
import os
import sys
import unittest

# Add project root to path
sys.path.append(os.getcwd())
from scripts.your_module import your_function

class TestYourModule(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        pass

    def tearDown(self):
        """Cleanup after each test"""
        pass

    def test_your_feature(self):
        """Test description"""
        result = your_function()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```

### Best Practices
1. Use descriptive test names: `test_<feature>_<scenario>`
2. One assertion per test (when possible)
3. Clean up resources in `tearDown()`
4. Use `tempfile` for temporary files
5. Document complex test logic

## Quick Stats

```bash
# Count total tests
python3 -m unittest discover -s tests/unit -p "test_*.py" -v 2>&1 | grep -c "ok$"

# Show test names only
python3 -m unittest discover -s tests/unit -p "test_*.py" -v 2>&1 | grep "^test_"

# Summary
python3 -m unittest discover -s tests/unit -p "test_*.py" 2>&1 | tail -3
```
