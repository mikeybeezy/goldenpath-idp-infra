# GoldenPath Design Philosophy

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
`docs/00_DOC_INDEX.md` and tracked by the doc freshness mechanism described in
`docs/30_DOCUMENTATION_FRESHNESS.md`.
