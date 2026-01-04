---
id: 44_PRINCIPLES_AND_FRAMEWORKS
title: Principles and Decision Frameworks
type: documentation
owner: platform-team
status: active
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

- 01_adr_index
- 24_PR_GATES
- 43_OPERATING_PRINCIPLES

---

# Principles and Decision Frameworks

Doc contract:

- Purpose: Provide a hub for decision frameworks and where to apply them.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/00-foundations/43_OPERATING_PRINCIPLES.md, docs/adrs/01_adr_index.md, docs/80-onboarding/24_PR_GATES.md

This is a link-first guide. Use it to pick the right framework, then jump to
the canonical documents for execution.

## How to use this

1. Choose the decision type (strategy, architecture, operations, governance).
2. Use the "Apply when" and "Anchor docs" for that framework.
3. Record the outcome in ADRs, run logs, or checklists.

## Frameworks and where to apply them

### Architect Elevator (Gregor Hohpe)

Apply when: translating platform work into business outcomes or preparing ADRs.

Anchor docs:

- docs/50-observability/05_OBSERVABILITY_DECISIONS.md
- docs/50-observability/09_PLATFORM_DASHBOARD_CATALOG.md
- docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md
- docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md

### Abstractions vs Illusions (Hohpe)

Apply when: designing templates, contracts, or guardrails.

Anchor docs:

- docs/00-foundations/00_DESIGN_PHILOSOPHY.md
- docs/20-contracts/02_PLATFORM_BOUNDARIES.md
- docs/20-contracts/42_APP_TEMPLATE_LIVING.md

### Platform as Product

Apply when: prioritizing features and defining value propositions.

Anchor docs:

- docs/00-foundations/00_DESIGN_PHILOSOPHY.md
- docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md
- docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md

### Friction as Governance

Apply when: shaping behavior through gates, defaults, and templates.

Anchor docs:

- docs/80-onboarding/24_PR_GATES.md
- docs/10-governance/04_PR_GUARDRAILS.md
- docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md

### Operating Principles (Andy Grove)

Apply when: choosing metrics, removing bottlenecks, and defining reliability goals.

Anchor docs:

- docs/00-foundations/43_OPERATING_PRINCIPLES.md
- docs/40-delivery/41_BUILD_RUN_LOG.md
- docs/70-operations/10_INFRA_FAILURE_MODES.md

### Strategy Kernel (Rumelt)

Apply when: making large decisions or writing ADRs.

Anchor docs:

- docs/00-foundations/43_OPERATING_PRINCIPLES.md
- docs/adrs/01_adr_index.md

### DDD Boundaries and Ubiquitous Language

Apply when: defining scope, naming, and ownership boundaries.

Anchor docs:

- docs/20-contracts/02_PLATFORM_BOUNDARIES.md
- docs/10-governance/35_RESOURCE_TAGGING.md
- docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md

## Platform due-diligence checklist (mapped)

Use this as a readiness or audit lens. Each area maps to canonical docs.

| Area | Primary docs |
| --- | --- |
| Ownership and governance | docs/10-governance/01_GOVERNANCE.md, docs/adrs/01_adr_index.md |
| Architecture traceability | docs/adrs/01_adr_index.md, docs/30-architecture/04_REPO_STRUCTURE.md |
| Production readiness | docs/production-readiness-gates/READINESS_CHECKLIST.md |
| Observability and operability | docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/50-observability/09_PLATFORM_DASHBOARD_CATALOG.md |
| Security and risk posture | docs/60-security/28_SECURITY_FLOOR_V1.md, docs/60-security/SHARED_RESPONSIBILITY.md |
| Platform scope and clarity | docs/00-foundations/00_DESIGN_PHILOSOPHY.md, docs/20-contracts/02_PLATFORM_BOUNDARIES.md |
| Lifecycle and change safety | docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/70-operations/10_INFRA_FAILURE_MODES.md |
| Change management | docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md, docs/changelog/README.md |
| Dependency and coupling risk | docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md, docs/70-operations/36_STATE_KEY_STRATEGY.md |
| Knowledge transfer | docs/80-onboarding/23_NEW_JOINERS.md, docs/80-onboarding/25_DAY_ONE_CHECKLIST.md |
