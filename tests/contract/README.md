# Contract Tests

**Purpose:** Tier 1 tests that verify input/output contracts for parsers and request handlers.

> "Contract tests define expected behavior at system boundaries."
> — GOV-0017

---

## When to Use Contract Tests

Use contract tests when code:
- Parses external input (YAML, JSON, CLI args)
- Produces structured output consumed by other systems
- Implements a schema-defined interface

| Component | Contract | Test Focus |
|-----------|----------|------------|
| `secret_request_parser.py` | YAML → SecretRequest | Schema compliance |
| `eks_build_parser.py` | YAML → EKSConfig | Required fields, defaults |
| `rds_provision.py` | Request → SQL commands | Output format |

---

## Directory Structure

```
tests/contract/
├── README.md                          # This file
├── conftest.py                        # Contract test fixtures
├── test_secret_request_contract.py    # Secret request parser
├── test_eks_request_contract.py       # EKS build parser
├── test_rds_request_contract.py       # RDS request parser
└── fixtures/
    └── requests/
        ├── valid/
        │   ├── secret-minimal.yaml
        │   └── secret-full.yaml
        └── invalid/
            ├── missing-required.yaml
            └── wrong-type.yaml
```

---

## Writing a Contract Test

```python
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "requests"

class TestSecretRequestContract:
    """Contract tests for secret request parser."""

    def test_minimal_request_parses(self):
        """Minimal valid request should parse without error."""
        from scripts.secret_request_parser import parse_request

        request = (FIXTURES / "valid" / "secret-minimal.yaml").read_text()
        result = parse_request(request)

        assert result.name is not None
        assert result.namespace is not None

    def test_full_request_preserves_all_fields(self):
        """Full request should preserve all specified fields."""
        from scripts.secret_request_parser import parse_request

        request = (FIXTURES / "valid" / "secret-full.yaml").read_text()
        result = parse_request(request)

        assert result.rotation_days == 90
        assert result.tags["environment"] == "dev"

    def test_missing_required_raises(self):
        """Missing required field should raise ValidationError."""
        from scripts.secret_request_parser import parse_request, ValidationError

        request = (FIXTURES / "invalid" / "missing-required.yaml").read_text()

        with pytest.raises(ValidationError):
            parse_request(request)
```

---

## Contract Test Patterns

### 1. Required Fields
```python
def test_required_field_present():
    result = parse(valid_input)
    assert result.required_field is not None
```

### 2. Default Values
```python
def test_default_applied_when_missing():
    result = parse(minimal_input)
    assert result.optional_field == "default_value"
```

### 3. Type Coercion
```python
def test_string_coerced_to_int():
    result = parse(input_with_string_number)
    assert isinstance(result.count, int)
```

### 4. Error Cases
```python
def test_invalid_input_raises_specific_error():
    with pytest.raises(ValidationError, match="field 'name' is required"):
        parse(invalid_input)
```

---

## CI Enforcement

Contract tests run on every PR that modifies:
- `scripts/*_parser.py`
- `scripts/*_request*.py`
- `schemas/*.yaml`

---

## Related

- [GOV-0017: TDD and Determinism](../../docs/10-governance/policies/GOV-0017-tdd-and-determinism.md)
- [tests/schemas/](../schemas/) — Schema validation tests
