---
id: CL-0190-tdd-foundation-and-testing-stack
title: TDD Foundation and Testing Stack Implementation
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
  - 24_PR_GATES
  - 25_DAY_ONE_CHECKLIST
  - 26_AI_AGENT_PROTOCOLS
  - 27_TESTING_QUICKSTART
  - AGENT_FIRST_BOOT
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

# CL-0190: TDD Foundation and Testing Stack Implementation

**Date:** 2026-01-26
**Author:** platform-team + Claude Opus 4.5
**Branch:** feature/tdd-foundation
**PR:** #282

## Summary

Adopted Test-Driven Development (TDD) as a core philosophy for the platform.
Implemented testing infrastructure, CI workflows, and comprehensive documentation
to enforce "No feature without a test. No merge without green."

## Changes

### New Governance Documents

| File | Purpose |
| --- | --- |
| `docs/adrs/ADR-0182-tdd-philosophy.md` | TDD mandate, coverage targets, enforcement policy |
| `docs/10-governance/policies/GOV-0016-testing-stack-matrix.md` | Standard testing tools for infra and Backstage |

### New CI Workflows

| Workflow | Purpose |
| --- | --- |
| `.github/workflows/tdd-gate.yml` | PR gate requiring test files for Python/Shell changes |
| `.github/workflows/determinism-guard.yml` | Blast radius check (>80 files), critical path tests, schema validation |

### New Testing Infrastructure

| File | Purpose |
| --- | --- |
| `tests/conftest.py` | Shared pytest fixtures (temp_dir, mock_aws, create_yaml_file, etc.) |
| `tests/bats/helpers/common.bash` | Shared bats helpers (assert_success, assert_contains, mock_command) |
| `tests/bats/test_example.bats` | Example bats test demonstrating helper usage |

### New Onboarding Documentation

| File | Purpose |
| --- | --- |
| `docs/80-onboarding/27_TESTING_QUICKSTART.md` | 5-minute testing setup guide |

### Updated Files

| File | Change |
| --- | --- |
| `.pre-commit-config.yaml` | Added ruff (Python linting/formatting), shellcheck, shfmt |
| `Makefile` | Added `test`, `test-python`, `test-shell`, `validate-schemas`, `lint` targets |
| `docs/80-onboarding/24_PR_GATES.md` | Added TDD Gate and Determinism Guard to gate table |
| `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md` | Added testing setup to first-day steps |
| `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md` | Added section 4a) TDD requirements |
| `docs/80-onboarding/AGENT_FIRST_BOOT.md` | Added TDD protocol under Execution Protocols |
| `docs/extend-capabilities/EC-0014-agent-scope-registry.md` | Agent role scoping (related work) |
| `tests/scripts/test_script_0035.py` | Fixed stale test assertions for rds_provision |

## Testing Stack Matrix

### Infrastructure (goldenpath-idp-infra)

| Layer | Framework | Linter | Formatter |
| --- | --- | --- | --- |
| Python | pytest | ruff | ruff |
| Shell | bats-core | shellcheck | shfmt |
| Terraform | terraform test (V2) | tflint | terraform fmt |
| YAML | yamllint | kubeconform | - |

### Application (goldenpath-idp-backstage)

| Layer | Framework | Linter | Formatter |
| --- | --- | --- | --- |
| TypeScript | Jest | ESLint | Prettier |
| E2E | Playwright | - | - |

## Coverage Targets

| Layer | V1 Target | V1.1 Target |
| --- | --- | --- |
| Python scripts | 60% | 80% |
| Shell scripts | 40% | 60% |
| Backstage | 50% | 70% |

## Makefile Targets

```bash
make test              # Run all tests (Python + Shell)
make test-python       # Run pytest
make test-shell        # Run bats
make validate-schemas  # Validate YAML schemas
make lint              # Run all pre-commit hooks
```

## CI Behavior

| Trigger | Action |
| --- | --- |
| PR with `.py`/`.sh` changes | TDD Gate checks for corresponding test file |
| PR with >80 files | Determinism Guard requires `blast-radius-approved` label |
| PR touching critical paths | Determinism Guard runs pytest + bats |
| PR touching `schemas/` | Determinism Guard validates YAML schemas |

## Migration Notes

- No breaking changes
- Existing tests continue to work
- New PRs with Python/Shell changes will require test files
- Use `SKIP-TDD:reason` in PR description for exceptional cases (requires approval)

## Validation

- [x] All 87 pytest tests pass (2.5s runtime)
- [x] Pre-commit hooks install and run
- [x] TDD gate workflow syntax valid
- [x] Determinism guard workflow syntax valid
- [x] Onboarding docs link correctly

## Related

- Session capture: `session_capture/2026-01-26-tdd-foundation-and-testing-stack.md`
- Previous session: Governance metrics and V1 readiness assessment
