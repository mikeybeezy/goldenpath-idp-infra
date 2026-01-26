---
id: EC-0015-backstage-tdd-parity-plan
title: Backstage TDD Parity Plan
type: extend-capability
domain: platform-core
applies_to:
  - goldenpath-idp-backstage
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - ADR-0162-determinism-protection
  - ADR-0164-agent-trust-and-identity
  - ADR-0182-tdd-philosophy
  - GOV-0016-testing-stack-matrix
  - GOV-0017-tdd-and-determinism
supersedes: []
superseded_by: []
tags:
  - testing
  - tdd
  - backstage
  - parity
inheritance: {}
status: proposed
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# EC-0015: Backstage TDD Parity Plan

**Purpose:** Bring `goldenpath-idp-backstage` to testing parity with `goldenpath-idp-infra`.

**Target:** Apply the same TDD philosophy, agent trust architecture, and enforcement
mechanisms established in the infra repo to the Backstage repo.

---

## Current State Assessment

### Infra Repo (Reference)

| Capability | Status | Evidence |
|------------|--------|----------|
| Test coverage | ~20% | 108+ tests passing |
| TDD gate | Enforced | `tdd-gate.yml` |
| Test integrity guard | Enforced | `test-integrity-guard.yml` |
| Determinism guard | Enforced | `determinism-guard.yml` |
| Golden tests | Implemented | `tests/golden/` |
| Contract tests | Implemented | `tests/contract/` |
| Agent trust (CODEOWNERS) | Implemented | ADR-0164 paths |
| Pre-commit hooks | Enforced | ruff, shellcheck, shfmt |

### Backstage Repo (Current)

| Capability | Status | Gap |
|------------|--------|-----|
| Test coverage | ~5% | 2 smoke tests only |
| TDD gate | None | Missing workflow |
| Test integrity guard | None | Missing workflow |
| Determinism guard | None | Missing workflow |
| Golden tests | None | No directory structure |
| Contract tests | None | No directory structure |
| Agent trust (CODEOWNERS) | Basic | No protected paths |
| Pre-commit hooks | Partial | ESLint only |
| CI blocking | Disabled | `continue-on-error: true` |

---

## Target State

After implementation, Backstage repo will have:

1. **Enforced CI gates** - No `continue-on-error: true`
2. **TDD gate workflow** - Require tests for TS/TSX changes
3. **Test integrity guard** - Detect test weakening
4. **Coverage thresholds** - 50% minimum (V1), 70% (V1.1)
5. **Golden test infrastructure** - For generated code/configs
6. **Contract test infrastructure** - For API boundaries
7. **Agent trust CODEOWNERS** - Protected paths per ADR-0164
8. **Pre-commit hooks** - ESLint, Prettier, type checking

---

## Implementation Phases

### Phase 1: Remove CI Escape Hatches (P1 - Day 1)

**Goal:** Make CI gates blocking.

#### 1.1 Audit `continue-on-error` usage

```bash
# In backstage repo
grep -r "continue-on-error" .github/workflows/
```

#### 1.2 Remove or justify each instance

| File | Line | Action |
|------|------|--------|
| `ci.yml` | various | Remove |
| `build.yml` | various | Remove |

#### 1.3 Verification

- Push a failing test
- Confirm CI blocks merge

---

### Phase 2: TDD Gate Workflow (P1 - Day 1-2)

**Goal:** Require test files for source changes.

#### 2.1 Create `.github/workflows/tdd-gate.yml`

```yaml
name: TDD Gate

on:
  pull_request:
    paths:
      - 'packages/**/*.ts'
      - 'packages/**/*.tsx'
      - 'plugins/**/*.ts'
      - 'plugins/**/*.tsx'

jobs:
  check-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check for corresponding tests
        run: |
          MISSING_TESTS=()

          # Get changed source files (exclude test files)
          FILES=$(git diff --name-only origin/${{ github.base_ref }} | \
            grep -E '\.(ts|tsx)$' | \
            grep -v '\.test\.' | \
            grep -v '\.spec\.' | \
            grep -v '__tests__' | \
            grep -v '__mocks__')

          for file in $FILES; do
            # Skip non-source files
            if [[ "$file" =~ (index|types|constants|config) ]]; then
              continue
            fi

            dir=$(dirname "$file")
            base=$(basename "$file" | sed 's/\.[^.]*$//')

            # Check for test file patterns
            if [[ ! -f "${dir}/${base}.test.ts" ]] && \
               [[ ! -f "${dir}/${base}.test.tsx" ]] && \
               [[ ! -f "${dir}/${base}.spec.ts" ]] && \
               [[ ! -f "${dir}/${base}.spec.tsx" ]] && \
               [[ ! -f "${dir}/__tests__/${base}.test.ts" ]] && \
               [[ ! -f "${dir}/__tests__/${base}.test.tsx" ]]; then
              MISSING_TESTS+=("$file")
            fi
          done

          if [[ ${#MISSING_TESTS[@]} -gt 0 ]]; then
            echo "❌ Missing tests for:"
            printf '  - %s\n' "${MISSING_TESTS[@]}"
            echo ""
            echo "TDD requires a test file for each source file."
            echo "Add SKIP-TDD:reason to PR description to bypass (requires approval)."
            exit 1
          fi

          echo "✅ All source files have corresponding tests"

      - name: Check for SKIP-TDD bypass
        if: failure()
        run: |
          if [[ "${{ github.event.pull_request.body }}" =~ SKIP-TDD: ]]; then
            echo "::warning::SKIP-TDD bypass requested - requires human approval"
          fi
```

