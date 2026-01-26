---
id: session-2026-01-26-tdd-foundation-and-testing-stack
title: TDD Foundation and Testing Stack Implementation
type: session-capture
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0182-tdd-philosophy
  - GOV-0016-testing-stack-matrix
  - GOV-0015-build-pipeline-testing-matrix
  - EC-0014-agent-scope-registry
---

# Session Capture: TDD Foundation and Testing Stack Implementation

## Session Metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-26
**Timestamp:** 2026-01-26T12:00:00Z
**Branch:** feature/tdd-foundation
**PR:** #282

## Scope

- Adopt Test-Driven Development philosophy for platform and Backstage
- Create comprehensive testing stack matrix (GOV-0016)
- Implement TDD enforcement via CI workflow
- Add pre-commit hooks for Python and Shell linting
- Document tool choices with rationale

## Context

This session was a continuation from a previous conversation covering:
- V1 readiness assessment (90.4% reported, ~65% realistic)
- Agent scope registry design (EC-0014)
- Build pipeline security gaps (Chainguard, Trivy, SBOM)
- CI optimization opportunities

The user requested adoption of TDD philosophy to preserve determinism and enable confident iteration.

## Work Summary

### 1. Testing Stack Analysis

Evaluated tools for each language layer:

| Layer | Test Framework | Linter | Formatter | Type Checker |
|-------|----------------|--------|-----------|--------------|
| **Python** | pytest | ruff | ruff | mypy (V2) |
| **Shell** | bats-core | shellcheck | shfmt | - |
| **Terraform** | terraform test | tflint | terraform fmt | - |
| **TypeScript** | Jest | ESLint | Prettier | tsc |
| **K8s YAML** | kuttl (V2) | kubeconform | yamllint | - |

### 2. Tool Decisions

**ruff over flake8/black/isort:**
- 10-100x faster (written in Rust)
- Single tool replaces multiple
- Black-compatible formatting
- 800+ lint rules

**bats-core for Shell:**
- Bash Automated Testing System
- TAP output format
- Simple assertion helpers

**tox deferred to V2:**
- Multi-environment testing
- Different Python versions
- Different dependency sets
- Requires solid pytest foundation first

**mypy deferred to V2:**
- Requires type hints in code
- Add after ruff adoption stabilizes

### 3. Backlog Created

Comprehensive backlog with 22+ items across priorities:

| Priority | Example Items |
|----------|---------------|
| **P0** | Fix CI IAM permissions |
| **P1** | TDD gate, shellcheck, ruff, Backstage CI blocking |
| **P2** | Coverage enforcement, Terraform tests, Trivy, Dependabot |
| **P3** | Chainguard, SBOM, kuttl |
| **V2** | tox, mypy |
| **V1.1** | Cosign, OWASP ZAP |

### 4. Honest Assessment

User asked for honest evaluation of the project:

**Portfolio Piece:** Exceptional - shows senior/staff-level platform engineering

**Product:** Not yet - missing:
- Real test coverage (~5% in Backstage)
- Security scanning (defined but not implemented)
- CI gates (continue-on-error everywhere)
- Production workloads (only hello-goldenpath-idp)

**AI-Human Collaboration:** Key differentiator
- Session capture pattern
- Agent merge guard
- Scoped agent roles (EC-0014)
- Co-Authored-By attribution

### 5. V1 Realistic Readiness

| Category | Weight | Score |
|----------|--------|-------|
| Governance/Docs | 30% | 95% |
| Infrastructure | 25% | 85% |
| CI/CD | 20% | 40% |
| Security | 15% | 30% |
| Testing | 10% | 10% |
| **Weighted Total** | | **~65%** |

## Artifacts Created

### New Files

