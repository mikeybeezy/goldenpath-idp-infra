---
id: CL-0191-coverage-enforcement-and-tdd-parity
title: Coverage Enforcement and TDD Parity with Backstage
type: changelog
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - ADR-0182-tdd-philosophy
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
  - CL-0190-tdd-foundation-and-testing-stack
  - EC-0015-backstage-tdd-parity-plan
  - EC-0016-bespoke-schema-validator
supersedes: []
superseded_by: []
tags:
  - testing
  - tdd
  - coverage
  - parity
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0191: Coverage Enforcement and TDD Parity with Backstage

**Date:** 2026-01-26
**Author:** platform-team + Claude Opus 4.5
**Branch:** feature/development-branch-protection

## Summary

Added coverage enforcement to infra CI pipeline and verified TDD gate parity between
goldenpath-idp-infra and goldenpath-idp-backstage repos. Documented architectural
decision to keep bespoke schema format.

## Changes

### Coverage Enforcement Added

Updated `.github/workflows/python-tests.yml` to enforce 50% minimum coverage:

```yaml
pytest tests/ \
  --cov=scripts \
  --cov-report=xml:coverage/coverage.xml \
  --cov-report=html:coverage/html \
  --cov-report=term-missing \
  --cov-fail-under=50 \
  ...
```

| Target | V1 (Current) | V1.1 (Future) |
|--------|--------------|---------------|
| Coverage threshold | 50% | 70% |

### TDD Gate Verification

Confirmed infra already has TDD gate workflow (`.github/workflows/tdd-gate.yml`) with:
- Python test file detection (`tests/unit/test_<name>.py`)
- Shell test file detection (`tests/bats/test_<name>.bats`)
- SKIP-TDD bypass mechanism
- PR comment on failure

### Parity Assessment

| Capability | Infra | Backstage | Status |
|------------|-------|-----------|--------|
| TDD gate workflow | ✅ | ✅ | Parity |
| Test integrity guard | ✅ | ✅ | Parity |
| Coverage enforcement | ✅ 50% | ✅ 30% | Infra higher |
| Test count | 108 | 2 | Gap |
| Golden tests | ✅ | ❌ | Gap |
| Contract tests | ⚠️ | ❌ | Gap |

### Architectural Decision: Bespoke Schema Format

Documented decision to keep custom schema format rather than convert to JSON Schema:

- Custom format captures business rules (`conditional_rules`, `approval_routing`)
- Being opinionated is a feature, not a bug
- Created EC-0016 for custom schema validator

## Files Modified

| File | Change |
|------|--------|
| `.github/workflows/python-tests.yml` | Added coverage enforcement (50% threshold) |
| `docs/extend-capabilities/EC-0016-bespoke-schema-validator.md` | Created custom validator proposal |
| `session_capture/2026-01-26-session-capture-tdd-quality-gate.md` | Updated with architectural decisions |

## Testing

```bash
# Verify coverage enforcement
$ make test-python
# CI will fail if coverage < 50%

# Verify TDD gate
$ # Push PR with .py file without test
# TDD gate will fail
```

## Related Work

- **EC-0015**: Backstage TDD Parity Plan (ongoing)
- **EC-0016**: Bespoke Schema Validator (proposed)
- **CL-0190**: TDD Foundation (prior work)

## Next Steps

1. Write more tests to increase coverage
2. Implement custom schema validator (EC-0016)
3. Add golden test infrastructure to Backstage
4. Remove `continue-on-error` from Backstage security audit in V1.1