#### 2.2 Verification

- Create PR with `.ts` file but no test
- Confirm TDD gate fails
- Add test file, confirm gate passes

---

### Phase 3: Test Integrity Guard (P1 - Day 2-3)

**Goal:** Prevent test weakening.

#### 3.1 Create `.github/workflows/test-integrity-guard.yml`

```yaml
name: Test Integrity Guard

on:
  pull_request:
    paths:
      - 'packages/**/*.test.ts'
      - 'packages/**/*.test.tsx'
      - 'packages/**/*.spec.ts'
      - 'packages/**/*.spec.tsx'
      - 'plugins/**/*.test.ts'
      - 'plugins/**/*.test.tsx'
      - 'jest.config.*'
      - 'package.json'

permissions:
  contents: read
  pull-requests: write

jobs:
  test-integrity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check for coverage threshold reduction
        run: |
          # Check jest.config changes
          JEST_CHANGES=$(git diff origin/${{ github.base_ref }}...HEAD -- '**/jest.config.*' || true)

          if echo "$JEST_CHANGES" | grep -E '^\+.*coverageThreshold' | grep -E '[0-9]+' > /dev/null; then
            echo "::warning::Coverage threshold may have been modified - review required"
          fi

      - name: Detect test weakening patterns
        run: |
          DIFF=$(git diff origin/${{ github.base_ref }}...HEAD -- '**/*.test.ts' '**/*.test.tsx' '**/*.spec.ts' '**/*.spec.tsx')

          WARNINGS=""

          # Check for removed expects
          REMOVED_EXPECTS=$(echo "$DIFF" | grep -c '^-.*expect(' || true)
          ADDED_EXPECTS=$(echo "$DIFF" | grep -c '^\+.*expect(' || true)

          if [ "$REMOVED_EXPECTS" -gt "$ADDED_EXPECTS" ]; then
            WARNINGS="${WARNINGS}Net assertion reduction (removed: $REMOVED_EXPECTS, added: $ADDED_EXPECTS)\n"
          fi

          # Check for new skips
          NEW_SKIPS=$(echo "$DIFF" | grep -c '^\+.*\(it\.skip\|describe\.skip\|test\.skip\)' || true)
          if [ "$NEW_SKIPS" -gt 0 ]; then
            WARNINGS="${WARNINGS}New test skips added ($NEW_SKIPS instances)\n"
          fi

          if [ -n "$WARNINGS" ]; then
            echo "::warning::Potential test weakening detected:"
            echo -e "$WARNINGS"
            echo "Per ADR-0164, test weakening requires human review."
          fi

      - name: Count test cases
        id: test-count
        run: |
          # Count test cases (it/test functions)
          PR_TESTS=$(find packages plugins -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' 2>/dev/null | \
            xargs grep -c '^\s*\(it\|test\)(' 2>/dev/null | \
            awk -F: '{sum += $2} END {print sum}' || echo "0")

          git checkout origin/${{ github.base_ref }} -- packages/ plugins/ 2>/dev/null || true
          BASE_TESTS=$(find packages plugins -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' 2>/dev/null | \
            xargs grep -c '^\s*\(it\|test\)(' 2>/dev/null | \
            awk -F: '{sum += $2} END {print sum}' || echo "0")

          git checkout HEAD -- packages/ plugins/

          echo "base_count=$BASE_TESTS" >> $GITHUB_OUTPUT
          echo "pr_count=$PR_TESTS" >> $GITHUB_OUTPUT

          if [ "$PR_TESTS" -lt "$BASE_TESTS" ]; then
            DIFF=$((BASE_TESTS - PR_TESTS))
            echo "::error::Test count regression: $DIFF fewer tests"
            echo "::error::Per ADR-0164, removing tests requires human approval"
            exit 1
          fi
```

---

### Phase 4: Coverage Enforcement (P1 - Day 3-4)

**Goal:** Enforce minimum coverage thresholds.

#### 4.1 Update `jest.config.js` (or `jest.config.ts`)