| File | Purpose |
|------|---------|
| `docs/adrs/ADR-0182-tdd-philosophy.md` | TDD mandate, coverage targets, enforcement |
| `docs/10-governance/policies/GOV-0016-testing-stack-matrix.md` | Standard tools for each layer |
| `.github/workflows/tdd-gate.yml` | PR gate requiring tests |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/bats/helpers/common.bash` | Shared bats helpers |
| `tests/bats/test_example.bats` | Example bats test |
| `docs/extend-capabilities/EC-0014-agent-scope-registry.md` | Agent role scoping |
| `.github/workflows/determinism-guard.yml` | Blast radius + critical path enforcement |
| `docs/80-onboarding/27_TESTING_QUICKSTART.md` | 5-minute testing setup guide |

### Modified Files

| File | Change |
|------|--------|
| `.pre-commit-config.yaml` | Added ruff, shellcheck, shfmt hooks |
| `PLATFORM_HEALTH.md` | Regenerated |
| `Makefile` | Added test, test-python, test-shell, validate-schemas, lint |
| `docs/80-onboarding/24_PR_GATES.md` | Added TDD Gate and Determinism Guard |
| `docs/80-onboarding/25_DAY_ONE_CHECKLIST.md` | Added testing to first-day steps |
| `docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md` | Added TDD requirements (section 4a) |
| `docs/80-onboarding/AGENT_FIRST_BOOT.md` | Added TDD protocol |

## Key Discussions

### Testing Frameworks Explained

**pytest:** Python unit/integration testing with fixtures
**bats-core:** Bash Automated Testing System
**Jest:** JavaScript/TypeScript testing
**Playwright:** Cross-browser E2E testing
**terraform test:** Native Terraform module testing
**kubeconform:** K8s manifest validation (replaces deprecated kubeval)
**kuttl:** Kubernetes Test TooL for E2E

### Security Tools Explained

**OWASP ZAP:** Dynamic Application Security Testing (DAST) - tests running apps
**Trivy:** Container image vulnerability scanning
**Syft:** SBOM generation
**Cosign:** Image signing
**Gitleaks:** Secret detection in code

### Python Tools Explained

**ruff:** Ultra-fast linter + formatter (replaces flake8/black/isort)
**mypy:** Static type checker (requires type hints)
**tox:** Multi-environment test orchestrator
**Pydantic:** Data validation (not adopted - wrong fit for this stack)

### CI/CD Gaps Identified

1. Duplicate builds between ci.yml and build-push-ecr.yml
2. No concurrency control
3. `continue-on-error: true` disables gates
4. No path filtering (runs on docs-only changes)
5. No timeout limits
6. Reports are console-only (no JUnit XML in infra repo)

## Validation

- [x] Pre-commit config syntax valid
- [x] TDD gate workflow syntax valid
- [x] pytest conftest.py imports work
- [x] bats helpers syntax valid
- [ ] Full pre-commit run (pending merge)
- [ ] TDD gate blocks test-less PR (pending CI run)

## Current State / Follow-ups

### Current State

- TDD foundation implemented in infra repo
- PR #282 open for review
- Backstage repo changes pending (separate PR needed)

### Immediate Next Steps

| Priority | Action |
|----------|--------|
| P1 | Merge PR #282 |
| P1 | Make Backstage CI blocking (remove continue-on-error) |
| P2 | Add coverage enforcement to python-tests.yml |
| P2 | Add Trivy scan to build-push-ecr.yml |

### V2 Roadmap

| Item | Purpose |
|------|---------|
| tox | Multi-Python-version testing |
| mypy | Static type checking |
| kuttl | K8s E2E testing |
| Mutation testing | Verify test quality |

## Commits

```
1b6dea1d docs: add testing quickstart and update onboarding docs with TDD
dd986a57 docs: update session capture with determinism guard
ab156acf feat: add determinism guard workflow and Makefile test targets
391d3132 docs: add EC-0014 Agent Scope Registry
64d4c06c chore: regenerate platform health report
3edbdd2e feat: implement TDD foundation for platform testing
```

## Lessons Learned

1. **Test infrastructure before tests**: Setting up fixtures/helpers first makes writing tests easier
2. **Tool consolidation**: ruff replacing 3+ tools reduces config complexity
3. **Honest assessment matters**: 90.4% vs 65% readiness shows metric gaps
4. **AI collaboration is differentiator**: Most projects don't govern AI contributions

## Related Sessions

- `2026-01-25-governance-metrics-v1-observability.md` - Previous session
- `2026-01-19-build-pipeline-architecture.md` - Pipeline design
- `2026-01-24-build-timing-capture-gap.md` - CI timing analysis

Signed: Claude Opus 4.5 (2026-01-26T12:00:00Z)
