---
id: ADR-0078
title: 'ADR-0078: Governance-driven app repository scaffolder'
type: adr
owner: platform-team
status: active
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
- 42_APP_TEMPLATE_LIVING
- ADR-0062
- ADR-0078
------

# ADR-0078: Governance-driven app repository scaffolder

- **Status:** Proposed
- **Date:** 2026-01-03
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Governance | Delivery
- **Related:** `backstage/templates/app-template/template.yaml`, `.github/workflows/repo-scaffold-app.yml`, `docs/20-contracts/42_APP_TEMPLATE_LIVING.md`, `docs/adrs/ADR-0062-platform-app-template-contract.md`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

App repos are created ad-hoc today, which leads to missing catalog metadata,
inconsistent guardrails, and drift from platform standards. We need a single,
deterministic path that scaffolds a repo with governance metadata and the
Golden Path app template.

We also want a low-friction entry point (workflow dispatch) while keeping the
Backstage scaffolder as the long-term UX.

---

## Decision

We will provide a **governance-driven app repo scaffolder** with two entry
points that render the same template:

1. Backstage scaffolder template for self-service creation.
2. A GitHub Actions workflow for operational or scripted use.

Both entry points require governance metadata (owner, lifecycle, service tier,
data classification) and generate a repo that includes `catalog-info.yaml`
annotated with those fields.

---

## Scope

Applies to **new app repositories** created via the Golden Path template.
Existing repos are not retrofitted in V1.

---

## Consequences

### Positive

- Consistent, governance-ready metadata at repo creation.
- Single template source of truth for app scaffolds.
- Clear audit trail for who created the repo and with what inputs.
- Standard identity: every repo ships with the same CI/CD, README, and branch protections.
- No orphans: every repo is owned by a team.
- Compliance-by-default: cannot create a public repo or skip branch protection.

### Tradeoffs / Risks

- Workflow requires a repo-scoped token for creation.
- Template and workflow inputs must stay aligned.

### Operational impact

- Platform maintains the template and workflow defaults.
- Platform manages the `REPO_SCOPED_GH_TOKEN` secret for repo creation.

---

## Alternatives considered

- Manual repo creation with a checklist: too error-prone.
- Backstage-only scaffolder: higher dependency on portal availability.

---

## Follow-ups

- Document the input schema and defaults in the app template living doc.
- Decide whether to enforce repo creation through the scaffolder only in V1.1.

---

## Notes

If the template contract changes materially, publish a new ADR and supersede
this one.
