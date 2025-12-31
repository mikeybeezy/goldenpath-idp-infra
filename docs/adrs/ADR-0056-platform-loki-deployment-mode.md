# ADR-0056: Loki deployment mode for V1

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Observability
- **Related:** `docs/05_OBSERVABILITY_DECISIONS.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

We need a log storage baseline that is simple to operate in V1 while still
allowing a clear path to scale and HA when log volume grows. Loki offers two
common deployment modes: Single Binary and Simple Scalable. We must choose a
default that aligns with V1 delivery speed and operational cost.

---

## Decision

We will start Loki in **Single Binary** mode for V1 across environments.

We will move to **Simple Scalable** only when log retention, query performance,
or HA requirements justify the added complexity and object storage dependency.

---

## Scope

Applies to platform-managed clusters and the platform default log backend.
Teams can use external managed log services if required, but the platform
baseline remains Loki.

---

## Consequences

### Positive

- Fastest path to a working log backend.
- Lower operational overhead for V1.
- Easier to debug and recover.

### Tradeoffs / Risks

- Limited scale and HA compared to Simple Scalable.
- Retention bound by PV capacity unless archival is added.

### Operational impact

- Single Binary uses fewer components and simpler upgrades.
- Switching to Simple Scalable requires object storage (S3/GCS/MinIO) and
  more careful capacity planning.

---

## Alternatives considered

- **Simple Scalable from day one:** rejected due to higher ops overhead and
  storage dependencies before usage data exists.
- **Vendor-managed logs only:** rejected to avoid lock-in and cost creep in V1.

---

## Follow-ups

- Define thresholds for switching (ingest rate, query latency, retention).
- Document the migration path to Simple Scalable when required.

---

## Notes

This ADR reflects a V1 default and should be revisited once real log volumes
and retention needs are known.
