# Documentation Index (Living)

Doc contract:
- Purpose: Track living docs and review metadata for freshness checks.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md

This file is the source of truth for living documents that must stay current.
It is used by the doc freshness validator to flag stale or missing reviews.

## Living docs

| Doc | Owner | Review cycle | Last reviewed | Notes |
| --- | --- | --- | --- | --- |
| docs/00-foundations/00_DESIGN_PHILOSOPHY.md | platform | 90d | 2025-12-27 | Core origin and product philosophy |
| docs/10-governance/01_GOVERNANCE.md | platform | 90d | 2025-12-31 | Governance principles and rules |
| docs/10-governance/04_PR_GUARDRAILS.md | platform | 90d | 2026-01-02 | PR guardrails, labels, and enforcement |
| docs/20-contracts/02_PLATFORM_BOUNDARIES.md | platform | 90d | 2025-12-31 | Platform vs team contract |
| docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md | platform | 90d | 2026-01-01 | CI environment separation summary |
| docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md | platform | 90d | 2025-12-31 | CI environment inputs and guarantees |
| ci-workflows/CI_WORKFLOWS.md | platform | 90d | 2026-01-01 | Workflow index with owners and runbooks |
| docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md | platform | 90d | 2025-12-27 | CD expectations and promotion model |
| docs/60-security/28_SECURITY_FLOOR_V1.md | platform | 90d | 2025-12-27 | V1 security floor checklist |
| docs/80-onboarding/23_NEW_JOINERS.md | platform | 90d | 2025-12-27 | Onboarding and local preflight rules |
| docs/80-onboarding/24_PR_GATES.md | platform | 90d | 2026-01-02 | PR gate overview and unblock guidance |
| docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md | platform | 90d | 2025-12-27 | Doc freshness mechanism |
| docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md | platform | 90d | 2026-01-01 | State backend, locking, and CI access paths |
| docs/70-operations/36_STATE_KEY_STRATEGY.md | platform | 90d | 2025-12-29 | Lifecycle-aware state key usage |
| docs/00-foundations/34_PLATFORM_SUCCESS_CHECKLIST.md | platform | 30d | 2026-01-02 | Baseline success checklist (living) |
| docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md | platform | 90d | 2025-12-29 | V1 vs V1.1 scope and delivery checklist |
| docs/40-delivery/38_BRANCHING_STRATEGY.md | platform | 90d | 2025-12-29 | Branching strategy and promotion flow |
| docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md | platform | 90d | 2025-12-30 | End-to-end PR → apply → bootstrap → teardown validation |
| docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md | platform | 90d | 2025-12-31 | Changelog policy and enforcement |
| docs/changelog/CHANGELOG_LABELS.md | platform | 90d | 2025-12-31 | Changelog label definitions and rules |
| docs/10-governance/35_RESOURCE_TAGGING.md | platform | 90d | 2026-01-01 | Tagging contract and cleanup implications |
| docs/50-observability/41_STORAGE_AND_PERSISTENCE.md | platform | 90d | 2025-12-31 | Storage defaults, persistence requirements, and tradeoffs |
| docs/20-contracts/42_APP_TEMPLATE_LIVING.md | platform | 90d | 2025-12-31 | App template structure and ownership boundaries |
| docs/00-foundations/43_OPERATING_PRINCIPLES.md | platform | 90d | 2026-01-01 | Grove-inspired operating principles |
| docs/90-doc-system/44_DOC_TIGHTENING_PLAN.md | platform | 90d | 2026-01-01 | Doc relationships and consolidation plan |
| docs/production-readiness-gates/ROADMAP.md | platform | 30d | 2026-01-02 | Monthly platform backlog review |
| docs/production-readiness-gates/V1_04_CAPABILITY_MATRIX.md | platform | 30d | 2026-01-02 | Capability matrix with status updates |
| docs/production-readiness-gates/READINESS_CHECKLIST.md | platform | 30d | 2026-01-02 | Periodic due-diligence assessment and gaps |
| docs/00-foundations/10_PLATFORM_REQUIREMENTS.md | platform | 90d | 2026-01-02 | Formal platform requirements |
| docs/20-contracts/01_PLATFORM_SERVICE_AGREEMENT.md | platform | 90d | 2026-01-02 | Platform SLA/SLO agreement |
| docs/20-contracts/10_SERVICE_CATALOG.md | platform | 90d | 2026-01-02 | Supported services and add-ons |
| docs/70-operations/01_LIFECYCLE_POLICY.md | platform | 90d | 2026-01-02 | Lifecycle and upgrade policy |
