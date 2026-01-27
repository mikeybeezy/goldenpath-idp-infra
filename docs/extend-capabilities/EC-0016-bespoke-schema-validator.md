---
id: EC-0016-bespoke-schema-validator
title: Bespoke Schema Validator for Contract Validation
type: extension-capability
status: proposed
relates_to:
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - ADR-0170
  - EC-0002-shared-parser-library
dependencies:
  - Stable schema format definition
  - At least one parser using standard CLI contract
priority: medium
vq_class: 🟢 HV/HQ
estimated_roi: Enables contract validation for all request types
effort_estimate: 3-5 days
---

## Bespoke Schema Validator for Contract Validation

This document proposes building a custom schema validator that understands the GoldenPath bespoke schema format, enabling contract validation in CI.

**Status**: Proposed - Architectural decision made to keep bespoke format.

## Executive Summary

The GoldenPath IDP uses a bespoke schema format that extends beyond standard JSON Schema to capture business rules, approval routing, and platform opinions. Standard tools like `check-jsonschema` cannot validate against these schemas.

Building a custom validator will:

- **Enable Contract Validation**: Validate request fixtures against full schema (structure + business rules)
- **Preserve Platform Opinions**: Keep expressive schema format rather than dumbing down to JSON Schema
- **Unify Validation**: Single validator for CI, parsers, and Backstage templates
- **Support TDD**: Enable `make validate-contracts` to actually validate

## Problem Statement

Current state:

1. Schemas use bespoke format with `conditional_rules`, `approval_routing`, `enum_from`, etc.
2. `check-jsonschema` fails on these schemas (expects pure JSON Schema)
3. `make validate-contracts` currently skips validation with a warning
4. No automated validation of request fixtures against business rules

## Architectural Decision

**Decision**: Keep the bespoke schema format. Being opinionated is a feature, not a bug.

| Capability | JSON Schema | Our Bespoke Format |
| ---------- | ----------- | ------------------ |
| Structure validation | Yes | Yes |
| Conditional business rules | Limited `if/then` | `conditional_rules` |
| Approval routing logic | No | `approval_routing` |
| Purpose-based defaults | No | `purpose_defaults` |
| Output artifact mapping | No | `generates` |
| External enum references | No | `enum_from` |

Converting to JSON Schema would lose expressiveness. Instead, build tooling that understands our format.

## Proposed Solution

### New Script: `scripts/validate_request.py`

```python
#!/usr/bin/env python3
"""
Validate request fixtures against bespoke GoldenPath schemas.

Supports:
- Structure validation (type, pattern, enum, required)
- enum_from references (loads from schemas/metadata/enums.yaml)
- conditional_rules evaluation
- Detailed error reporting

Usage:
    python3 scripts/validate_request.py \
        --schema schemas/requests/s3.schema.yaml \
        --request tests/golden/fixtures/inputs/S3-0001.yaml

    python3 scripts/validate_request.py \
        --schema-dir schemas/requests \
        --request-dir tests/golden/fixtures/inputs \
        --auto-match  # Match S3-*.yaml to s3.schema.yaml
"""
```

### Validation Capabilities

1. **Structure Validation**
   - `type`: string, integer, boolean, object, array
   - `pattern`: regex validation
   - `enum`: allowed values
   - `required`: field presence
   - `minLength`, `maxLength`, `minimum`, `maximum`

2. **Enum References**
   - Load enums from `schemas/metadata/enums.yaml`
   - Resolve `enum_from: owners` to actual values
   - Error if enum not found

3. **Conditional Rules**
   - Evaluate `when` conditions
   - Check `then` requirements
   - Produce actionable error messages

4. **Error Reporting**
   - JSON output for CI parsing
   - Human-readable summary
   - Line numbers where possible

### Makefile Integration

```makefile
# Replace check-jsonschema with custom validator
validate-contracts:
    @echo "Validating request fixtures against schemas..."
    @python3 scripts/validate_request.py \
        --schema-dir schemas/requests \
        --request-dir tests/golden/fixtures/inputs \
        --auto-match \
        --output json > test-results/contract-validation.json
    @echo "OK: all contracts valid"
```

### Directory Structure

