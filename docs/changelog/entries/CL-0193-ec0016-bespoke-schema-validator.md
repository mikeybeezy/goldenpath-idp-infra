---
id: CL-0193-ec0016-bespoke-schema-validator
title: EC-0016 Bespoke Schema Validator Implementation
type: changelog
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - EC-0016-bespoke-schema-validator
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - CL-0191-coverage-enforcement-and-tdd-parity
supersedes: []
superseded_by: []
tags:
  - testing
  - validation
  - schema
  - contracts
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0193: EC-0016 Bespoke Schema Validator Implementation

**Date:** 2026-01-26
**Author:** platform-team + Claude Opus 4.5
**Branch:** feature/tdd-foundation

## Summary

Implemented the bespoke schema validator proposed in EC-0016. This validator understands
the GoldenPath custom schema format (conditional_rules, enum_from, approval_routing)
that standard JSON Schema tools cannot process.

## Problem Solved

Previously, `make validate-contracts` used `check-jsonschema` which:

1. Could not parse bespoke schemas (not pure JSON Schema)
2. Passed with zero validations (false-green)
3. Required JSON Schema conversion (would lose business rules)

## Solution

Created `scripts/validate_request.py` (SCRIPT-0058) with:

- **Type validation**: string, integer, boolean, object, array
- **Pattern validation**: regex patterns
- **Enum validation**: inline enums and `enum_from` references
- **Conditional rules**: evaluates `when`/`then` conditions
- **Nested objects**: validates nested properties and required fields
- **Auto-matching**: matches requests to schemas by prefix (S3-, EKS-, RDS-)

## Validation Capabilities

| Feature | Description |
|---------|-------------|
| `type` | Validates Python types match schema types |
| `pattern` | Regex validation for strings |
| `enum` | Inline allowed values |
| `enum_from` | References to `schemas/metadata/enums.yaml` |
| `required` | Field presence validation |
| `minimum`/`maximum` | Numeric constraints |
| `minLength`/`maxLength` | String length constraints |
| `conditional_rules` | Business logic (e.g., "prod requires KMS") |

## Files Created

| File | Purpose |
|------|---------|
| `scripts/validate_request.py` | Bespoke schema validator (570 lines) |
| `tests/scripts/test_validate_request.py` | 30 unit tests |
| `tests/golden/fixtures/inputs/S3-0001.yaml` | S3 request fixture for testing |

## Makefile Integration

Updated `validate-contracts` target:

```makefile
validate-contracts:
    python3 scripts/validate_request.py \
        --schema-dir schemas/requests \
        --request-dir tests/golden/fixtures/inputs \
        --enums schemas/metadata/enums.yaml \
        --auto-match
```

## Usage

```bash
# Validate all fixtures
$ make validate-contracts
✅ tests/golden/fixtures/inputs/S3-0001.yaml
ℹ️  Skipped 1 file(s) without bespoke schemas
OK: 1 request(s) validated successfully

# Validate single request
$ python3 scripts/validate_request.py \
    --schema schemas/requests/s3.schema.yaml \
    --request tests/golden/fixtures/inputs/S3-0001.yaml

# JSON output for CI
$ python3 scripts/validate_request.py \
    --schema-dir schemas/requests \
    --request-dir tests/golden/fixtures/inputs \
    --auto-match \
    --output json
```

## Prefix Handling

| Prefix | Schema | Status |
|--------|--------|--------|
| `S3-` | `s3.schema.yaml` | Validated |
| `EKS-` | `eks.schema.yaml` | Validated |
| `RDS-` | `rds.schema.yaml` | Validated |
| `SECRET-` | N/A | Skipped (no bespoke schema yet) |

## Codex Review Response

This implementation addresses Codex review findings:

| Finding | Resolution |
|---------|------------|
| False-green quality gate | Now validates or fails explicitly |
| `python` vs `python3` | Uses `python3` consistently |
| Doc drift on fixture names | Renamed to `SECRET-0001.yaml`, `S3-0001.yaml` |

## Validation

```bash
$ pytest tests/scripts/test_validate_request.py -v
30 passed in 0.35s

$ make validate-contracts
OK: 1 request(s) validated successfully
```

## Related

- EC-0016 proposal: `docs/extend-capabilities/EC-0016-bespoke-schema-validator.md`
- Session capture: `session_capture/2026-01-26-tdd-foundation-and-testing-stack.md`
