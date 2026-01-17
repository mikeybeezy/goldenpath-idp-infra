---
id: 19_DELIVERY_INSIGHTS
title: Delivery Insights (CI/CD Observability)
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
  - 01_GOVERNANCE
  - ADR-0009-app-delivery-insights
category: delivery
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:opentelemetry
breaking_change: false
---
# Delivery Insights (CI/CD Observability)

## Purpose

Delivery Insights provide visibility into the delivery system itself — build,
package, and promotion — so teams can understand where time, risk, and cost
accumulate during deployment.

This capability exists to support improvement, not to enforce performance
targets or mandate tooling.

## Position in the Platform

Delivery Insights are a V2, optional capability.

Golden Path V1 prioritizes:

- deterministic bootstrap and teardown
- reliable deployment and promotion
- runtime observability for deployed workloads

Delivery Insights build on this foundation once delivery becomes stable and
repeatable.

## What Delivery Insights cover

When enabled, Delivery Insights may include:

- build duration trends
- job and step-level timing
- cache effectiveness
- artifact size trends
- commit-to-deployment latency

These signals help teams identify delivery bottlenecks and regressions over
time.

## What Delivery Insights are not

Delivery Insights are not:

- mandatory for all teams
- a replacement for CI logs
- a performance scoring mechanism
- centrally enforced by the platform

Teams choose whether and when to adopt them.

## Architectural approach

Golden Path supports Delivery Insights through:

- OpenTelemetry (OTel) as the standard data model
- CI pipelines emitting workflow, job, and step spans
- export via OTLP to any compatible backend (e.g., Grafana, Honeycomb)

This keeps the platform:

- backend-agnostic
- vendor-neutral
- future-proof

Golden Path does not require or operate a specific CI observability backend.

## Reference usage

Golden Path will use Delivery Insights first for platform-owned reference
applications (e.g., Backstage) to:

- validate the approach
- refine guidance
- document patterns

Adoption by other teams is optional and example-driven.

## Governance principles

Delivery Insights follow these principles:

- opt-in, not enforced
- metadata and timing only (no command output or sensitive data)
- minimal recommended dashboards
- clear ownership by the team emitting telemetry

## Evolution

Delivery Insights may evolve as:

- delivery pipelines grow in complexity
- CI cost or flakiness becomes a concern
- teams request deeper visibility into deployment flow

Any move to make Delivery Insights a core platform feature would require a new
Architecture Decision Record (ADR).
