---
type: governance-report
env: development
generated_at: 2026-01-25T11:54:26Z
source:
  branch: development
  sha: d723f90599539f570a79ea02e4fe3714cf3a879b
pipeline:
  workflow: Governance Registry Writer
  run_id: 21332166974
integrity:
  derived_only: true
---
<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 01_adr_index
title: metadata
type: adr
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
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_GOVERNANCE
  - ADR-0001-platform-argocd-as-gitops-operator
  - ADR-0002-platform-Kong-as-ingress-API-gateway
  - ADR-0003-platform-AWS-IAM-bootstrap-IRSA-SSM-
  - ADR-0004-platform-datree-policy-as-code-in-ci
  - ADR-0005-app-keycloak-as-identity-provider-for-human-sso
  - ADR-0006-platform-secrets-strategy
  - ADR-0007-platform-environment-model
  - ADR-0008-app-backstage-portal
  - ADR-0009-app-delivery-insights
  - ADR-0010-platform-terraform-lockfile-stability
  - ADR-0011-platform-ci-environment-contract
  - ADR-0012-platform-repo-decoupling-options
  - ADR-0013-platform-argo-app-management-approach
  - ADR-0014-platform-ci-local-preflight-checks
  - ADR-0015-platform-aws-oidc-for-github-actions
  - ADR-0016-platform-ci-environment-separation
  - ADR-0017-platform-policy-as-code
  - ADR-0018-platform-container-registry-standard
  - ADR-0019-platform-pre-commit-hooks
  - ADR-0020-platform-helm-kustomize-hybrid
  - ADR-0021-platform-pr-terraform-plan
  - ADR-0022-platform-post-apply-health-checks
  - ADR-0023-platform-ci-image-scanning
  - ADR-0024-platform-security-floor-v1
  - ADR-0025-platform-boundaries-contract
  - ADR-0026-platform-cd-deployment-contract
  - ADR-0027-platform-design-philosophy
  - ADR-0028-platform-dev-branch-gate
  - ADR-0029-platform-dev-plan-gate
  - ADR-0030-platform-precreated-iam-policies
  - ADR-0031-platform-bootstrap-irsa-service-accounts
  - ADR-0032-platform-eks-access-model
  - ADR-0033-platform-ci-orchestrated-modes
  - ADR-0034-platform-ci-environment-contract
  - ADR-0035-platform-iam-audit-cadence
  - ADR-0036-platform-orphan-cleanup-workflow
  - ADR-0037-platform-resource-tagging-policy
  - ADR-0038-platform-teardown-orphan-cleanup-gate
  - ADR-0039-platform-tag-scoped-iam-policy-template
  - ADR-0040-platform-lifecycle-aware-state-keys
  - ADR-0041-platform-orphan-cleanup-deletion-order
  - ADR-0042-platform-branching-strategy
  - ADR-0043-platform-teardown-lb-eni-wait
  - ADR-0044-platform-infra-checks-ref-mode
  - ADR-0045-platform-teardown-lb-delete-default
  - ADR-0046-platform-pr-plan-validation-ownership
  - ADR-0047-platform-teardown-destroy-timeout-retry
  - ADR-0048-platform-teardown-version-selector
  - ADR-0049-platform-pragmatic-observability-baseline
  - ADR-0050-platform-changelog-label-gate
  - ADR-0051-platform-reliability-metrics-contract-minimums
  - ADR-0052-platform-kube-prometheus-stack-bundle
  - ADR-0053-platform-storage-lifecycle-separation
  - ADR-0054-platform-observability-exporters-otel-split
  - ADR-0055-platform-tempo-tracing-backend
  - ADR-0056-platform-loki-deployment-mode
  - ADR-0057-platform-ci-terraform-force-unlock-workflow
  - ADR-0058-platform-grafana-config-workflow
  - ADR-0059-platform-ci-workflow-index-and-ownership
  - ADR-0060-platform-ephemeral-update-workflow
  - ADR-0061-platform-observability-provisioning-boundary
  - ADR-0062-platform-app-template-contract
  - ADR-0063-platform-terraform-helm-bootstrap
  - ADR-0064-platform-dev-bootstrap-defaults
  - ADR-0065-platform-branch-policy-guard
  - ADR-0066-platform-dashboards-as-code
  - ADR-0067-platform-labeler-base-ref
  - ADR-0068-platform-review-cadence-output
  - ADR-0069-platform-observability-baseline-golden-signals
  - ADR-0070-platform-terraform-aws-lb-controller
  - ADR-0071-doc-taxonomy-refactor
  - ADR-0072-platform-pr-checklist-template
  - ADR-0073-platform-bootstrap-v3-irsa-skip
  - ADR-0074-platform-ops-workflow-branch-guard
  - ADR-0075-app-example-deployments
  - ADR-0076-platform-infracost-ci-visibility
  - ADR-0077-platform-ci-build-teardown-log-automation
  - ADR-0078-platform-governed-repo-scaffolder
  - ADR-0079-platform-ai-agent-governance
  - ADR-0080-platform-github-agent-roles
  - ADR-0081-platform-repo-wide-linting
  - ADR-0082-platform-metadata-validation
  - ADR-0083-platform-metadata-backfill-protocol
  - ADR-0084-platform-enhanced-metadata-schema
  - ADR-0085-score-implementation
  - ADR-0086-federated-metadata-validation
  - ADR-0087-k8s-metadata-sidecars
  - ADR-0088-automated-metadata-remediation
  - ADR-0089-closed-loop-metadata-injection
  - ADR-0090-automated-platform-health-dashboard
  - ADR-0092-ecr-registry-product-strategy
  - ADR-0093-automated-policy-enforcement
  - ADR-0094-automated-catalog-docs
  - ADR-0095-self-service-registry-creation
  - ADR-0096-risk-based-ecr-controls
  - ADR-0097-domain-based-resource-catalogs
  - ADR-0098-standardized-pr-gates
  - ADR-0099-standardized-iam-policy-management
  - ADR-0100-standardized-ecr-lifecycle-and-documentation
  - ADR-0101-pr-metadata-auto-heal
  - ADR-0102
  - ADR-0103-automated-workflow-docs
  - ADR-0104-automated-script-docs
  - ADR-0110-idp-knowledge-graph-architecture
  - ADR-0111-platform-documentation-auto-healing
  - ADR-0112-automated-adr-index-generation
  - ADR-0113-platform-queryable-intelligence-enums
  - ADR-0114-automated-enum-consistency-validation
  - ADR-0115-enhanced-enum-validation-engine
  - ADR-0116-emoji-usage-policy-and-enforcement
  - ADR-0117-conclusive-governance-routing-architecture
  - ADR-0118-config-driven-metadata-governance
  - ADR-0119-grand-metadata-healing-and-contextual-alignment
  - ADR-0120-metadata-inheritance-and-active-governance
  - ADR-0121-value-quantification-framework
  - ADR-0122
  - ADR-0123
  - ADR-0124
  - ADR-0125
  - ADR-0126
  - ADR-0127
  - ADR-0128
  - ADR-0129
  - ADR-0130
  - ADR-0131
  - ADR-0132
  - ADR-0133
  - ADR-0134-metadata-inheritance-active-governance-and-leak-protection
  - ADR-0135
  - ADR-0136
  - ADR-0137
  - ADR-0138
  - ADR-0139
  - ADR-0140
  - ADR-0141
  - ADR-0142
  - ADR-0143
  - ADR-0144
  - ADR-0145
  - ADR-0146
  - ADR-0147
  - ADR-0148-seamless-build-deployment-with-immutability
  - ADR-0153
  - ADR-0154
  - ADR-0155-ci-governance-registry-fetch
  - ADR-0156-platform-ci-build-timing-capture
  - ADR-0157-platform-multi-tenant-rds-architecture
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0159-backstage-catalog-registry-sync
  - ADR-0160
  - ADR-0161
  - ADR-0162
  - ADR-0163
  - ADR-0164-teardown-v3-enhanced-reliability
  - ADR-0165
  - ADR-0166
  - ADR-0167
  - ADR-0168
  - ADR-0169
  - ADR-0170
  - ADR-0171-platform-application-packaging-strategy
  - ADR-0172-cd-promotion-strategy-with-approval-gates
  - ADR-0173-governance-doc-naming-migration
  - ADR-0174-pipeline-decoupling-from-cluster-bootstrap
  - ADR_INDEX_AUTOMATION_SPEC
  - AUTO_HEALING_GUIDE
  - CL-0068-adr-index-automation
  - HEALTH_AUDIT_LOG
  - PLATFORM_DASHBOARDS
  - PLATFORM_HEALTH
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
---

