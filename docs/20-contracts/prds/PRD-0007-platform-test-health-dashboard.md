---
id: PRD-0007-platform-test-health-dashboard
title: 'PRD-0007: Platform Test Health Dashboard'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_PRDS_README
  - GOV-0016-testing-stack-matrix
  - ADR-0066-platform-dashboards-as-code
  - ADR-0090-automated-platform-health-dashboard
  - ADR-0183-test-health-metrics-schema
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0007: Platform Test Health Dashboard

Status: draft
Owner: platform-team
Date: 2026-01-26

## Problem Statement

Test results and coverage are produced across multiple frameworks and repos
(pytest, bats, Terraform tests, Jest/TypeScript), but there is no unified view
that tracks coverage, pass rates, or recency. This makes it hard to assess test
health and to surface it inside the existing Platform Health dashboard.

## Goals

- Create a single, canonical Test Health dashboard that aggregates test and
  coverage results across `goldenpath-idp-infra` and `goldenpath-idp-backstage`.
- Surface a concise Test Health summary in `PLATFORM_HEALTH.md`.
- Make test data deterministic and auditable by storing metrics in the
  governance-registry branch.

## Non-Goals

- Replacing existing CI workflows or test frameworks.
- Defining new test strategies or expanding test scope beyond current stacks.
- Building a real-time monitoring system; this is a CI-sourced dashboard.

## Scope

- **Repos**: `goldenpath-idp-infra`, `goldenpath-idp-backstage`.
- **Frameworks**: pytest, bats, Terraform tests, Jest/TypeScript tests.
- **Outputs**: JUnit summaries, coverage summaries, and derived rollups.

## Requirements

### Functional

- Collect test counts and results from each framework (total/passed/failed/skipped).
- Collect coverage data where available (lines/branches/functions/statements).
- Publish a deterministic metrics artifact to governance-registry on each run.
- Render a dedicated Test Health dashboard and a summarized section in
  `PLATFORM_HEALTH.md`.

### Non-Functional

- Deterministic outputs (stable ordering, no timestamps unless explicitly included).
- No secrets, no production data, and no privileged access required.
- Minimal additional CI runtime (< 2 minutes per workflow).

## Proposed Approach (High-Level)

- Define a canonical metrics schema (JSON) for test health.
- Implement a lightweight collector that ingests JUnit and coverage outputs
  from both repos and writes a normalized metrics artifact.
- Extend `scripts/platform_health.py` to read the metrics artifact and render
  a concise Test Health summary.
- Add a new dashboard doc (e.g., `PLATFORM_TEST_HEALTH.md`) and index it in
  `PLATFORM_DASHBOARDS.md`.

## Guardrails

- Test metrics must be non-blocking for builds (collection failure does not fail CI).
- Metrics must be written to governance-registry to avoid branch contention.

## Observability / Audit

- Store metrics artifacts per run (commit + timestamp) in governance-registry.
- Include “last updated” timestamps and source commits in the dashboard output.

## Acceptance Criteria

- Test Health dashboard renders aggregated metrics for pytest, bats, Terraform,
  and Jest across both repos.
- `PLATFORM_HEALTH.md` shows a summarized Test Health section with pass rates,
  coverage, and last updated timestamp.
- Metrics artifacts are stored in governance-registry and traceable to CI runs.

## Success Metrics

- 100% of CI runs publish test health metrics artifacts.
- Coverage and pass rates are visible in a single place across repos.
- Reduced time to detect coverage regressions (target < 1 day).

## Implementation Plan (Phased)

**Phase 0 — Align scope (no code)**

1) Confirm data sources per repo (infra + backstage) and required formats.
2) Confirm where the canonical metrics artifact will live in governance-registry.
3) Agree on schema fields and thresholds.

**Phase 1 — Canonical metrics + collector**

4) Add a collector script in infra (`scripts/collect_test_metrics.py`) that reads:
   - pytest JUnit + `coverage.xml` (infra)
   - bats JUnit (infra)
   - Jest JUnit + `coverage-summary.json` (backstage)
5) Emit a single normalized JSON payload (schema defined in this PRD).
6) Add a schema + validator for the payload (optional, if required by quality-gate).

