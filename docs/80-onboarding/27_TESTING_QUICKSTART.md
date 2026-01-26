---
id: 27_TESTING_QUICKSTART
title: Testing Quickstart Guide
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - 00_DOC_INDEX
  - 24_PR_GATES
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - ADR-0182-tdd-philosophy
  - GOV-0016-testing-stack-matrix
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Testing Quickstart Guide

Doc contract:

- Purpose: Get contributors running tests locally within 5 minutes.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/adrs/ADR-0182-tdd-philosophy.md, docs/10-governance/policies/GOV-0016-testing-stack-matrix.md

This guide helps you set up and run the testing stack for GoldenPath IDP.
All code changes require tests per ADR-0182.

## TDD Philosophy

> **"No feature without a test. No merge without green."**

Tests are executable contracts that define expected behavior before
implementation. See [ADR-0182](../adrs/ADR-0182-tdd-philosophy.md) for the
full philosophy.

## Quick Setup (5 minutes)

### 1. Install dependencies

```bash
# Python testing tools
pip install pytest pytest-cov pyyaml

# Shell testing tools (macOS)
brew install bats-core

# Shell testing tools (Ubuntu/Debian)
sudo apt-get install bats

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### 2. Verify installation

```bash
# Check tools are available
pytest --version
bats --version
pre-commit --version
```

### 3. Run all tests

```bash
make test
```

## Test Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests (Python + Shell) |
| `make test-python` | Run Python tests with pytest |
| `make test-shell` | Run Shell tests with bats |
| `make validate-schemas` | Validate YAML schemas |
| `make lint` | Run all linters via pre-commit |

## Running Tests Directly

### Python Tests (pytest)

```bash
# Run all Python tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test file
pytest tests/unit/test_specific.py

# Run tests matching pattern
pytest tests/ -k "test_metadata"
```

### Shell Tests (bats)

```bash
# Run all bats tests
bats tests/bats/*.bats

# Run specific test file
bats tests/bats/test_example.bats

# Run with verbose output
bats tests/bats/*.bats --verbose-run
```

## Test Structure

```text
tests/
  conftest.py           # Shared pytest fixtures (auto-loaded)
  unit/
    test_*.py           # Python unit tests
  integration/
    test_*.py           # Python integration tests
  bats/
    helpers/
      common.bash       # Shared bats helpers
    test_*.bats         # Shell tests
```

## Writing Tests

### Python Test Template

```python
"""Tests for my_module."""

import pytest
from scripts.my_module import my_function


class TestMyFunction:
    """Tests for my_function."""

    def test_returns_expected_value(self):
        """Test that my_function returns expected output."""
        result = my_function("input")
        assert result == "expected"

    def test_handles_edge_case(self):
        """Test edge case handling."""
        result = my_function("")
        assert result is None

    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that requires more time (skipped by default)."""
        # Run with: pytest --runslow
        result = expensive_operation()
        assert result.success
```

### Shell Test Template

```bash
#!/usr/bin/env bats

load 'helpers/common'

setup() {
  export TEST_TEMP_DIR=$(mktemp -d)
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

@test "my_script: returns success on valid input" {
  run bash scripts/my_script.sh --valid
  assert_success
}

@test "my_script: outputs expected message" {
  run bash scripts/my_script.sh --help
  assert_success
  assert_output_contains "Usage:"
}

@test "my_script: fails on invalid input" {
  run bash scripts/my_script.sh --invalid
  assert_failure
}
```

## Using Fixtures

The `tests/conftest.py` provides shared fixtures:

```python
def test_with_temp_dir(temp_dir):
    """temp_dir is auto-cleaned after test."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("hello")
    assert test_file.exists()


def test_with_yaml_file(create_yaml_file):
    """Factory fixture for creating YAML files."""
    yaml_file = create_yaml_file("config.yaml", {"key": "value"})
    assert yaml_file.exists()


def test_with_mock_aws(mock_aws_credentials):
    """AWS credentials are mocked for this test."""
    # AWS_ACCESS_KEY_ID etc. are set to "testing"
    pass
```

Available fixtures:

| Fixture | Description |
|---------|-------------|
| `project_root` | Path to project root |
| `scripts_dir` | Path to scripts/ |
| `temp_dir` | Auto-cleaned temporary directory |
| `temp_file` | Auto-cleaned temporary file |
| `sample_yaml_content` | Sample YAML string |
| `sample_frontmatter` | Sample frontmatter dict |
| `mock_aws_credentials` | Mocked AWS credentials |
| `mock_github_env` | Mocked GitHub Actions env |
| `create_yaml_file` | Factory for YAML files |
| `create_markdown_file` | Factory for MD files |

## CI Workflows

### TDD Gate (`tdd-gate.yml`)

Ensures every Python/Shell change has a corresponding test file.

**Triggered by:** PRs modifying `.py`, `.sh` files

**Bypass:** Add `SKIP-TDD:reason` to PR description for exceptional cases.

### Determinism Guard (`determinism-guard.yml`)

Protects against large or dangerous changes.

**Features:**

- Blast radius check (>80 files requires `blast-radius-approved` label)
- Critical path detection (modules/, scripts/, bootstrap/, workflows)
- Schema validation for YAML schemas
- Test execution for critical path changes

## Coverage Targets

| Layer | V1 Target | V1.1 Target |
|-------|-----------|-------------|
| Python scripts | 60% | 80% |
| Shell scripts | 40% | 60% |
| Backstage | 50% | 70% |

## Troubleshooting

### pytest not found

```bash
pip install pytest
# or if using virtual env
source venv/bin/activate && pip install pytest
```

### bats not found

```bash
# macOS
brew install bats-core

# Ubuntu/Debian
sudo apt-get install bats

# From source
git clone https://github.com/bats-core/bats-core.git
cd bats-core && ./install.sh /usr/local
```

### Tests pass locally but fail in CI

1. Check Python version matches CI (3.11)
2. Ensure all dependencies are in `requirements.txt`
3. Check for environment-specific paths or credentials

### Pre-commit hooks not running

```bash
pre-commit install
pre-commit run --all-files  # Verify hooks work
```

## Related Documentation

- [TDD Philosophy (ADR-0182)](../adrs/ADR-0182-tdd-philosophy.md)
- [Testing Stack Matrix (GOV-0016)](../10-governance/policies/GOV-0016-testing-stack-matrix.md)
- [PR Gates](./24_PR_GATES.md)
- [AI Agent Protocols](./26_AI_AGENT_PROTOCOLS.md)
