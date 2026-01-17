---
id: ADR-0131
title: 'ADR-0131: Outcome Metrics for Platform Health'
type: adr
status: proposed
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0090-automated-platform-health-dashboard
  - ADR-0113-platform-queryable-intelligence-enums
  - ADR-0131
  - CL-0091-platform-health-outcome-metrics
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-08
version: 1.0
breaking_change: false
---

# ADR-0131: Outcome Metrics for Platform Health

- **Status:** Proposed
- **Date:** 2026-01-08
- **Owners:** `platform-team`
- **Decision type:** Governance | Observability

---

## Context

The platform health dashboard currently focuses on governance inputs
(metadata compliance, ADR activity, changelog volume) but lacks outcome-based
signals that reflect delivery reliability and time-to-value. This creates a
risk of drift toward vanity metrics and makes it hard to detect operational
inefficiencies in the platform lifecycle.

We need a minimal, repeatable way to capture outcome metrics without introducing
heavy infrastructure or slow manual reporting.

## Decision

We will extend platform health reporting to include **outcome metrics** sourced
from CI logs and operational records, and we will track **time-to-ready** for
ECR provisioning as a first high-signal metric.

## Scope

**Applies to:**
- Platform Health dashboard (`PLATFORM_HEALTH.md`)
- Outcome metrics aggregation (`OUTCOME_METRICS.json`)
- ECR provisioning workflow (time-to-ready tracking)

**Does not apply to:**
- Terraform/AWS resource tags (value intent stays in governance/docs)
- Mandatory backfill across all existing docs

## Consequences

### Positive
- Adds delivery reliability and latency signals to V1 readiness.
- Enables trend tracking for plan/apply/teardown outcomes.
- Provides a concrete time-to-ready measure for ECR provisioning.

### Tradeoffs / Risks
- Requires additional instrumentation in CI/logging.
- Metrics can mislead if data collection is partial or inconsistent.
- Adds small maintenance overhead for aggregation scripts.

### Operational impact
- Add/maintain a lightweight aggregation script.
- Update workflows to emit consistent status/duration fields.
- Keep outcome metrics updated on a schedule.

## Alternatives considered

1. **Manual reporting** (rejected: slow and inconsistent).
2. **Full observability stack first** (rejected: too heavy for V1).
3. **No change** (rejected: risks vanity metrics and blind spots).

## Follow-ups

- Define `OUTCOME_METRICS.json` schema and aggregation script.
- Update `platform_health.py` to surface outcome metrics.
- Add ECR time-to-ready tracking in the registry workflow.
- Decide enforcement scope for new value metadata fields.

## Notes

If outcome metrics drift or remain incomplete for more than one release cycle,
we will revisit instrumentation scope and required fields.