**Phase 2 — CI wiring**

7) Update workflows to upload test artifacts in a consistent location.
8) Add a CI step to run the collector and write JSON to governance-registry
   (non-blocking if unavailable).

**Phase 3 — Dashboard surfaces**

9) Add a dedicated dashboard doc (`PLATFORM_TEST_HEALTH.md`) and list it in
   `PLATFORM_DASHBOARDS.md`.
10) Extend `scripts/platform_health.py` to read the metrics JSON and render
    a concise Test Health summary in `PLATFORM_HEALTH.md`.

**Phase 4 — Quality-gate alignment**

11) Surface quality-gate outcomes (proofs + contract validation status).
12) Make “skipped vs executed” explicit to avoid false-green reporting.

**Phase 5 — Hardening**

13) Add a small regression test for the collector output.
14) Add a check that fails only if required metrics disappear (optional, per governance).

## Open Questions (All Resolved)

| Question | Resolution | Rationale |
|----------|------------|-----------|
| Should collection fail if no metrics found? | **Yes** - collection script failure fails the gate | Per false-green prevention principle |
| Should missing metrics be warning-only for V1? | **Warning-only for V1**, hard-fail in V1.1 | Allows graceful rollout; aligns with "non-blocking for builds" guardrail |
| Per-branch or default branch only? | **Default branch only** for V1; per-branch in V1.1 if needed | Simplicity for V1 |
| How to normalize Terraform test outputs? | **Deferred** - Terraform tests not yet implemented | Phase 3 of TDD plan |
| Should collector run in infra CI only, or both repos? | **Both repos** - each writes to `governance-registry/test-metrics/{repo}.json` | Decoupled, self-contained; aggregation is a read-time concern |

**Clarification**: "Collection failure" (script crashes) vs "missing metrics" (no tests ran) are distinct:

- Collection failure → hard-fail (something is broken)
- Missing metrics → warning for V1, hard-fail for V1.1 (gradual enforcement)

## Canonical Metrics Schema

Each repo writes a JSON file to `governance-registry/test-metrics/{repo}.json`:

```json
{
  "repo": "goldenpath-idp-infra",
  "branch": "main",
  "commit": "abc123def",
  "ci_run_id": "12345678",
  "last_run": "2026-01-26T21:00:00Z",
  "frameworks": [
    {
      "framework": "pytest",
      "total": 42,
      "passed": 40,
      "failed": 1,
      "skipped": 1,
      "duration_seconds": 12.5,
      "coverage": {
        "lines": 65.2,
        "branches": 58.1,
        "functions": 70.0,
        "statements": 64.8
      },
      "threshold_met": true
    },
    {
      "framework": "bats",
      "total": 15,
      "passed": 15,
      "failed": 0,
      "skipped": 0,
      "duration_seconds": 3.2,
      "coverage": null,
      "threshold_met": true
    }
  ]
}
```

Schema fields:

| Field | Type | Description |
|-------|------|-------------|
| `repo` | string | Repository name |
| `branch` | string | Branch name (for future per-branch rollups) |
| `commit` | string | Git commit SHA |
| `ci_run_id` | string | CI run ID for traceability |
| `last_run` | ISO8601 | Timestamp of test run |
| `frameworks[]` | array | Per-framework results |
| `framework` | string | Framework name (pytest, bats, jest, terraform) |
| `total/passed/failed/skipped` | int | Test counts |
| `duration_seconds` | float | Test execution time |
| `coverage.*` | float/null | Coverage percentages (null if not applicable) |
| `threshold_met` | bool | Quick pass/fail indicator |

## Implementation Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| pytest with JUnit output | Done | `python-tests.yml` |
| bats with TAP output | Done | `bats-tests.yml` |
| Jest with JUnit output | Done | `ci.yml` |
| Coverage enforcement | Done | 60% Python, 30% Backstage |
| Contract validation | Done | EC-0016 implemented |
| Certification proofs | Done | `generate_test_proofs.py` |
| Terraform tests | Not started | Phase 3 |

## References

