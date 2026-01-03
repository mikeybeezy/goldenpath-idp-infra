# CL-0030: Add Build Log Metrics and Roadmap Update

Date: 2026-01-03
Owner: platform
Scope: docs
Related: docs/build-run-logs/BR-0002-03-01-26-01.md, docs/production-readiness-gates/ROADMAP.md

## Summary

This change standardizes how we capture build metrics and adds Cost Visibility to the roadmap.

## Changes

### Added
- **Metric: Plan Delta:** Added to build logs to measure resource churn (blast radius).
- **Roadmap Item 045:** Added "Infracost + Backstage Integration" to `ROADMAP.md`.
- **Log Schema:** Updated `docs/build-run-logs/README.md` to require Plan Delta and Duration fields.

### Changed
- **BR-0002:** Enriched the log for build 03-01-26-01 with precise timestamps and Delta analysis.

## Impact
- **Observability:** Better historical data on build efficiency and churn.
- **Strategy:** Formalized the intent to add cost visibility (FinOps).
