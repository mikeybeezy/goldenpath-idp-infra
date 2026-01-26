# Golden Output Tests

**Purpose:** Tier 2 tests that assert generated outputs match known-good snapshots.

> "Golden output tests are the primary guardrail against agent helpfulness."
> — GOV-0017

---

## When to Use Golden Tests

Use golden tests for any code that **generates files or structured output**:

| Generator Type | Example | Golden File |
|----------------|---------|-------------|
| Doc scaffolds | `scaffold_doc.py` | `expected/adr-scaffold.md` |
| Config generators | `generate_tfvars.py` | `expected/dev.tfvars` |
| Template renderers | Jinja2, Helm | `expected/rendered-manifest.yaml` |
| Parser outputs | `secret_request_parser.py` | `expected/parsed-request.json` |

---

## Directory Structure

```
tests/golden/
├── README.md                      # This file
├── conftest.py                    # Golden test fixtures
├── test_scaffold_outputs.py       # Scaffold generator tests
├── test_parser_outputs.py         # Parser output tests
└── fixtures/
    ├── inputs/                    # Test input files
    │   ├── secret-request.yaml
    │   └── adr-params.json
    └── expected/                  # Golden snapshots
        ├── adr-scaffold.md
        └── parsed-secret.json
```

---

## Writing a Golden Test

```python
from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"

def test_scaffold_doc_matches_golden():
    """Assert scaffold_doc output matches golden snapshot."""
    from scripts.scaffold_doc import scaffold_doc

    # Generate output
    result = scaffold_doc(doc_type="adr", title="test-decision")

    # Load golden file
    golden = (FIXTURES / "expected" / "adr-scaffold.md").read_text()

    # Assert exact match
    assert result == golden, "Output differs from golden file. Run update protocol if intentional."
```

---

## Updating Golden Files

Golden files are **immutable by default**. To update:

1. **Verify the change is intentional** — review the diff
2. **Get human approval** — AI agents cannot update golden files alone
3. **Run the update command:**
   ```bash
   pytest tests/golden/ --update-golden
   ```
4. **Document the change** — PR description must explain why output changed

---

## CI Enforcement

Golden tests run as part of the Determinism Guard workflow when critical paths are touched:
- `scripts/scaffold_doc.py`
- `scripts/*_parser.py`
- `scripts/*_generator.py`

Failures block merge until resolved.

---

## Related

- [GOV-0017: TDD and Determinism](../../docs/10-governance/policies/GOV-0017-tdd-and-determinism.md)
- [ADR-0162: Determinism Protection](../../docs/adrs/ADR-0162-determinism-protection.md)
