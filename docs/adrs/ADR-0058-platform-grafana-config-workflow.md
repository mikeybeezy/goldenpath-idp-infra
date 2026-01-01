# ADR-0058: Separate Grafana config workflow with readiness guard

Filename: `ADR-0058-platform-grafana-config-workflow.md`

- **Status:** Proposed
- **Date:** 2025-12-31
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Observability | Operations
- **Related:** `docs/50-observability/05_OBSERVABILITY_DECISIONS.md`, `idp-tooling/grafana-config/`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Grafana configuration (dashboards, datasources, alert rules) is managed as code
via Terraform in `idp-tooling/grafana-config/`. The Grafana API must be reachable
and stable before the provider can apply changes. Bootstrap completion does not
guarantee Grafana readiness, and stabilization time varies by environment and
team resource profiles.

We need a workflow that is reliable today and flexible for future automation.

---

## Decision

We will use a **separate, manually triggered workflow** for Grafana config
applies, with a **readiness guard** (health check/retry) inside the workflow.

Bootstrap will **not** invoke Grafana config by default.

---

## Scope

Applies to:
- Grafana dashboards, datasources, and alert rules managed via Terraform.
- CI-driven platform configuration flows.

Does not apply to:
- Grafana deployment (handled by bootstrap/GitOps).
- App-team owned dashboards managed outside platform scope.

---

## Consequences

### Positive

- Avoids false failures when Grafana is not yet ready after bootstrap.
- Keeps bootstrap deterministic and predictable across environments.
- Provides a clear operational gate and audit trail for config changes.

### Tradeoffs / Risks

- Adds an extra manual step until automation is reliable.
- Dashboards may appear later than platform deploys if the workflow is not run.
- Requires readiness checks and retry logic to be maintained.

### Operational impact

- Operators trigger the Grafana config workflow after confirming readiness.
- Workflow must include a health check before applying Terraform changes.

---

## Alternatives considered

- **Inline in bootstrap:** rejected due to variable stabilization time and
  increased bootstrap fragility.
- **Fully automated trigger:** deferred until readiness signals are stable.
- **Manual Terraform apply only:** rejected; lacks CI audit trail and consistency.

---

## Follow-ups

- Add the Grafana config workflow with readiness guard.
- Add a runbook section for timing and readiness checks.
- Revisit automation once readiness signals are stable across environments.

---

## Notes

This is a deliberate hybrid choice: manual trigger now, with a readiness guard,
and a path to automation later.