id: 01_adr_index
title: ADR Index (GoldenPath IDP)
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
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to:
<!-- ADR_RELATE_START -->

<!-- ADR_RELATE_END -->
---

## ADR Index (GoldenPath IDP)

This index lists Architecture Decision Records (ADRs) for GoldenPath IDP.

## How to use this

- ADRs document **what we decided**, **why**, and **tradeoffs**.
- Decisions should be changed by **superseding** an ADR (create a new one), not rewriting history.

> Location:`docs/adrs/`

---

## Active ADRs

<!-- ADR_TABLE_START -->

<!-- ADR_TABLE_END -->

---

## Superseded ADRs

- [ADR-0069](ADR-0069-platform-observability-baseline-golden-signals.md) — superseded by`ADR-0049-platform-pragmatic-observability-baseline.md`.
- [ADR-0036](ADR-0036-platform-orphan-cleanup-workflow.md) — superseded by`ADR-0038-platform-teardown-orphan-cleanup-gate.md`.
- [ADR-0043](ADR-0043-platform-teardown-lb-eni-wait.md) — superseded by`ADR-0045-platform-teardown-lb-delete-default.md`.
- [ADR-0044](ADR-0044-platform-infra-checks-ref-mode.md) — superseded by`ADR-0046-platform-pr-plan-validation-ownership.md`.
- [ADR-0103](ADR-0103-automated-workflow-docs.md) — superseded by`ADR-0111-platform-documentation-auto-healing.md`.
- [ADR-0104](ADR-0104-automated-script-docs.md) — superseded by`ADR-0111-platform-documentation-auto-healing.md`.

Legacy aliases (kept to preserve historical links):

-`docs/adrs/ADR-0011-platform-ci-environment-contract.md`→`ADR-0034-platform-ci-environment-contract.md`

---

## New ADRs

When introducing a new ADR:

- Follow the Domain convention (Platform or Application).
- Use the filename pattern:`ADR-XXXX-(platform|app)-short-title.md`.
- Add the entry to the Active ADRs table with its Domain.

---

## Conventions

- **Numbering:**`ADR-0001`,`ADR-0002`, … (sequential, never reused)
- **Filename:**`ADR-XXXX-(platform|app)-short-title.md`
- **Domain:**`Platform`or`Application`
- **Status values:**`Proposed`,`Accepted`,`Deprecated`,`Superseded`
- **Changing a decision:** write a new ADR that **supersedes** the old one and link both.

---

## Adding a new ADR

1. Copy the standard template.

2. Create`docs/adrs/ADR-XXXX-(platform|app)-title.md`.

3. Fill in Domain, context, decision, tradeoffs, and follow-ups.

4. Open a PR.

5. Update this index.
