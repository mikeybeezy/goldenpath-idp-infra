---
id: 00_DESIGN_PHILOSOPHY
title: GoldenPath Design Philosophy
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
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 00_DOC_INDEX
- 01_GOVERNANCE
- 02_PLATFORM_BOUNDARIES
- 30_DOCUMENTATION_FRESHNESS
- 43_OPERATING_PRINCIPLES
---

# GoldenPath Design Philosophy

Doc contract:

- Purpose: Define product philosophy and foundational principles.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/10-governance/01_GOVERNANCE.md, docs/20-contracts/02_PLATFORM_BOUNDARIES.md, docs/00-foundations/43_OPERATING_PRINCIPLES.md

GoldenPath is an Internal Developer Platform designed around one core principle:

> We build the platform using the same paths we expect others to use.

The platform’s own workloads, pipelines, and governance are not special cases. They are the
reference implementation.

## First principles

### 1) Determinism over cleverness

The platform prioritizes predictable outcomes over maximum flexibility. If a system can be torn
down and rebuilt with confidence, it can be trusted.

### 2) Opinionated defaults, not mandates

GoldenPath provides strong defaults that work out of the box. Teams may deviate when justified, but
the default path is designed to be safe, repeatable, and low-friction.

### 3) Governance as constraint, not control

Governance exists to reduce ambiguity and risk, not to slow delivery. Decisions are captured
explicitly so tradeoffs are visible and revisitable.

### 4) One system, many workloads

There is a single delivery system. The platform itself is simply the first workload running on it.

### 5) Proof over promise

Every recommendation in GoldenPath is backed by a working example. If the platform cannot support
its own build and delivery needs, it is not ready to support others.

## Documentation as product

The design philosophy is a living document. Core living docs are indexed in
`docs/90-doc-system/00_DOC_INDEX.md` and tracked by the doc freshness mechanism described in
`docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md`.
