---
id: CL-0194-coverage-threshold-enforcement
title: Coverage Threshold Enforcement in CI
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
  - CL-0190-tdd-foundation-and-testing-stack
  - CL-0191-coverage-enforcement-and-tdd-parity
  - CL-0192-phase1-tdd-test-suite-completion
supersedes: []
superseded_by: []
tags:
  - testing
  - coverage
  - ci
  - enforcement
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0194: Coverage Threshold Enforcement in CI

**Date:** 2026-01-26
**Author:** platform-team + Claude Opus 4.5
**Branch:** feature/tdd-foundation (infra), development (backstage)

## Summary

Implemented blocking coverage threshold enforcement in CI for both repositories.
This completes Phase 2 of the TDD adoption plan by making coverage gates mandatory,
not advisory.

## Changes

### Infra Repository (goldenpath-idp-infra)

Updated `.github/workflows/python-tests.yml`:

```yaml
pytest tests/ \
  --cov=scripts \
  --cov-fail-under=60 \  # Increased from 50%
  ...
```

| Metric | Previous | New | V1.1 Target |
|--------|----------|-----|-------------|
| Threshold | 50% | **60%** | 70% |
| Status | Blocking | Blocking | Blocking |

### Backstage Repository (goldenpath-idp-backstage)

Updated `.github/workflows/ci.yml`:

```yaml
yarn test --coverage \
  --coverageThreshold='{"global":{"branches":30,"functions":30,"lines":30,"statements":30}}' \
  ...
```

| Metric | Previous | New | V1.1 Target |
|--------|----------|-----|-------------|
| Threshold | None | **30%** | 50% |
| Status | Non-blocking | Blocking | Blocking |

## Rationale

### Why 60% for Python (infra)?

- V1 target from TDD adoption plan
- 166 tests now exist covering core parsers
- Achievable without heroic effort
- Room to grow to 70% in V1.1

### Why 30% for Backstage?

- Backstage has minimal custom code (mostly plugin imports)
- 16 new tests cover custom Root components and APIs
- Higher threshold would require testing Backstage framework code
- Will increase as custom components are added

## Files Modified

| File | Change |
|------|--------|
| `.github/workflows/python-tests.yml` | Increased `--cov-fail-under` to 60% |
| `goldenpath-idp-backstage/.github/workflows/ci.yml` | Added `--coverageThreshold` at 30% |

## CI Behavior

| Repo | Trigger | Gate |
|------|---------|------|
| Infra | PR/push with Python changes | Coverage < 60% = FAIL |
| Backstage | PR/push | Coverage < 30% = FAIL |

## Validation

```bash
# Infra: verify coverage enforcement
$ pytest tests/ --cov=scripts --cov-fail-under=60
# Passes if coverage >= 60%

# Backstage: verify coverage enforcement
$ yarn test --coverage \
    --coverageThreshold='{"global":{"lines":30}}'
# Passes if coverage >= 30%
```

## Impact

Quality gates are now **actually gates**:

| Gate | Status |
|------|--------|
| Python tests pass | Blocking |
| Python coverage >= 60% | Blocking |
| Backstage tests pass | Blocking |
| Backstage coverage >= 30% | Blocking |
| Contract validation | Blocking |
| Schema validation | Blocking |

## Related

- Session capture: `session_capture/2026-01-26-tdd-foundation-and-testing-stack.md`
- TDD Plan: `.claude/plans/sleepy-pondering-turing.md`