```
scripts/
  validate_request.py          # Main validator script
  lib/
    schema_validator.py        # Core validation logic
    enum_resolver.py           # enum_from resolution
    conditional_evaluator.py   # conditional_rules evaluation
tests/
  unit/
    test_schema_validator.py   # Unit tests for validator
```

## Implementation Plan

### Phase 1: Structure Validation (2 days)

1. Parse bespoke schema YAML
2. Validate basic structure (type, pattern, enum, required)
3. Handle nested objects and arrays
4. Unit tests for each validation type

### Phase 2: Enum Resolution (1 day)

1. Load `schemas/metadata/enums.yaml`
2. Resolve `enum_from` references
3. Cache loaded enums
4. Error on missing enum

### Phase 3: Conditional Rules (1-2 days)

1. Parse `conditional_rules` section
2. Evaluate `when` conditions
3. Check `then` requirements
4. Produce actionable errors

### Phase 4: Integration (0.5 days)

1. Update Makefile `validate-contracts` target
2. Add to `quality-gate` pipeline
3. CI integration

## Success Criteria

- [ ] `make validate-contracts` validates all fixtures
- [ ] S3, EKS, RDS, SECRET requests validated against schemas
- [ ] Conditional rules enforced (e.g., prod requires KMS)
- [ ] Clear error messages for validation failures
- [ ] Unit test coverage > 80%

## Alternatives Considered

| Alternative | Why Not |
| ----------- | ------- |
| Convert to JSON Schema | Loses business rules, approval routing |
| Split into JSON Schema + rules | Extra complexity, two files to maintain |
| Use JSON Schema + custom validator for rules | Partial solution, still need custom code |

## References

- Session Capture: 2026-01-26-session-capture-tdd-quality-gate.md
- GOV-0016: Testing Stack Matrix
- GOV-0017: TDD and Determinism
- EC-0002: Shared Parser Library (related refactoring)

---

## Appendix A: Parser CLI Updates for Golden Test Compatibility

### Current Parser Interfaces vs Standard Contract

| Parser | Current Interface | Standard Contract Required |
| ------ | ----------------- | -------------------------- |
| **S3** | `--mode`, `--input-files`, `--output-root`, `--dry-run` | `--request`, `--out`, `--format stable`, `--dry-run` |
| **Secret** | `--mode`, `--input-files`, `--enums`, `--tfvars-out-root` | `--request`, `--out`, `--format stable`, `--dry-run` |
| **RDS** | `--mode`, `--input-files`, `--enums`, `--tfvars-out-root` | `--request`, `--out`, `--format stable`, `--dry-run` |
| **EKS** | `--mode`, `--input-files`, `--enums`, `--tfvars-out-root` | `--request`, `--out`, `--format stable`, `--dry-run` |

### Gap Analysis

**What needs to change for each parser:**

1. **Rename arguments:**
   - `--input-files` → `--request` (single file for golden test simplicity)
   - `--output-root` / `--tfvars-out-root` → `--out`

2. **Add `--format stable`:**
   - Sorts keys alphabetically in JSON/YAML output
   - Uses consistent timestamp formatting (or omits timestamps)
   - Removes non-deterministic elements (random IDs, timestamps)
   - Enables byte-exact comparison in golden tests

3. **Implicit enum loading:**
   - Currently: `--enums schemas/metadata/enums.yaml` required
   - Desired: Auto-detect from repo structure or default path

4. **Keep backward compatibility:**
   - Support both old and new interfaces during transition
   - Deprecation warnings for old arguments

### Implementation Effort

| Task | Effort |
| ---- | ------ |
| Add argument aliases (`--request`, `--out`) | 0.5 day |
| Implement `--format stable` (deterministic output) | 1 day |
| Auto-detect enum path | 0.5 day |
| Update 4 parsers | 2 days total |
| Update golden test infrastructure | 0.5 day |

---

## Appendix B: Current Test Coverage Analysis

### Test Breakdown (108 Tests)

#### By Test Type