```javascript
module.exports = {
  // ... existing config

  collectCoverage: true,
  collectCoverageFrom: [
    'packages/*/src/**/*.{ts,tsx}',
    'plugins/*/src/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/__mocks__/**',
    '!**/__tests__/**',
  ],
  coverageThreshold: {
    global: {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50,
    },
  },
  coverageReporters: ['text', 'lcov', 'html'],
};
```

#### 4.2 Update CI workflow

```yaml
- name: Run tests with coverage
  run: |
    yarn test --coverage --ci --reporters=default --reporters=jest-junit
  env:
    JEST_JUNIT_OUTPUT_DIR: ./reports
    JEST_JUNIT_OUTPUT_NAME: junit.xml

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage/lcov.info
    fail_ci_if_error: true
```

#### 4.3 Coverage targets

| Phase | Branches | Functions | Lines | Statements |
|-------|----------|-----------|-------|------------|
| V1 (now) | 50% | 50% | 50% | 50% |
| V1.1 | 70% | 70% | 70% | 70% |
| V2 | 80% | 80% | 80% | 80% |

---

### Phase 5: Golden Test Infrastructure (P2 - Week 2)

**Goal:** Test generated outputs (templates, configs).

#### 5.1 Create directory structure

```
packages/backend/src/
  __golden__/
    fixtures/
      inputs/
        catalog-info-basic.yaml
      expected/
        catalog-info-basic-resolved.yaml
    __tests__/
      catalogResolver.golden.test.ts
```

#### 5.2 Create golden test utilities

```typescript
// packages/backend/src/__golden__/utils.ts
import { readFileSync } from 'fs';
import { join } from 'path';

const FIXTURES_DIR = join(__dirname, 'fixtures');

export function loadInput(name: string): string {
  return readFileSync(join(FIXTURES_DIR, 'inputs', name), 'utf-8');
}

export function loadExpected(name: string): string {
  return readFileSync(join(FIXTURES_DIR, 'expected', name), 'utf-8');
}

export function assertMatchesGolden(actual: string, goldenFile: string): void {
  const expected = loadExpected(goldenFile);

  // Normalize whitespace
  const actualNorm = actual.trim();
  const expectedNorm = expected.trim();

  if (actualNorm !== expectedNorm) {
    throw new Error(
      `Output differs from golden file '${goldenFile}'.\n\n` +
      `If this change is intentional:\n` +
      `  1. Review the diff\n` +
      `  2. Get human approval (per ADR-0164)\n` +
      `  3. Update the golden file\n\n` +
      `Expected:\n${expectedNorm}\n\nActual:\n${actualNorm}`
    );
  }
}
```

#### 5.3 Example golden test

```typescript
// packages/backend/src/__golden__/__tests__/catalogResolver.golden.test.ts
import { loadInput, assertMatchesGolden } from '../utils';
import { resolveCatalogInfo } from '../../plugins/catalog/resolver';

describe('Catalog Resolver (Golden)', () => {
  it('resolves basic catalog-info correctly', async () => {
    const input = loadInput('catalog-info-basic.yaml');
    const result = await resolveCatalogInfo(input);
    assertMatchesGolden(result, 'catalog-info-basic-resolved.yaml');
  });
});
```

---

### Phase 6: Contract Test Infrastructure (P2 - Week 2)

**Goal:** Test API boundaries and schemas.

#### 6.1 Create directory structure

```
packages/backend/src/
  __contracts__/
    fixtures/
      requests/
        valid/
          create-component.json
        invalid/
          missing-required-fields.json
    __tests__/
      catalogApi.contract.test.ts
```

#### 6.2 Example contract test

```typescript
// packages/backend/src/__contracts__/__tests__/catalogApi.contract.test.ts
import request from 'supertest';
import { createApp } from '../../app';

describe('Catalog API Contract', () => {
  let app: Express;

  beforeAll(async () => {
    app = await createApp();
  });

  describe('POST /api/catalog/entities', () => {
    it('accepts valid entity', async () => {
      const validEntity = require('../fixtures/requests/valid/create-component.json');

      const response = await request(app)
        .post('/api/catalog/entities')
        .send(validEntity)
        .expect(201);

      expect(response.body).toHaveProperty('metadata.uid');
    });

    it('rejects invalid entity with 400', async () => {
      const invalidEntity = require('../fixtures/requests/invalid/missing-required-fields.json');

      const response = await request(app)
        .post('/api/catalog/entities')
        .send(invalidEntity)
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });
  });
});
```

---

### Phase 7: Agent Trust CODEOWNERS (P1 - Day 4)

**Goal:** Protect test integrity paths per ADR-0164.

#### 7.1 Create/Update `.github/CODEOWNERS`

