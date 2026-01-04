---
id: 44_DOC_TIGHTENING_PLAN
title: Documentation Tightening Plan (V1)
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
relates_to: []
---

# Documentation Tightening Plan (V1)

Doc contract:
- Purpose: Reduce duplication, make doc relationships explicit, and keep living docs current.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/90-doc-system/00_DOC_INDEX.md, docs/90-doc-system/30_DOCUMENTATION_FRESHNESS.md

## Goals

- Establish one source of truth per topic.
- Make relationships between docs, ADRs, and runbooks explicit.
- Keep living docs current via the doc index and review cadence.

## Relationship rules

- Living docs define the current, enforced stance.
- ADRs capture rationale and tradeoffs for decisions.
- Runbooks capture operational recovery steps.
- The doc index is the authoritative list for living docs.

## Topic map (current)

| Topic | Canonical doc | Supporting docs | ADRs / Runbooks |
| --- | --- | --- | --- |
| Governance | docs/10-governance/01_GOVERNANCE.md | docs/10-governance/02_GOVERNANCE_MODEL.md, docs/10-governance/03_GOVERNANCE_BACKSTAGE.md | docs/adrs/ADR-0008-app-backstage-portal.md |
| Platform boundaries | docs/20-contracts/02_PLATFORM_BOUNDARIES.md | docs/20-contracts/42_APP_TEMPLATE_LIVING.md | docs/adrs/ADR-0025-platform-boundaries-contract.md |
| CI environment contract | docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md | docs/20-contracts/20_CI_ENVIRONMENT_SEPARATION.md, ci-workflows/CI_WORKFLOWS.md | docs/adrs/ADR-0034-platform-ci-environment-contract.md |
| GitOps + CD | docs/40-delivery/12_GITOPS_AND_CICD.md, docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md | docs/40-delivery/26_POST_APPLY_HEALTH_CHECKS.md | docs/adrs/ADR-0001-platform-argocd-as-gitops-operator.md, docs/adrs/ADR-0026-platform-cd-deployment-contract.md |
| Observability | docs/50-observability/05_OBSERVABILITY_DECISIONS.md | docs/50-observability/41_STORAGE_AND_PERSISTENCE.md | docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md, docs/adrs/ADR-0056-platform-loki-deployment-mode.md |
| Teardown | docs/70-operations/15_TEARDOWN_AND_CLEANUP.md | docs/70-operations/10_INFRA_FAILURE_MODES.md | docs/adrs/ADR-0043-platform-teardown-lb-eni-wait.md, docs/runbooks/09_CI_TEARDOWN_RECOVERY_V2.md |
| Security floor | docs/60-security/28_SECURITY_FLOOR_V1.md | docs/60-security/27_CI_IMAGE_SCANNING.md | docs/adrs/ADR-0024-platform-security-floor-v1.md |
| Tagging | docs/10-governance/35_RESOURCE_TAGGING.md | docs/policies/01_TAG_SCOPED_POLICY_TEMPLATE.md | docs/adrs/ADR-0037-platform-resource-tagging-policy.md |
| App template | docs/20-contracts/42_APP_TEMPLATE_LIVING.md | apps/fast-api-app-template/README.md | docs/adrs/ADR-0062-platform-app-template-contract.md |

## Immediate changes (this update)

- Add a doc contract header to key docs (purpose, owner, status, cadence, related).
- Add cross-links in doc headers to clarify relationships.
- Update the doc index to include newly tracked living docs.

## Future cleanup backlog

- Rename docs/03_GOVERNENCE_BACKSTAGE.md to docs/10-governance/03_GOVERNANCE_BACKSTAGE.md and update references.
- Consider promoting docs/50-observability/05_OBSERVABILITY_DECISIONS.md to the living doc index.
- Consolidate governance matrices so only one doc carries the canonical table.
- Standardize titles and naming for numbered docs (case, spelling, prefixes).
