<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: PRD-0006-persistent-cluster-build-timing
title: 'PRD-0006: Persistent Cluster Build Timing Capture'
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - ADR-0156
  - CL-0128
  - DOCS_PRDS_README
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0006: Persistent Cluster Build Timing Capture

Status: draft
Owner: platform-team
Date: 2026-01-24

## Problem Statement

Build and teardown timings for persistent cluster deployments are not being captured in the governance registry. The `record-build-timing.sh` script was implemented for ephemeral CI builds (ADR-0156) but was not integrated with the Bootstrap v4 persistent cluster workflow introduced later.

This creates an observability gap:
- No visibility into persistent cluster provisioning durations
- Cannot track reliability SLOs for persistent deployments
- Cannot correlate build time with infrastructure costs
- Cannot identify performance regressions over time

**Evidence**: The governance-registry branch stores timing data in `environments/<env>/latest/build_timings.csv`. The persistent cluster deployed on 2026-01-24 was not recorded because the `record-build-timing.sh` script was not called by persistent cluster targets.

## Goals

- Capture build timings for all persistent cluster deployments
- Capture teardown timings for all persistent cluster teardowns
- Maintain parity with ephemeral build timing capture
- Enable reliability metrics and trend analysis for persistent clusters

## Non-Goals

- Changing the existing CSV schema or data format
- Backfilling historical data for past deployments
- Real-time alerting on build durations (future enhancement)
- Modifying ephemeral build timing capture (already working)

## Scope

**In Scope**:
- `make deploy-persistent` (all BOOTSTRAP_VERSION variants)
- `make teardown-persistent`
- `make bootstrap-persistent-v4`
- `make apply-persistent`

**Out of Scope**:
- CI workflow timing (handled separately by ADR-0156)
- RDS-only deployments (`make rds-deploy`)
- Individual ArgoCD app sync timings

## Requirements

### Functional

- FR-1: Each `deploy-persistent` invocation MUST record an entry in `environments/<env>/latest/build_timings.csv` on the governance-registry branch
- FR-2: Each `teardown-persistent` invocation MUST record an entry in the same CSV
- FR-3: Timing entries MUST include: start_time_utc, end_time_utc, phase, env, build_id, duration_seconds, exit_code, flags, resources_added, resources_changed, resources_destroyed, log_path
- FR-4: Build ID for persistent clusters MUST be "persistent" to distinguish from ephemeral DD-MM-YY-NN format
- FR-5: Failed builds MUST still record timing with appropriate exit_code
- FR-6: Log filenames MUST match pattern `*<phase>*<build_id>*.log` for timing capture to work

### Non-Functional

- NFR-1: Timing capture MUST NOT block or delay the actual build/teardown operation
- NFR-2: Timing capture failures MUST be non-blocking (fail-open)
- NFR-3: Timing data MUST be committed to the governance-registry branch
- NFR-4: Implementation MUST be idempotent (running twice produces consistent results)

## Proposed Approach (High-Level)

1. Update log naming in Makefile to include canonical `build_id` and `phase` matching the pattern `*<phase>*<build_id>*.log`
2. Add `record-build-timing.sh` call to `bootstrap-persistent-v4` Makefile target after bootstrap completion
3. Add `record-build-timing.sh` call to `teardown-persistent` Makefile target after teardown completion
4. Add `record-build-timing.sh` call to `apply-persistent` Makefile target after terraform apply
5. Use phase identifiers: `bootstrap-persistent`, `teardown-persistent`, `apply-persistent`
6. Set BUILD_ID to "persistent" to distinguish from ephemeral builds

## Guardrails

- Timing capture script MUST run in fail-open mode (errors logged but not propagated)
- No credentials or sensitive data in timing entries
- Governance-registry branch push MUST use existing CI workflow (not direct push from local)

## Observability / Audit

- All timing entries stored in `environments/<env>/latest/build_timings.csv` on governance-registry branch (append-only)
- Log files stored in `logs/build-timings/` directory with naming pattern `*<phase>*<build_id>*.log`
- Script commits directly to governance-registry branch
- Can query CSV for metrics: average duration, success rate, trend over time

## Acceptance Criteria

- [ ] AC-1: Running `make deploy-persistent ENV=dev` creates a new entry in `environments/development/latest/build_timings.csv` on governance-registry branch
- [ ] AC-2: Running `make teardown-persistent ENV=dev` creates a new entry in same CSV
- [ ] AC-3: Entry includes accurate start_time_utc, end_time_utc, and duration_seconds
- [ ] AC-4: Entry includes correct phase identifier (bootstrap-persistent, teardown-persistent)
- [ ] AC-4a: Log filename matches pattern `*<phase>*<build_id>*.log` (required for script pattern matching)
- [ ] AC-5: Entry includes correct env and build_id
- [ ] AC-6: Failed operations still record timing with non-zero exit_code
- [ ] AC-7: Timing capture failure does not block the main operation

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Timing capture rate | 100% | All persistent builds have CSV entry |
| Data accuracy | Duration within 5s of actual | Compare CSV to log timestamps |
| Non-blocking | 0 build failures from timing | No exit code 1 from record script |

## Open Questions

1. Should we use "persistent" as build_id or derive from cluster name (e.g., "goldenpath-dev-eks")?
2. Should we capture sub-phase timings (terraform Phase 1, terraform Phase 2, ArgoCD sync)?
3. Should timing data also be pushed to a metrics backend (Prometheus/CloudWatch)?

## References

- ADR-0156: Platform CI Build Timing Capture
- CL-0128: CI Build Timing Capture changelog
- `scripts/record-build-timing.sh` - Existing timing capture script (line 47 shows pattern matching)
- `environments/<env>/latest/build_timings.csv` on governance-registry branch - Timing data store
- Session Capture: 2026-01-24-build-timing-capture-gap.md

---

## Comments and Feedback

- 2026-01-24 (platform-team): Initial draft based on gap discovered during persistent cluster deployment.
