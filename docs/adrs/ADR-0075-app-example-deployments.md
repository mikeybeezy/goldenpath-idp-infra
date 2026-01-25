<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0075-app-example-deployments
title: 'ADR-0075: App example deployments via Argo CD, Helm, and Kustomize'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - ADR-0075-app-example-deployments
  - CL-0027-app-example-deployments
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2028-01-04
version: '1.0'
breaking_change: false
---

# ADR-0075: App example deployments via Argo CD, Helm, and Kustomize

Filename: `ADR-0075-platform-app-example-deployments.md`

- **Status:** Accepted
- **Date:** 2026-01-03
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** PR #127, docs/40-delivery/42_APP_EXAMPLE_DEPLOYMENTS.md, docs/changelog/entries/CL-0027-app-example-deployments.md

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Example applications were added under `apps/`, but they lacked a consistent,
repeatable packaging format for GitOps deployment. We need deterministic example
apps that can be deployed via Argo CD using either Helm or Kustomize, while
keeping the Backstage scaffold templates intact.

## Decision

We will standardize example apps with a consistent scaffold layout and add
deployable packaging for both Helm and Kustomize, plus Argo CD Application
manifests per environment.

## Scope

Applies to:

- Example apps under `apps/` (stateless, stateful, WordPress-on-EFS).
- Per-app dashboards and ServiceMonitor defaults.
- Argo CD app manifests under `gitops/argocd/apps/<env>/`.

Does not apply to:

- `apps/fast-api-app-template/` (remains the Backstage scaffold source only).
- Production application delivery standards beyond example usage.

## Consequences

### Positive

- Consistent example app deployment across Argo CD + Helm + Kustomize.
- Clear reference for teams adopting the Golden Path app pattern.
- Out-of-the-box dashboards and metrics wiring for examples.

### Tradeoffs / Risks

- Adds more example files to maintain.
- Example manifests may drift from live best practices without periodic review.

### Operational impact

- Argo CD Applications can be synced from example paths for validation.
- Doc updates are required when example patterns change.

## Alternatives considered

- Keep examples as raw manifests only: rejected due to inconsistent deployment.
- Provide Helm-only examples: rejected to keep parity with Kustomize workflows.

## Follow-ups

- Add example application runbook updates if patterns evolve.
- Periodically validate example apps during platform readiness reviews.

## Notes

None.
