---
id: ADR-0051
title: 'ADR-0051: Minimal reliability metrics and contract minimums'
type: adr
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
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
  - 02_PLATFORM_BOUNDARIES
  - 17_BUILD_RUN_FLAGS
  - 21_CI_ENVIRONMENT_CONTRACT
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - 35_RESOURCE_TAGGING
  - 40_CHANGELOG_GOVERNANCE
  - ADR-0051
---

# ADR-0051: Minimal reliability metrics and contract minimums

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Operations | Governance
- **Related:** `docs/40-delivery/17_BUILD_RUN_FLAGS.md`, `docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md`, `docs/20-contracts/02_PLATFORM_BOUNDARIES.md`, `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`, `docs/10-governance/35_RESOURCE_TAGGING.md`, `docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md`, `docs/build-timings.csv`, `scripts/reliability-metrics.sh`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

V1 needs visible proof that build/teardown are reliable without adopting full
CI observability. We also need a minimal platform contract that keeps lifecycle
runs deterministic and auditable without introducing heavyweight gates.

---

## Decision

We will adopt a **minimal reliability metrics baseline** and a **minimal
platform contract** for V1.

Reliability metrics baseline:

- Timed build/teardown runs will append rows to `docs/build-timings.csv` with
  start/end, duration, status, and log path.
- `make reliability-metrics` will summarize build/teardown counts and
  durations from that CSV.

Minimal platform contract:

- Required tags are `BuildId`, `Environment`, `Lifecycle`, `ManagedBy`, `Owner`,
  and `Project`.
- CI workflows require `env` and `lifecycle`, plus `build_id` for ephemeral
  runs and explicit confirmation inputs for apply/bootstrap.
- Changelog entries are required only when a PR is labeled
  `changelog-required`.

---

## Scope

Applies to platform build/teardown workflows and governance docs in this repo.
Does not introduce full CI observability, service-level metrics, or new
runtime SLO requirements.

---

## Consequences

### Positive

- Reliability is visible with minimal overhead.
- Contract requirements are explicit and auditable.
- V1 avoids heavy tooling while preserving determinism.

### Tradeoffs / Risks

- CSV-based metrics are coarse and require discipline to keep current.
- Contract enforcement is mostly documentation and workflow input validation.
- Metrics are not real-time and do not replace full CI observability.

### Operational impact

- Use timed Make targets for build/teardown when gathering reliability data.
- Keep required tags consistent in Terraform/automation.
- Apply changelog labels intentionally to enforce entries when needed.

---

## Alternatives considered

- Full CI observability (OTel + backend): deferred as V2; higher cost/complexity.
- No metrics and no explicit contract: rejected due to lack of visibility and
  increased operator ambiguity.
- Enforce contract via policy-as-code gates: deferred to avoid V1 friction.

---

## Follow-ups

- Wire timed targets into CI workflows when acceptable to write metrics data.
- Revisit if reliability metrics need a non-repo storage backend.
- Extend contract enforcement if drift is observed.

---

## Notes

This ADR sets a **minimum** baseline and is expected to be superseded once V1
reliability evidence is stable and V2 observability is introduced.
