---
id: 00_DESIGN_PHILOSOPHY
title: GoldenPath Design Philosophy
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
  - 00_DOC_INDEX
  - 01_GOVERNANCE
  - 02_PLATFORM_BOUNDARIES
  - 30_DOCUMENTATION_FRESHNESS
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - 37_V1_SCOPE_AND_TIMELINE
  - 43_OPERATING_PRINCIPLES
  - 90_DOC_SYSTEM
  - ADR-0027-platform-design-philosophy
  - IDP_PRODUCT_FEATURES
  - agent_session_summary
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

## GoldenPath Design Philosophy

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

## 6) Externalized memory over tribal knowledge

Documentation is not an afterthought—it is the platform's memory. We write abundantly because:

- **We are not afraid of information loss.** Decisions, context, and rationale live in structured files, not in someone's head.
- **Infrastructure is traversable by design.** Documents are interconnected through explicit `relates_to` links, enabling navigation by humans and agents alike.
- **Safe iteration requires captured decisions.** When decisions are recorded, we can confidently change course because we understand what led us here and can rollback with context.
- **Onboarding serves humans and agents equally.** The same documentation that helps a new engineer ramp up enables an AI agent to provide accurate assistance.
- **Outcomes trace back to decisions.** Any current state can be audited back through the evolutionary path of ADRs, changelogs, and governance records.

This makes the platform **robust but malleable**: stable enough to trust, flexible enough to evolve.

### The paradigm shift

Traditional documentation assumes humans read, memorize, and recall. We assume instead that:

1. Machines retrieve and surface relevant context on demand
2. Humans focus on judgment and synthesis, not memorization
3. Abundance of structured information beats sparse, polished documentation

The documentation need not be optimized for human reading speed—it must be optimized for **machine traversability** and **completeness**. If the information exists and is findable, agents can surface it when needed.

## Documentation as product

The design philosophy is a living document. Core living docs are indexed in
`docs/90-doc-system/00_DOC_INDEX.md` and tracked by the doc freshness mechanism described in
`docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md`.