- GOV-0016: Testing Stack Matrix
- GOV-0017: TDD and Determinism
- ADR-0066: Platform Dashboards as Code
- ADR-0090: Automated Platform Health Dashboard
- ADR-0182: TDD Philosophy
- EC-0016: Bespoke Schema Validator
- CL-0192: Phase 1 TDD Test Suite Completion
- CL-0194: Coverage Threshold Enforcement
- `PLATFORM_HEALTH.md`

---

## Comments and Feedback

When providing feedback, leave a comment and timestamp your comment.

- **Claude Opus 4.5 / 2026-01-26:** Updated PRD to align with TDD Phase 1+2 completion. Added health thresholds, metrics schema, contract validation, certification proofs, and resolved open questions based on recent implementation work.
- **Codex / 2026-01-26:** What I reviewed: infra repo test outputs (pytest JUnit + coverage in `python-tests.yml`, bats JUnit in `bats-tests.yml`, quality gate/proof generation in `scripts/generate_test_proofs.py` and `Makefile`); Backstage repo test outputs (Jest JUnit + coverage in `goldenpath-idp-backstage/.github/workflows/ci.yml`); latest capture with bespoke schema decision and quality-gate changes in `session_capture/2026-01-26-session-capture-tdd-quality-gate.md`. Recommendations: define a canonical test-metrics schema (single JSON payload) stored in governance-registry for `PLATFORM_HEALTH.md` consumption with fields `framework`, `total`, `passed`, `failed`, `skipped`, `duration`, `coverage.lines`, `coverage.branches`, `coverage.functions`, `coverage.statements`, `last_run`, `repo`, `commit`. Standardize outputs across frameworks so the aggregator is deterministic: Python `junit.xml` + `coverage.xml` (already produced), bats `bats-junit.xml` (already produced), Backstage `junit.xml` + `coverage-summary.json` (already produced), Terraform add `terraform test -json` and convert to JUnit so it flows into the same schema. Add a Test Health section to `PLATFORM_HEALTH.md` sourced from governance-registry (overall pass rate by framework + repo, coverage percent, last run timestamp + commit, flake rate if recorded). Create a dedicated dashboard doc (e.g., `PLATFORM_TEST_HEALTH.md`) and list it in `PLATFORM_DASHBOARDS.md` with trends and a "Top 10 most flaky" section. Wire quality-gate outcomes into the dashboard (test proofs + contract validation status), and explicitly report when contract validation is skipped vs executed. Concrete data sources already available: infra pytest JUnit + coverage (`python-tests.yml`), infra bats JUnit (`bats-tests.yml`), Backstage Jest JUnit + coverage (`ci.yml`).
- **Codex / 2026-01-26 (Review):** Gaps to address: (1) coverage thresholds are listed but not anchored to the exact workflow/config sources; add references for enforcement locations. (2) Terraform tests are deferred but the schema should include a placeholder entry (`coverage: null`, `threshold_met: false`) to avoid ambiguity. (3) The Implementation Plan should explicitly include the shared schema validator as a Phase 1 deliverable if validation is required for quality-gate integrity.

- **Claude Opus 4.5 / 2026-01-26 (Review):** Reviewed PRD with Codex input. Key findings and resolutions:

  **Inconsistency Found and Resolved:** Original PRD had conflicting statements - line 148 asked "Should collection fail if no metrics found?" while line 158 marked it resolved as "Yes", but line 152 still asked "Should missing metrics be warning-only for V1?". Clarified the distinction: *collection failure* (script crashes) is different from *missing metrics* (no tests ran). Collection failure should always fail; missing metrics should warn for V1 and fail for V1.1.

  **Architecture Decision:** Both repos write independently to `governance-registry/test-metrics/{repo}.json`. This keeps repos decoupled and self-contained. Aggregation happens at read-time in `platform_health.py`. If two-file approach becomes verbose, can add a combined view later.

  **Schema Enhancements:** Added fields beyond Codex's proposal: `branch` (for future per-branch rollups), `ci_run_id` (traceability), `threshold_met` (quick pass/fail indicator). Nested frameworks array allows multiple test frameworks per repo in a single file.

  **Implementation Recommendation:** Phase 1 should include a shared schema validator (can reuse EC-0016 bespoke validator pattern) to ensure both repos emit conformant JSON before CI wiring begins.
