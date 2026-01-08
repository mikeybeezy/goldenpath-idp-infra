---
id: ADR-0009-app-delivery-insights
title: 'ADR-0009: CI/CD observability via OpenTelemetry ("Delivery Insights")'
type: adr
status: active
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0008
  - ADR-0009
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0009: CI/CD observability via OpenTelemetry (“Delivery Insights”)

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Application
- **Decision type:** Architecture | Observability | Delivery
- **Related:** docs/10-governance/01_GOVERNANCE.md, docs/40-delivery/19_DELIVERY_INSIGHTS.md, docs/adrs/ADR-0008-app-backstage-portal.md

## Context

Delivery (build → package → promote) represents a significant portion of value
creation in the platform. Traditional CI feedback (pass/fail + logs) is
insufficient to:

- understand build performance trends
- identify delivery bottlenecks
- reduce flakiness
- reason about delivery cost over time

We want visibility into the delivery system itself without coupling the
platform to a single vendor or mandating adoption.

## Decision

GoldenPath will support CI/CD observability by enabling GitHub Actions to emit
OpenTelemetry traces representing:

- workflow runs
- jobs
- individual steps

These traces can be exported via OTLP to any compatible backend (e.g., Grafana
Tempo, Honeycomb, Datadog).

This capability is provided as an **optional “Delivery Insights” addon**, not a
mandatory platform requirement.

## Scope

- Applies to: CI pipelines that choose to adopt it (initially Backstage

  reference app).

- Out of scope:
  - mandatory instrumentation
  - log or command output capture
  - platform-operated CI observability backend

## Consequences

### Positive

- Makes delivery performance measurable and explainable.
- Enables trend analysis (build time, step regressions, cache efficiency).
- Aligns CI/CD observability with runtime observability via shared OTel

  semantics.

- Differentiates the platform without increasing baseline complexity.

### Tradeoffs / Risks

- Telemetry volume and cost if applied indiscriminately.
- Requires secure handling of exporter credentials.
- Risk of over-optimising CI too early.

### Mitigations

- Adoption is opt-in.
- Initial usage limited to reference applications.
- Recommended dashboards limited to a small, curated set.
- Clear guidance on attributes vs payload size.

### Operational impact

- Provide reference GitHub Actions workflows that emit OTel spans.
- Document required attributes (repo, workflow, job, step, commit SHA).
- Recommend but do not enforce backends.
- Ensure secrets for exporters are managed via GitHub Secrets.

## Alternatives considered

- CI logs only (rejected: insufficient signal).
- Vendor-specific CI visibility only (rejected: lock-in).
- Custom metrics scraping (rejected: higher effort, less flexibility).

## Follow-ups

- Add reference workflow for Backstage CI with OTel export.
- Add “Delivery Insights” section to platform docs.
- Define a minimal, recommended dashboard set.