```
# Owner: platform-team
# Purpose: Ensure human oversight per ADR-0164 Agent Trust Architecture
#
# AGENT TRUST BOUNDARIES
# ======================
# AI agents cannot approve changes to these paths.
# They can only propose changes for human review.

# Global fallback
*                                   @mikeybeezy

# ============================================================================
# PROTECTED RESOURCES - Agent Trust Boundaries (ADR-0164)
# ============================================================================

# This file itself - agents cannot modify approval authority
.github/CODEOWNERS                  @mikeybeezy

# CI/CD workflows - agents cannot modify enforcement mechanisms
.github/workflows/                  @mikeybeezy

# Test configuration - agents cannot weaken coverage thresholds
jest.config.*                       @mikeybeezy
**/jest.config.*                    @mikeybeezy

# Golden files - agents cannot change expected behavior
**/__golden__/fixtures/expected/    @mikeybeezy

# Package configuration - agents cannot modify test settings
package.json                        @mikeybeezy
**/package.json                     @mikeybeezy

# ============================================================================
# STANDARD CODE OWNERSHIP
# ============================================================================

# Backend packages
packages/backend/                   @mikeybeezy

# Frontend packages
packages/app/                       @mikeybeezy

# Plugins
plugins/                            @mikeybeezy
```

---

### Phase 8: Pre-commit Hooks (P2 - Week 2)

**Goal:** Enforce quality before commit.

#### 8.1 Create `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=500']

  - repo: local
    hooks:
      - id: eslint
        name: ESLint
        entry: yarn lint
        language: system
        types: [typescript, tsx]
        pass_filenames: false

      - id: typecheck
        name: TypeScript Check
        entry: yarn tsc --noEmit
        language: system
        types: [typescript, tsx]
        pass_filenames: false

      - id: test-affected
        name: Test Affected
        entry: yarn test --onlyChanged --passWithNoTests
        language: system
        types: [typescript, tsx]
        pass_filenames: false
```

#### 8.2 Add to package.json

```json
{
  "scripts": {
    "prepare": "husky install",
    "pre-commit": "lint-staged"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

---

## File Creation Summary

| Phase | File | Action |
|-------|------|--------|
| P1 | `.github/workflows/tdd-gate.yml` | Create |
| P1 | `.github/workflows/test-integrity-guard.yml` | Create |
| P1 | `.github/CODEOWNERS` | Create/Update |
| P1 | `jest.config.js` | Update (coverage thresholds) |
| P1 | `.github/workflows/ci.yml` | Update (remove continue-on-error) |
| P2 | `packages/backend/src/__golden__/` | Create directory |
| P2 | `packages/backend/src/__golden__/utils.ts` | Create |
| P2 | `packages/backend/src/__contracts__/` | Create directory |
| P2 | `.pre-commit-config.yaml` | Create |
| P2 | `package.json` | Update (lint-staged, husky) |

---

## Verification Checklist

### Phase 1 Verification
- [ ] `grep -r "continue-on-error" .github/workflows/` returns empty
- [ ] Failing test blocks PR merge

### Phase 2 Verification
- [ ] PR with `.ts` file and no test fails TDD gate
- [ ] PR with `.ts` file and matching test passes TDD gate
- [ ] SKIP-TDD bypass shows warning

### Phase 3 Verification
- [ ] Removing assertions triggers warning
- [ ] Adding `it.skip` triggers warning
- [ ] Test count regression blocks merge

### Phase 4 Verification
- [ ] `yarn test --coverage` shows coverage report
- [ ] Coverage below threshold fails CI

### Phase 5-6 Verification
- [ ] Golden test fails when output changes
- [ ] Contract test validates API schema

### Phase 7 Verification
- [ ] Changes to protected paths require CODEOWNER approval
- [ ] GitHub shows correct reviewers

---

## Success Metrics

| Metric | Current | V1 Target | V1.1 Target |
|--------|---------|-----------|-------------|
| Test coverage | ~5% | 50% | 70% |
| CI gates blocking | No | Yes | Yes |
| TDD gate active | No | Yes | Yes |
| Golden tests | 0 | 5+ | 20+ |
| Contract tests | 0 | 5+ | 15+ |
| CODEOWNERS protected | No | Yes | Yes |

---

## Related Documents

- [ADR-0162: Determinism Protection](../adrs/ADR-0162-determinism-protection.md)
- [ADR-0164: Agent Trust and Identity](../adrs/ADR-0164-agent-trust-and-identity.md)
- [ADR-0182: TDD Philosophy](../adrs/ADR-0182-tdd-philosophy.md)
- [GOV-0016: Testing Stack Matrix](../10-governance/policies/GOV-0016-testing-stack-matrix.md)
- [GOV-0017: TDD and Determinism](../10-governance/policies/GOV-0017-tdd-and-determinism.md)

---

*"The same trust architecture that governs agents in infra must govern agents in Backstage."*
