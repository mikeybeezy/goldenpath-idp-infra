---
id: DOCS_BUILD-RUN-LOGS_README
title: Build and Teardown Logs Documentation
type: documentation
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - 41_BUILD_RUN_LOG
  - BR-TEMPLATE
  - BR_TEMPLATE
  - TD-TEMPLATE
  - TD_TEMPLATE
---

# Build Run Logs

This directory holds per-run records for builds/bootstraps and teardowns.

## Naming convention

- `BR-XXXX-<build-id>.md` for build + bootstrap runs
- `TD-XXXX-<build-id>.md` for teardown runs

`XXXX` is a zero-padded sequence (start at 0001).

## When to add a new entry

Create an entry when:

- A build/bootstrap/teardown run is used for validation, demos, or promotion decisions.
- A run exposes a failure mode, cleanup issue, or notable drift.
- You need a durable reference beyond CI logs (timing, flags, or outcomes).

Do not create an entry for:

- Local experiments that are not part of shared validation.
- Runs that duplicate an existing log without new findings.

Use `docs/40-delivery/41_BUILD_RUN_LOG.md` as the summary index and link to
these entries for deeper detail.

## Usage guidelines

- Keep entries lightweight and factual; avoid narrative unless there is an issue.
- Use the workflow run URL as the source of truth for logs and raw output.
- Summarize key metrics (duration, plan delta, orphan counts) consistently.
- Periodically summarize (weekly/monthly) to keep the log set actionable.

## Standard Fields

Please copy the appropriate template when creating a new entry:

- **Build/Bootstrap:** `docs/build-run-logs/BR-TEMPLATE.md`
- **Teardown:** `docs/build-run-logs/TD-TEMPLATE.md`

Key metrics to capture:

- **Build ID / Commit:** Traceability to code.
- **Plan Delta:** Number of resources added/changed/destroyed (Blast radius).
- **Duration:** Precise times for Build vs. Bootstrap phases.
- **Flags:** Exact flags used for reproducibility.