| Category | Tests | Files |
| -------- | ----- | ----- |
| **Unit tests** | ~45 | `tests/unit/*.py` |
| **Script tests** | ~50 | `tests/scripts/*.py` |
| **Golden tests** | 6 | `tests/golden/*.py` |
| **Contract tests** | 8 | `tests/contract/*.py` |

#### By Script Coverage

| Script ID | Script Name | Tests | Coverage |
| --------- | ----------- | ----- | -------- |
| SCRIPT-0034 | `rds_request_parser.py` | 16 | Full flow tested |
| SCRIPT-0035 | `provision_rds_users.py` | 22 | Including integration |
| SCRIPT-0037 | `s3_request_parser.py` | 24 | Most comprehensive |
| SCRIPT-0026 | `secret_request_parser.py` | 3 | Basic coverage |
| N/A | `validate_metadata.py` | 6 | Good coverage |
| N/A | `standardize_metadata.py` | 3 | Basic coverage |
| N/A | `inject_script_metadata.py` | 3 | Basic coverage |
| N/A | `vq_logger.py` | 3 | Basic coverage |
| N/A | Script imports | 4 | Import validation |

#### Test Quality Distribution

| Quality Level | Count | Characteristics |
| ------------- | ----- | --------------- |
| **Comprehensive** | ~40 | Full scenarios, edge cases, error paths |
| **Basic** | ~50 | Happy path, minimal edge cases |
| **Infrastructure** | ~18 | Test framework validation, imports |

---

## Appendix C: What's Working

### CI Pipeline (Automated)

- **Python tests run on every PR** targeting main/development
- **Coverage measured** (50% threshold enforced)
- **Test proofs generated** from junit.xml
- **Artifacts uploaded** (coverage reports, proofs)

### Test Infrastructure

- **pytest fixtures** in `tests/conftest.py` - shared setup
- **Golden test fixtures** in `tests/golden/conftest.py` - comparison helpers
- **Template tests** for new scripts in `tests/templates/`

### Validated Parsers

| Parser | Validated By | Status |
| ------ | ------------ | ------ |
| S3 | 24 tests (test_script_0037.py) | Comprehensive |
| RDS | 16 tests (test_script_0034.py) | Good |
| Secret | 3 unit + 8 contract tests | Basic |
| EKS | Import test only | Minimal |

### Quality Gates

- `make validate-schemas` - YAML syntax + JSON Schema validation
- `make test` - pytest execution with coverage
- `make quality-gate` - orchestrates all validators
- TDD gate workflow exists (requires tests for code changes)

---

## Appendix D: Identified Gaps

### Critical Gaps (P1)

| Gap | Impact | Fix |
| --- | ------ | --- |
| **EKS parser has no tests** | No regression safety | Write test_script_XXXX.py for EKS |
| **Golden tests don't run actual parsers** | Tests are placeholders | Update parsers to support standard CLI |
| **validate-contracts skips SECRET** | Schema validation incomplete | Build bespoke validator (this EC) |

### Medium Gaps (P2)

| Gap | Impact | Fix |
| --- | ------ | --- |
| **No shell script tests** | Bash scripts untested | Add bats-core infrastructure |
| **No Terraform tests** | Module regressions possible | Add `*.tftest.hcl` files |
| **Coverage at 50%** (not 70%) | Gaps in edge cases | Write more tests, raise threshold |

### Process Gaps

| Gap | Impact | Fix |
| --- | ------ | --- |
| **TDD gate not enforcing test creation** | Code can merge without tests | Verify TDD gate workflow is required check |
| **No mutation testing** | Tests may be weak | Consider adding mutmut/pytest-mutmut |
| **No load/performance tests** | Parser performance unknown | Out of scope for V1 |

---

## Appendix E: Target State Summary

| Area | Current State | Target V1 | Gap |
| ---- | ------------- | --------- | --- |
| **Test count** | 108 | 150+ | +42 tests |
| **Coverage** | 50% | 70% | +20% |
| **Parser CLI** | 4 variants | Standard contract | CLI refactor |
| **Golden tests** | Infrastructure only | Running parsers | Parser updates |
| **Shell tests** | 0 | 10+ | bats setup |
| **Terraform tests** | 0 | Per module | tftest files |
| **Bespoke validator** | Proposed (this EC) | Implemented | Build it |
