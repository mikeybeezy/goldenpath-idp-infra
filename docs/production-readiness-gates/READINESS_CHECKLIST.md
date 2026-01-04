---
id: READINESS_CHECKLIST
title: 'V1_05: Platform Due-Diligence Scorecard'
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
- 01_GOVERNANCE
- 37_V1_SCOPE_AND_TIMELINE
- ADR-0040
- ADR-0044
- ADR-0046
- ADR-0063
- CL-0002
------

# V1_05: Platform Due-Diligence Scorecard

Doc contract:
- Purpose: Periodic assessment of platform maturity and buyer risk.
- Owner: platform
- Status: living
- Review cadence: 30d
- Last reviewed: 2026-01-02
- Related: docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md, docs/10-governance/01_GOVERNANCE.md

## Scoring

Scale:
- 1 = missing
- 2 = weak
- 3 = partial
- 4 = strong
- 5 = excellent

Update this scorecard every 30 days or after major platform changes. The intent
is to keep decision readiness visible and traceable.

## 1) Ownership & Governance (3/5)

Evidence:
- docs/10-governance/01_GOVERNANCE.md
- docs/00-foundations/43_OPERATING_PRINCIPLES.md
- docs/40-delivery/38_BRANCHING_STRATEGY.md

Gaps:
- Escalation paths and change-management ownership are not explicit.
- Approval authority still feels person-dependent.

Recommendations:
- Add a short escalation matrix (platform owner, backup, decision quorum).
- Record governance change workflow (who approves, how, and where).

## 2) Architecture & Decision Traceability (4/5)

Evidence:
- docs/adrs/01_adr_index.md
- docs/adrs/02_adr_template.md

Gaps:
- Superseded ADR convention is not consistent (no uniform "Superseded by").

Recommendations:
- Standardize ADR supersedence text in the template and backfill key ADRs.

## 3) Production Readiness & Reliability (3/5)

Evidence:
- docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md
- docs/70-operations/10_INFRA_FAILURE_MODES.md
- docs/70-operations/15_TEARDOWN_AND_CLEANUP.md

Gaps:
- Readiness is documented but not enforced as a hard gate in every PR.
- Rollback guidance is present but not a standardized requirement in PRs.

Recommendations:
- Require a readiness checklist selection in the PR template (done).
- Add a single "rollback note required for infra/CI/bootstrap changes" rule.

## 4) Observability & Operability (3/5)

Evidence:
- docs/50-observability/05_OBSERVABILITY_DECISIONS.md
- docs/50-observability/41_STORAGE_AND_PERSISTENCE.md
- docs/runbooks/README.md

Gaps:
- Alert ownership and on-call expectations are not explicit.
- Runbook indexing exists but ownership mapping is not standardized.

Recommendations:
- Add an "alert ownership" section to observability docs.
- Add on-call expectations to a single ops contract doc.

## 5) Security & Risk Posture (3/5)

Evidence:
- docs/60-security/28_SECURITY_FLOOR_V1.md
- docs/60-security/31_EKS_ACCESS_MODEL.md
- docs/60-security/33_IAM_ROLES_AND_POLICIES.md

Gaps:
- Shared responsibility model is not consolidated in one authoritative doc.
- Audit logging expectations are implied rather than explicit.

Recommendations:
- Publish docs/60-security/SHARED_RESPONSIBILITY.md.
- Add a short audit logging expectation statement to the security floor doc.

## 6) Platform Scope & Product Clarity (4/5)

Evidence:
- docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md
- docs/20-contracts/02_PLATFORM_BOUNDARIES.md
- docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md

Gaps:
- Service catalog is scoped but not operationally enforced yet.

Recommendations:
- Publish a minimum service catalog set and ownership metadata rules.

## 7) Lifecycle, Upgrades & Change Safety (2/5)

Evidence:
- docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md
- docs/70-operations/36_STATE_KEY_STRATEGY.md

Gaps:
- No documented upgrade/deprecation policy or compatibility window.
- No published change window expectations.

Recommendations:
- Create a V1 upgrade and deprecation policy (1 page).
- Add a cadence for breaking change announcements.

## 8) Change Management & Release Discipline (3/5)

Evidence:
- docs/90-doc-system/40_CHANGELOG_GOVERNANCE.md
- docs/changelog/CHANGELOG_LABELS.md

Gaps:
- Emergency change process is not formalized.
- PR review requirement on main is intentionally off.

Recommendations:
- Add a short emergency change process note.
- Decide when to enable PR reviews on main.

## 9) Dependency & Platform Coupling Risk (3/5)

Evidence:
- docs/adrs/ADR-0040-platform-lifecycle-aware-state-keys.md
- docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md

Gaps:
- Vendor exit/migration constraints are not clearly documented.

Recommendations:
- Add a short "exit constraints" section to architecture docs.

## 10) People Independence & Knowledge Transfer (4/5)

Evidence:
- docs/runbooks/README.md
- docs/80-onboarding/23_NEW_JOINERS.md
- docs/90-doc-system/00_DOC_INDEX.md

Gaps:
- Support model and escalation ownership are not explicit.

Recommendations:
- Publish a support model (who owns triage, escalation path).

## References to recent fixes

- Infra checks workflow is manual-only:
  - docs/adrs/ADR-0046-platform-pr-plan-validation-ownership.md
  - docs/adrs/ADR-0044-platform-infra-checks-ref-mode.md
  - docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md
- Bootstrap resolution:
  - docs/adrs/ADR-0063-platform-terraform-helm-bootstrap.md
  - docs/changelog/entries/CL-0002-bootstrap-refactor.md
  - docs/40-delivery/27_REFACTORING_VALIDATION_GUIDE.md
