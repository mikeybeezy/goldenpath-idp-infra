---
id: PRD-0009
title: Integration Test Gap Closure
type: prd
status: draft
priority: P1
owner: platform-team
lifecycle: planning
created: 2026-01-29
relates_to:
  - GOV-0017-tdd-and-determinism
  - PRD-0008-governance-rag-pipeline
  - ADR-0182-tdd-philosophy
---

# PRD-0009: Integration Test Gap Closure

## Executive Summary

Both `goldenpath-idp-infra` and `goldenpath-idp-backstage` repositories have significant integration test gaps. While unit tests provide code correctness verification, they cannot validate that components work together correctly. This PRD tracks the gap and defines a closure plan.

## Problem Statement

### Current State

| Repository | Unit Tests | Integration Tests | Gap Severity |
|------------|-----------|-------------------|--------------|
| goldenpath-idp-infra | 194 tests (verified 2026-01-29 via `pytest -q tests/unit`) | 10 tests (new) | 🟠 HIGH |
| goldenpath-idp-backstage | 6 test files (unverified in this repo) | 1 e2e test (unverified in this repo) | 🔴 CRITICAL |

### Why This Matters

Unit tests verify: **"Does the code do what I wrote?"**
Integration tests verify: **"Do the components work together?"**

Without integration tests, we cannot catch:
- API contract mismatches
- Data flow errors between components
- State management issues
- Race conditions in workflows
- Configuration drift between environments

## Gap Analysis

### goldenpath-idp-infra

#### What Exists

| Category | Count | Status |
|----------|-------|--------|
| Unit tests (Tier 1) | 194 | ✅ Strong |
| Golden tests (Tier 2) | 12 | ✅ Adequate |
| Contract tests (Tier 2) | 8 | ✅ Adequate |
| Integration tests (Tier 3) | 10 | 🟡 Minimal (RAG only) |

#### Critical Workflows WITHOUT Integration Tests

| Workflow | Components | Priority | Effort |
|----------|------------|----------|--------|
| ECR Sync | parser → pusher → ECR | P1 | Medium |
| Secret Provisioning | request → AWS SDK → SSM | P1 | Medium |
| Registry Mirror | mirror config → validation | P2 | Low |
| Backstage Entity Sync | catalog → publish | P2 | Medium |
| AWS SSM Parameter Flow | param → encrypt → store | P2 | Low |

#### What Was Added (2026-01-29)

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/integration/test_rag_pipeline.py` | 10 | RAG: load → chunk → index → retrieve |

### goldenpath-idp-backstage

#### What Exists

| Category | Count | Status |
|----------|-------|--------|
| Unit tests | 6 files (234 lines) | 🟡 Partial |
| E2E tests | 1 file (27 lines) | 🔴 Minimal |
| Backend tests | 0 | 🔴 NONE |

#### Critical Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| Backend tests | 🔴 CRITICAL | 0% backend coverage |
| EntityPage.tsx | 🔴 CRITICAL | Catalog untested |
| SearchPage.tsx | 🔴 CRITICAL | Search untested |
| API integration | 🟠 HIGH | No backend-frontend tests |
| Auth flow | 🟠 HIGH | Login/logout untested |
| Plugin tests | 🟠 HIGH | No plugin coverage |

## Proposed Solution

### Phase 1: Foundation (Week 1-2)

#### goldenpath-idp-infra

1. **ECR Sync Integration Test**
   - File: `tests/integration/test_ecr_sync.py`
   - Mock: boto3 ECR client
   - Verify: Image sync workflow end-to-end

2. **Secret Provisioning Integration Test**
   - File: `tests/integration/test_secret_flow.py`
   - Mock: boto3 SSM client
   - Verify: Secret request → creation → retrieval

#### goldenpath-idp-backstage

1. **Backend Unit Tests**
   - File: `packages/backend/src/index.test.ts`
   - Cover: Server startup, plugin registration

2. **EntityPage Integration Test**
   - File: `packages/app/src/components/catalog/EntityPage.test.tsx`
   - Cover: Catalog browsing, entity display

### Phase 2: Coverage Expansion (Week 3-4)

#### goldenpath-idp-infra

3. **Registry Mirror Test**
   - File: `tests/integration/test_registry_mirror.py`

4. **AWS SSM Flow Test**
   - File: `tests/integration/test_ssm_flow.py`

#### goldenpath-idp-backstage

3. **SearchPage Integration Test**
   - File: `packages/app/src/components/search/SearchPage.test.tsx`

4. **API Integration Tests**
   - File: `packages/app/e2e-tests/api.test.ts`

### Phase 3: Quality Gates (Week 5-6)

1. **CI Enforcement**
   - Add `--runintegration` to nightly CI
   - Block production promotions without integration tests

2. **Coverage Targets**
   - infra: Minimum 5 integration test files
   - backstage: Raise coverage from 30% to 50%

## Test Infrastructure Requirements

### goldenpath-idp-infra

Already configured:
- `pytest` with `--runintegration` flag
- `pytest.mark.integration` marker
- Skip logic for missing services

Needed:
- Docker Compose for integration services
- CI workflow for integration tests

### goldenpath-idp-backstage

Already configured:
- Jest + Playwright
- Coverage thresholds (30% baseline)

Needed:
- Backend test infrastructure
- API mocking setup
- E2E test expansion

## Success Criteria

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| infra integration tests | 10 | 25+ | 4 weeks |
| backstage unit coverage | 63% | 80% | 4 weeks |
| backstage e2e tests | 1 | 10+ | 6 weeks |
| backend test coverage | 0% | 60% | 4 weeks |

## Action Items

### Immediate (This Sprint)

- [x] Create RAG pipeline integration tests (done 2026-01-29)
- [ ] Create ECR sync integration test
- [ ] Create secret provisioning integration test
- [ ] Add backend tests to backstage

### Short-term (Next 2 Sprints)

- [ ] EntityPage and SearchPage tests
- [ ] API integration tests
- [ ] CI workflow for integration tests
- [ ] Update coverage thresholds

### Long-term (Quarter)

- [ ] Visual regression tests
- [ ] Load testing
- [ ] Cross-repo integration tests

## Related Documents

- [GOV-0017: TDD and Determinism](../../10-governance/policies/GOV-0017-tdd-and-determinism.md)
- [tests/integration/README.md](../../../tests/integration/README.md)
- [ADR-0182: TDD Philosophy](../../adrs/ADR-0182-tdd-philosophy.md)

## Appendix: Test Pyramid Reference

```
                    ┌─────────────────┐
                    │   E2E Tests     │  ← Slow, expensive, few
                    │   (Playwright)  │
                    └────────┬────────┘
               ┌─────────────┴─────────────┐
               │    Integration Tests      │  ← Medium speed, selective
               │  (Real services, mocked)  │
               └─────────────┬─────────────┘
          ┌──────────────────┴──────────────────┐
          │          Unit Tests                 │  ← Fast, many, isolated
          │     (Mocked dependencies)           │
          └─────────────────────────────────────┘
```

Per GOV-0017: "Integration tests are selective — use them for workflows that cross boundaries."
