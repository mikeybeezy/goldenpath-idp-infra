---
type: governance-report
env: development
generated_at: 2026-01-21T02:16:34Z
source:
  branch: development
  sha: d64a69b4c4731bf920494df4c309dad6bba32791
pipeline:
  workflow: Governance Registry Writer
  run_id: 21194772316
integrity:
  derived_only: true
---
---
id: 01_adr_index
title: metadata
type: adr
domain: platform-core
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
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
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
  - ADR-0001
  - ADR-0002
  - ADR-0003
  - ADR-0004
  - ADR-0005
  - ADR-0006
  - ADR-0007
  - ADR-0008
  - ADR-0009
  - ADR-0010
  - ADR-0011
  - ADR-0012
  - ADR-0013
  - ADR-0014
  - ADR-0015
  - ADR-0016
  - ADR-0017
  - ADR-0018
  - ADR-0019
  - ADR-0020
  - ADR-0021
  - ADR-0022
  - ADR-0023
  - ADR-0024
  - ADR-0025
  - ADR-0026
  - ADR-0027
  - ADR-0028
  - ADR-0029
  - ADR-0030
  - ADR-0031
  - ADR-0032
  - ADR-0033
  - ADR-0034
  - ADR-0035
  - ADR-0036
  - ADR-0037
  - ADR-0038
  - ADR-0039
  - ADR-0040
  - ADR-0041
  - ADR-0042
  - ADR-0043
  - ADR-0044
  - ADR-0045
  - ADR-0046
  - ADR-0047
  - ADR-0048
  - ADR-0049
  - ADR-0050
  - ADR-0051
  - ADR-0052
  - ADR-0053
  - ADR-0054
  - ADR-0055
  - ADR-0056
  - ADR-0057
  - ADR-0058
  - ADR-0059
  - ADR-0060
  - ADR-0061
  - ADR-0062
  - ADR-0063
  - ADR-0064
  - ADR-0065
  - ADR-0066
  - ADR-0067
  - ADR-0068
  - ADR-0069
  - ADR-0070
  - ADR-0071
  - ADR-0072
  - ADR-0073
  - ADR-0074
  - ADR-0075
  - ADR-0076
  - ADR-0077
  - ADR-0078
  - ADR-0079
  - ADR-0080
  - ADR-0081
  - ADR-0082
  - ADR-0083
  - ADR-0084
  - ADR-0085
  - ADR-0086
  - ADR-0087
  - ADR-0088
  - ADR-0089
  - ADR-0090
  - ADR-0092
  - ADR-0093
  - ADR-0094
  - ADR-0095
  - ADR-0096
  - ADR-0097
  - ADR-0098
  - ADR-0099
  - ADR-0100
  - ADR-0101
  - ADR-0102
  - ADR-0103
  - ADR-0104
  - ADR-0110
  - ADR-0111
  - ADR-0112
  - ADR-0113
  - ADR-0114
  - ADR-0115
  - ADR-0116
  - ADR-0117
  - ADR-0118
  - ADR-0119
  - ADR-0120
  - ADR-0121
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
  - ADR-0134
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
  - ADR-0148
  - ADR-0153
  - ADR-0154
  - ADR-0155
  - ADR-0156
  - ADR-0157
  - ADR-0158
  - ADR-0159
  - ADR-0160
  - ADR-0161
  - ADR-0162
  - ADR-0163
  - ADR-0164
  - ADR-0165
  - ADR-0166
  - ADR-0167
  - ADR-0168
  - ADR-0169
  - ADR-0170
  - ADR-0170
  - ADR-0171
  - ADR-0172
  - ADR-0173
  - ADR-0174
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
| [ADR-0001](ADR-0001-platform-argocd-as-gitops-operator.md) | Platform | Adopt Argo CD as GitOps controller for platform deployments | Active | 2026-01-0? | We need a deterministic, auditable mechanism to deploy and reconcile platform components (Kong, cert-manager, autoscaler, etc.) on EKS. |
| [ADR-0002](ADR-0002-platform-Kong-as-ingress-API-gateway.md) | Platform | Use Kong as the primary ingress/API gateway behind an internal NLB | Active | 2026-01-0? | We need a consistent “front door” for platform and workloads on EKS. |
| [ADR-0003](ADR-0003-platform-AWS-IAM-bootstrap-IRSA-SSM-.md) | Platform | Use AWS IAM for bootstrap access, IRSA for pod-to-AWS access, and SSM for node break-glass | Active | 2026-01-0? | We need secure and deterministic access patterns: |
| [ADR-0004](ADR-0004-platform-datree-policy-as-code-in-ci.md) | Platform | Use Datree as Kubernetes policy-as-code gate in CI | Active | 2026-01-0? | We need governance that is opinionated but not authoritarian: |
| [ADR-0005](ADR-0005-app-keycloak-as-identity-provider-for-human-sso.md) | Platform | Adopt Keycloak for platform SSO (humans) and keep IRSA for pod-to-AWS auth | Active | 2026-01-0? | We want a consistent identity layer for platform UIs and developer experience: |
| [ADR-0006](ADR-0006-platform-secrets-strategy.md) | Platform | Use AWS Secrets Manager/SSM as system of record for secrets and External Secrets to hydrate Kubernetes | Active | 2026-01-0? | The platform is frequently rebuilt and clusters are disposable. Any secret stored only inside the cluster risks loss and encourages manual fixes. |
| [ADR-0007](ADR-0007-platform-environment-model.md) | Platform | Adopt an environment model that balances cost, iteration speed, and credible separation | Active | 2026-01-0? | We want a V1 platform that demonstrates: |
| [ADR-0008](ADR-0008-app-backstage-portal.md) | Platform | Use Backstage as the developer portal and the V1 demo application for env promotion | Active | 2026-01-0? | We want the IDP to feel like a product, not just installed tooling. We also need a credible demonstration that: |
| [ADR-0009](ADR-0009-app-delivery-insights.md) | Platform | CI/CD observability via OpenTelemetry ("Delivery Insights") | Active | 2026-01-0? | Delivery (build → package → promote) represents a significant portion of value creation in the platform. Traditional CI feedback (pass/fail + logs) is insufficient to: |
| [ADR-0010](ADR-0010-platform-terraform-lockfile-stability.md) | Platform | Enforce Terraform lockfile stability in CI | Active | 2026-01-0? | CI should validate infrastructure code exactly as reviewed and committed. Allowing CI to upgrade providers or modules introduces drift and can cause changes in behavior that were not explicitly app... |
| [ADR-0011](ADR-0011-platform-ci-environment-contract.md) | Platform | CI Environment Contract (Superseded) | Active | 2026-01-0? | No context provided. |
| [ADR-0012](ADR-0012-platform-repo-decoupling-options.md) | Platform | Repo decoupling options for infra and platform tooling | Active | 2026-01-0? | We need to plan how to separate infrastructure and platform tooling repositories once the platform stabilizes. Today everything lives in one monorepo, which is simple but mixes ownership and expand... |
| [ADR-0013](ADR-0013-platform-argo-app-management-approach.md) | Platform | Argo CD app management approach for current scale | Active | 2026-01-0? | We need to decide how to manage Argo CD applications in production. The two options are: |
| [ADR-0014](ADR-0014-platform-ci-local-preflight-checks.md) | Platform | Local preflight checks before PRs | Active | 2026-01-0? | We want consistent, low-friction quality gates while avoiding false confidence from local tooling that does not perfectly match CI. Teams should run fast, local checks before opening PRs, but CI re... |
| [ADR-0015](ADR-0015-platform-aws-oidc-for-github-actions.md) | Platform | Use AWS OIDC for GitHub Actions authentication | Active | 2026-01-0? | GitHub Actions currently needs AWS credentials to run infrastructure workflows. Long-lived access keys stored as GitHub secrets increase the risk of leakage and require rotation. We want a safer, a... |
| [ADR-0016](ADR-0016-platform-ci-environment-separation.md) | Platform | CI environment separation and manual promotion gates | Active | 2026-01-0? | We need a CI/CD model that scales safely from early-stage usage to later growth without frequent rework. Infrastructure changes must be reviewed, environment-scoped, and applied with explicit human... |
| [ADR-0017](ADR-0017-platform-policy-as-code.md) | Platform | Policy as code for infrastructure and application changes | Active | 2026-01-0? | As the platform scales, we need consistent guardrails that prevent unsafe infrastructure and application changes without relying solely on manual review. With Backstage as our first client, we must... |
| [ADR-0018](ADR-0018-platform-container-registry-standard.md) | Platform | Container registry standard — ECR default, GHCR supported, Docker Hub discouraged | Active | 2026-01-0? | GoldenPath V1 targets an AWS-first, EKS-based platform with: |
| [ADR-0019](ADR-0019-platform-pre-commit-hooks.md) | Platform | Pre-commit hooks as local quality gates | Active | 2026-01-0? | We want fast, consistent feedback for contributors before changes reach CI. Local pre-commit hooks can prevent common formatting and lint issues while keeping the CI pipeline authoritative. The pla... |
| [ADR-0020](ADR-0020-platform-helm-kustomize-hybrid.md) | Platform | Hybrid GitOps approach with Helm and Kustomize | Superseded | 2026-01-0? | The repo already includes Helm-based GitOps and Kustomize overlays. We want a consistent, scalable approach that keeps packaging benefits for third-party tools while making environment-specific cha... |
| [ADR-0021](ADR-0021-platform-pr-terraform-plan.md) | Platform | PR Terraform plan with automated comments | Active | 2026-01-0? | We want Terraform plan feedback on pull requests without introducing Atlantis or requiring manual copy/paste. The goal is to surface infrastructure changes early while keeping apply manual and cont... |
| [ADR-0022](ADR-0022-platform-post-apply-health-checks.md) | Platform | Post-apply health checks for platform readiness | Active | 2026-01-0? | Terraform apply and bootstrap do not guarantee that the platform is usable. We need a deterministic, binary signal that the environment is healthy after apply so that promotions and demos are safe ... |
| [ADR-0023](ADR-0023-platform-ci-image-scanning.md) | Platform | CI image scanning standard | Active | 2026-01-0? | We need a registry-agnostic image vulnerability gate in CI. The platform should provide a default scanner that works with ECR, GHCR, or other registries, while keeping future options open. |
| [ADR-0024](ADR-0024-platform-security-floor-v1.md) | Platform | Security floor for V1 | Active | 2026-01-0? | We need a minimal, non-negotiable security baseline that reduces catastrophic risk without slowing delivery. V1 must be secure-by-default and leave heavier DevSecOps capabilities to V2. |
| [ADR-0025](ADR-0025-platform-boundaries-contract.md) | Platform | Platform boundaries and contract | Active | 2026-01-0? | The platform and workload planes must be separated explicitly to avoid duplicate governance and confusion. A clear contract defines what the platform guarantees and what teams own. |
| [ADR-0026](ADR-0026-platform-cd-deployment-contract.md) | Platform | CD deployment contract | Active | 2026-01-0? | GoldenPath uses GitOps-based continuous deployment to apply and reconcile desired state across environments. We need to make deployment expectations explicit to ensure deterministic promotion, clea... |
| [ADR-0027](ADR-0027-platform-design-philosophy.md) | Platform | Platform design philosophy and reference implementation | Active | 2026-01-0? | GoldenPath is intended to be operable without a single maintainer and usable by humans and machines. That requires durable, explicit documentation and a clear statement of the platform’s founding p... |
| [ADR-0028](ADR-0028-platform-dev-branch-gate.md) | Platform | Dev branch gate before main | Active | 2026-01-0? | We want quality gates that prove changes run in a real environment before they reach`main`. Relying solely on plans or post-merge applies weakens the value of the dev environment as a gate. A simpl... |
| [ADR-0029](ADR-0029-platform-dev-plan-gate.md) | Platform | Dev plan gate before dev apply | Active | 2026-01-0? | The dev apply workflow currently checks for any successful plan on the same SHA. Because the plan workflow supports multiple environments, a non-dev plan can unlock a dev apply. This weakens the de... |
| [ADR-0030](ADR-0030-platform-precreated-iam-policies.md) | Platform | Pre-create IAM policies for IRSA controllers in V1 | Active | 2026-01-0? | The Terraform apply role used by GitHub Actions is intentionally scoped and cannot create IAM policies. Some IRSA controller roles (Cluster Autoscaler, AWS Load Balancer Controller) require custom ... |
| [ADR-0031](ADR-0031-platform-bootstrap-irsa-service-accounts.md) | Platform | Create IRSA service accounts during bootstrap | Active | 2026-01-0? | The AWS Load Balancer Controller and Cluster Autoscaler require IRSA-backed service accounts to exist before the controllers are installed. Early runs failed when the controllers were installed fir... |
| [ADR-0032](ADR-0032-platform-eks-access-model.md) | Platform | EKS access model (bootstrap admin vs steady-state access) | Active | 2026-01-0? | EKS grants cluster-admin access to the IAM principal that creates the cluster. In our case, that is the GitHub Actions bootstrap role. This is useful for initial provisioning, but it is a risk if l... |
| [ADR-0033](ADR-0033-platform-ci-orchestrated-modes.md) | Platform | CI orchestrated modes for infra lifecycle | Active | 2026-01-0? | The infra lifecycle requires multiple phases (apply, bootstrap, teardown). When operators must manually toggle flags, the workflow becomes brittle and error-prone. We saw repeated failures caused b... |
| [ADR-0034](ADR-0034-platform-ci-environment-contract.md) | Platform | CI Environment Contract | Active | 2026-01-0? | GoldenPath relies on CI pipelines to provision infrastructure, bootstrap clusters, deploy platform tooling, and tear environments down deterministically. As the system evolved, pipeline behavior be... |
| [ADR-0035](ADR-0035-platform-iam-audit-cadence.md) | Platform | IAM Audit Cadence for CI Roles | Active | 2026-01-0? | CI roles are intentionally broad during early iterations to keep the platform moving. Over time, unused permissions should be removed to reduce risk and increase confidence in least-privilege acces... |
| [ADR-0036](ADR-0036-platform-orphan-cleanup-workflow.md) | Platform | Orphan Cleanup Is Manual and Decoupled From Teardown | Superseded | 2026-01-0? | CI teardown can hang or fail when orphan cleanup is executed inline, especially when tagging permissions or AWS eventual consistency create long-running or retry-heavy cleanup loops. This reduces c... |
| [ADR-0037](ADR-0037-platform-resource-tagging-policy.md) | Platform | Platform resource tagging policy | Active | 2026-01-0? | GoldenPath creates and tears down short-lived environments frequently. Without consistent tags, it is difficult to audit cost, identify owners, and safely clean up orphans. We already rely on tags ... |
| [ADR-0038](ADR-0038-platform-teardown-orphan-cleanup-gate.md) | Platform | Gate Orphan Cleanup in CI Teardown with Explicit Modes | Active | 2026-01-0? | Teardown reliability is the weakest part of the infra lifecycle. We have seen teardown loops hang when GitOps recreates LoadBalancer Services and when orphan cleanup takes too long or is ambiguous ... |
| [ADR-0039](ADR-0039-platform-tag-scoped-iam-policy-template.md) | Platform | Tag-Scoped IAM Policy Template for Destructive Automation | Active | 2026-01-0? | Teardown and cleanup automation requires destructive permissions. Broad IAM policies raise the risk of deleting unintended resources, especially in shared accounts. We already enforce a platform-wi... |
| [ADR-0040](ADR-0040-platform-lifecycle-aware-state-keys.md) | Platform | Lifecycle-aware Terraform state keys for BuildId isolation | Active | 2026-01-0? | Ephemeral builds were reusing the persistent Terraform state key. New BuildIds would still load old state, leading to stale plans, drift reconciliation, and accidental reuse of resources. We need a... |
| [ADR-0041](ADR-0041-platform-orphan-cleanup-deletion-order.md) | Platform | Deterministic orphan cleanup deletion order | Active | 2026-01-0? | Orphan cleanup can fail when AWS resources are deleted out of dependency order (for example, trying to delete a subnet that still has ENIs or a route table that is still associated). We need a dete... |
| [ADR-0042](ADR-0042-platform-branching-strategy.md) | Platform | Branching strategy (development → main) | Active | 2026-01-0? | We need a simple, enforced branching model that keeps`main`stable and prevents direct merges from ad hoc branches. Recent work involved multiple short-lived branches, so we need a clear, documented... |
| [ADR-0043](ADR-0043-platform-teardown-lb-eni-wait.md) | Platform | Teardown waits for LoadBalancer ENIs before subnet delete | Superseded | 2026-01-0? | Teardown has been hanging at subnet deletion because network load balancer ENIs remain after Kubernetes LoadBalancer Services are deleted. Terraform destroy or AWS deletes then fail with`Dependency... |
| [ADR-0044](ADR-0044-platform-infra-checks-ref-mode.md) | Platform | Configurable ref for infra checks dispatch | Superseded | 2026-01-0? | PR Terraform Plan dispatches Infra Terraform Checks for validation. Teams need clarity on where those checks run: on the PR branch, on the target branch, or both. The default should remain simple, ... |
| [ADR-0045](ADR-0045-platform-teardown-lb-delete-default.md) | Platform | Default LB delete when ENIs persist during teardown | Active | 2026-01-0? | Even with the ENI wait gate, teardowns can still hang when NLB ENIs linger and the load balancer does not delete in time. Operators consistently choose the break-glass option to delete remaining cl... |
| [ADR-0046](ADR-0046-platform-pr-plan-validation-ownership.md) | Platform | PR plan owns validation (no auto infra checks dispatch) | Active | 2026-01-0? | The PR plan workflow has been dispatching Infra Terraform Checks automatically. This adds an extra workflow hop and creates confusion about what must run before apply. We already enforce the critic... |
| [ADR-0047](ADR-0047-platform-teardown-destroy-timeout-retry.md) | Platform | Retry Terraform destroy after timeout with cluster-scoped LB cleanup | Active | 2026-01-0? | Teardown can stall when Terraform destroy reaches subnet deletion while Kubernetes-created Network Load Balancer ENIs are still present. The LB cleanup step removes services, but AWS eventual consi... |
| [ADR-0048](ADR-0048-platform-teardown-version-selector.md) | Platform | Versioned teardown runners with selectable entrypoint | Active | 2026-01-0? | Teardown reliability depends on managed-service cleanup timing (LBs/ENIs) and Terraform destroy behaviors. Iterating on teardown logic is necessary, but changing the primary teardown script directl... |
| [ADR-0049](ADR-0049-platform-pragmatic-observability-baseline.md) | Platform | Pragmatic observability baseline for V1 (RED + Golden Signals) | Active | 2026-01-0? | V1 priorities emphasize reliable deployment and teardown with low operational overhead. Full distributed tracing and deep SLO mechanics are valuable, but they increase implementation complexity and... |
| [ADR-0050](ADR-0050-platform-changelog-label-gate.md) | Platform | Label-gated changelog entries | Active | 2026-01-0? | Changelog updates are required for material behavior changes but not for mechanical refactors or formatting fixes. A lightweight gate is needed to require entries only when change impact warrants i... |
| [ADR-0051](ADR-0051-platform-reliability-metrics-contract-minimums.md) | Platform | Minimal reliability metrics and contract minimums | Active | 2026-01-0? | V1 needs visible proof that build/teardown are reliable without adopting full CI observability. We also need a minimal platform contract that keeps lifecycle runs deterministic and auditable withou... |
| [ADR-0052](ADR-0052-platform-kube-prometheus-stack-bundle.md) | Platform | Use kube-prometheus-stack as the V1 monitoring bundle | Active | 2026-01-0? | V1 needs a deterministic, productized monitoring baseline. Today Prometheus, Grafana, and Alertmanager are installed as separate Helm charts, which increases config drift, operational overhead, and... |
| [ADR-0053](ADR-0053-platform-storage-lifecycle-separation.md) | Platform | Separate storage lifecycle from bootstrap and teardown | Active | 2026-01-0? | Monitoring components require PVCs to persist data. If storage add-ons are not ready at bootstrap, kube-prometheus-stack pods stay Pending and monitoring is not available. Teardown can be delayed b... |
| [ADR-0054](ADR-0054-platform-observability-exporters-otel-split.md) | Platform | Exporter vs OpenTelemetry split for platform observability | Active | 2026-01-0? | We need a clear and minimal observability baseline that separates infrastructure metrics from application telemetry. There has been ambiguity about whether OpenTelemetry replaces Prometheus exporte... |
| [ADR-0055](ADR-0055-platform-tempo-tracing-backend.md) | Platform | Tempo as the standard tracing backend (V1.1) | Active | 2026-01-0? | V1 focuses on metrics-first observability, with distributed tracing deferred to V1.1. When tracing is enabled, we need a default backend that aligns with the Grafana/Prometheus/Loki stack and integ... |
| [ADR-0056](ADR-0056-platform-loki-deployment-mode.md) | Platform | Loki deployment mode for V1 | Active | 2026-01-0? | We need a log storage baseline that is simple to operate in V1 while still allowing a clear path to scale and HA when log volume grows. Loki offers two common deployment modes: Single Binary and Si... |
| [ADR-0057](ADR-0057-platform-ci-terraform-force-unlock-workflow.md) | Platform | CI Terraform force-unlock workflow (break-glass) | Active | 2026-01-0? | Teardown and destroy runs can leave Terraform state locks when runs fail, runner pods are canceled, or a prior step exits without releasing the lock. Local`force-unlock`is risky and often unavailab... |
| [ADR-0058](ADR-0058-platform-grafana-config-workflow.md) | Platform | Separate Grafana config workflow with readiness guard | Active | 2026-01-0? | Grafana configuration (dashboards, datasources, alert rules) is managed as code via Terraform in`idp-tooling/grafana-config/`. The Grafana API must be reachable and stable before the provider can a... |
| [ADR-0059](ADR-0059-platform-ci-workflow-index-and-ownership.md) | Platform | CI workflow index, ownership, and UI grouping | Active | 2026-01-0? | The CI workflow list is growing. Without a single index, naming conventions, and clear ownership markers, workflows become hard to find, easy to misuse, and harder to audit. This creates operationa... |
| [ADR-0060](ADR-0060-platform-ephemeral-update-workflow.md) | Platform | Separate update workflow for existing ephemeral dev clusters | Active | 2026-01-0? | Ephemeral clusters are created through a new-build workflow that enforces`new_build=true`. When operators need to update an existing ephemeral cluster (same BuildId), that guard blocks the apply. W... |
| [ADR-0061](ADR-0061-platform-observability-provisioning-boundary.md) | Platform | Observability provisioning boundary (Helm in-cluster, Terraform external) | Active | 2026-01-0? | We need a consistent rule for how observability is provisioned to avoid drift between GitOps (Helm/Argo) and Terraform provider configurations. Today the platform uses Helm for in-cluster observabi... |
| [ADR-0062](ADR-0062-platform-app-template-contract.md) | Platform | App template contract for team-owned deployments | Active | 2026-01-0? | App teams need a consistent, self-serve starting point for deploying services without re-learning platform conventions each time. Today there is no single, opinionated template that makes ownership... |
| [ADR-0063](ADR-0063-platform-terraform-helm-bootstrap.md) | Platform | Terraform Helm Provider for Bootstrap | Active | 2026-01-0? | Running the platform requires a complex sequence of operations: provisioning AWS infrastructure (Terraform) and then installing Kubernetes controllers like ArgoCD (Bash scripts/Helm). |
| [ADR-0064](ADR-0064-platform-dev-bootstrap-defaults.md) | Platform | Dev bootstrap defaults off for k8s resources and storage | Active | 2026-01-0? | Recent bootstrap runs failed when Terraform-managed Kubernetes service accounts and storage add-on checks were enabled by default. The CI bootstrap role and cluster readiness were not consistently ... |
| [ADR-0065](ADR-0065-platform-branch-policy-guard.md) | Platform | Restore branch policy guard for main | Active | 2026-01-0? | We require a consistent release path that flows through the development branch before reaching main. Recent changes temporarily relaxed the branch policy guard, allowing non-development branches to... |
| [ADR-0066](ADR-0066-platform-dashboards-as-code.md) | Platform | Platform Dashboards as Code | Active | 2026-01-0? | Observability dashboards are critical operational artifacts. However, managing them via the Grafana UI ("ClickOps") leads to: |
| [ADR-0067](ADR-0067-platform-labeler-base-ref.md) | Platform | Use base ref for labeler checkout | Active | 2026-01-0? | The PR labeler workflow checked out the base commit SHA. When the base SHA pointed to an older labeler config, the v5 labeler action failed due to config schema drift. This blocked PRs even when th... |
| [ADR-0068](ADR-0068-platform-review-cadence-output.md) | Platform | Fix review cadence output delimiter | Active | 2026-01-0? | The production readiness review cadence workflow writes multi-line output to`GITHUB_OUTPUT`. The current quoted heredoc delimiter breaks note parsing and causes the check to fail even when the scri... |
| [ADR-0069](ADR-0069-platform-observability-baseline-golden-signals.md) | Platform | Observability baseline for golden signals in production | Superseded | 2026-01-0? | Production needs consistent visibility into the golden signals: latency, traffic, errors, and saturation. The platform should provide an opinionated baseline that is production-grade but not overki... |
| [ADR-0070](ADR-0070-platform-terraform-aws-lb-controller.md) | Platform | Terraform Management of AWS Load Balancer Controller | Active | 2026-01-0? | The AWS Load Balancer Controller is a critical component that bridges Kubernetes Ingress objects to AWS Application Load Balancers (ALBs). Without it, Ingress resources (like Kong) remain in a pend... |
| [ADR-0071](ADR-0071-doc-taxonomy-refactor.md) | Platform | Standardized Documentation Taxonomy | Active | 2026-01-0? | The documentation structure has grown organically, leading to scattered "product-like" definitions (Requirements, Catalog, SLAs) and ambiguous homes for operational policies (Upgrade/Deprecation ru... |
| [ADR-0072](ADR-0072-platform-pr-checklist-template.md) | Platform | PR checklist template in PR gates guide | Active | 2026-01-0? | The PR guardrails require checklist selections in the PR body. The checklist template lives in GitHub, but contributors often do not discover it until the PR guard fails. This adds friction for onb... |
| [ADR-0073](ADR-0073-platform-bootstrap-v3-irsa-skip.md) | Platform | Bootstrap v3 skips Terraform IRSA apply in Stage 3B | Active | 2026-01-0? | Bootstrap Stage 3B runs a targeted Terraform apply for IRSA service accounts. When the service accounts already exist, the plan reports "No changes" and the bootstrap guard treats that as a failure... |
| [ADR-0074](ADR-0074-platform-ops-workflow-branch-guard.md) | Platform | Ops workflow branch guard | Active | 2026-01-0? | Ops workflows (bootstrap, teardown, orphan cleanup, managed LB cleanup) can be invoked from any branch via workflow dispatch. That increases risk of running operational jobs from stale or experimen... |
| [ADR-0075](ADR-0075-app-example-deployments.md) | Platform | App example deployments via Argo CD, Helm, and Kustomize | Active | 2026-01-0? | Example applications were added under`apps/`, but they lacked a consistent, repeatable packaging format for GitOps deployment. We need deterministic example apps that can be deployed via Argo CD us... |
| [ADR-0076](ADR-0076-platform-infracost-ci-visibility.md) | Platform | Lightweight CI cost visibility with Infracost | Active | 2026-01-0? | We want early, low-friction cost visibility for Terraform changes without blocking delivery. Cost information should surface in PRs to build a habit of cost awareness before introducing hard gates. |
| [ADR-0077](ADR-0077-platform-ci-build-teardown-log-automation.md) | Platform | CI build/teardown log automation | Active | 2026-01-0? | Build, bootstrap, and teardown logs provide a durable record of run outcomes, flags, and timings. Capturing them manually is inconsistent and slows post-run analysis. We need an automated, low-fric... |
| [ADR-0078](ADR-0078-platform-governed-repo-scaffolder.md) | Platform | Governance-driven app repository scaffolder | Active | 2026-01-0? | App repos are created ad-hoc today, which leads to missing catalog metadata, inconsistent guardrails, and drift from platform standards. We need a single, deterministic path that scaffolds a repo w... |
| [ADR-0079](ADR-0079-platform-ai-agent-governance.md) | Platform | AI Agent Governance and Auditability | Active | 2026-01-0? | AI agents are increasingly used for documentation, workflow updates, and automation changes. Without explicit governance, changes risk drift, poor traceability, and inconsistent QA. |
| [ADR-0080](ADR-0080-platform-github-agent-roles.md) | Platform | GitHub App Roles for AI/Automation Access | Active | 2026-01-0? | We need a way to grant AI and automation roles without creating new human GitHub accounts. The solution must be auditable, least-privilege, and easy to rotate. |
| [ADR-0081](ADR-0081-platform-repo-wide-linting.md) | Platform | Repo-wide linting for knowledge-graph hygiene | Active | 2026-01-0? | We are introducing a knowledge-graph footprint that relies on consistent YAML and Markdown. Path-scoped linting misses drift when files move or when new schemas appear across the repo. |
| [ADR-0082](ADR-0082-platform-metadata-validation.md) | Platform | Platform Metadata Validation Strategy | Active | 2026-01-0? | As the Golden Path IDP scales, we are introducing a "Knowledge Graph" approach to link artifacts (Code, Docs, Decisions). We need a way to enforce the integrity of these links. |
| [ADR-0083](ADR-0083-platform-metadata-backfill-protocol.md) | Platform | Metadata Backfill Campaign Protocol | Active | 2026-01-0? | We are adopting a metadata strategy that enables traceability and automated governance. The validator currently enforces metadata on a subset of docs, and Terraform tags are not yet validated autom... |
| [ADR-0084](ADR-0084-platform-enhanced-metadata-schema.md) | Platform | Enhanced Metadata Schema for Knowledge Graph | Active | 2026-01-0? | The repository contains 300+ markdown files across documentation, modules, applications, and infrastructure code. To enable Knowledge Graph capabilities and semantic search, we need a comprehensive... |
| [ADR-0085](ADR-0085-score-implementation.md) | Platform | Implementing Score in V1 | Active | 2026-01-0? | Our current IDP handles application scaffolding via Backstage Templates that generate standard Kubernetes manifests. While functional, this "bakes in" the platform's K8s logic into every developers... |
| [ADR-0086](ADR-0086-federated-metadata-validation.md) | Platform | Federated Metadata Validation Strategy | Active | 2026-01-0? | Our current metadata compliance engine (`validate_metadata.py`) is locked within the`goldenpath-idp-infra`repository. As the platform scales, new application repositories (workloads) are being crea... |
| [ADR-0087](ADR-0087-k8s-metadata-sidecars.md) | Platform | Integration of Governance Metadata with Kubernetes Resources | Active | 2026-01-0? | The repository has achieved 100% metadata compliance across all documentation and markdown files. This metadata enables automated health reporting, risk assessment, and lifecycle management. Howeve... |
| [ADR-0088](ADR-0088-automated-metadata-remediation.md) | Platform | Automated Metadata Remediation over Manual Compliance | Active | 2026-01-0? | As the repository grows (currently 316+ files), maintaining a consistent metadata schema becomes increasingly difficult if left to manual developer effort. Traditional "governance" relies on blocki... |
| [ADR-0089](ADR-0089-closed-loop-metadata-injection.md) | Platform | Closed-Loop Metadata Injection | Active | 2026-01-0? | We have established a robust metadata governance system using sidecars (`metadata.yaml`). However, this metadata remained isolated from the live running resources in Kubernetes. To enable field-lev... |
| [ADR-0090](ADR-0090-automated-platform-health-dashboard.md) | Platform | Automated Platform Health Dashboard | Active | 2026-01-0? | As the GoldenPath IDP grows, manual auditing of metadata compliance, risk profiles, and "Dark Infrastructure" becomes unsustainable. We have a reporter script (`platform_health.py`), but its output... |
| [ADR-0092](ADR-0092-ecr-registry-product-strategy.md) | Platform | ECR Registry Product-Based Strategy & Shared Responsibility Model | Active | 2026-01-0? | We need a clear strategy for ECR registry management that aligns with Domain-Driven Design principles and establishes clear ownership boundaries between platform and application teams. |
| [ADR-0093](ADR-0093-automated-policy-enforcement.md) | Platform | Automated Policy Enforcement Framework | Active | 2026-01-0? | We need policies to be enforceable, not just documentation. Manual enforcement doesn't scale and policies become stale without automation. |
| [ADR-0094](ADR-0094-automated-catalog-docs.md) | Platform | Automated Registry Catalog Documentation | Active | 2026-01-0? | The ECR registry catalog (`docs/registry-catalog.yaml`) is the single source of truth for all container registries, but YAML is not easily scannable for humans. Teams need a quick, readable referen... |
| [ADR-0095](ADR-0095-self-service-registry-creation.md) | Platform | Self-Service ECR Registry Creation Workflow | Active | 2026-01-0? | Application teams need to request ECR registries, but the current process requires manual file editing and Terraform knowledge. This creates friction and bottlenecks the platform team. |
| [ADR-0096](ADR-0096-risk-based-ecr-controls.md) | Platform | Risk-Based ECR Security Controls | Proposed | 2026-01-0? | ECR registries have different security requirements based on their risk level. Production workloads need stronger controls (KMS encryption, immutable tags) while development environments can use li... |
| [ADR-0097](ADR-0097-domain-based-resource-catalogs.md) | Platform | Domain-Based Resource Catalogs | Proposed | 2026-01-0? | As the platform grows, we need to manage multiple resource types (ECR registries, RDS databases, S3 buckets, EKS clusters, etc.). We must decide between: |
| [ADR-0098](ADR-0098-standardized-pr-gates.md) | Platform | Standardized PR Gates for ECR Pipeline | Proposed | 2026-01-0? | The ECR pipeline PRs were experiencing repeated CI failures due to inconsistent guardrail checks, YAML linting errors, and missing metadata. Multiple workflows needed to trigger on both`main`and`de... |
| [ADR-0099](ADR-0099-standardized-iam-policy-management.md) | Platform | Standardized IAM Policy Management | Active | 2026-01-0? | Previously, IAM JSON policy fragments were scattered across documentation files or placed loosely in the`docs/10-governance/policies/`directory. This made it difficult to: 1.  Verify exactly what p... |
| [ADR-0100](ADR-0100-standardized-ecr-lifecycle-and-documentation.md) | Platform | Standardized ECR Lifecycle and Documentation | Proposed | 2026-01-0? | The previous ECR registry creation process required manual input for multiple redundant fields (name and ID) and suffered from a "drift gap" where the human-readable [REGISTRY_CATALOG.md](../REGIST... |
| [ADR-0101](ADR-0101-pr-metadata-auto-heal.md) | Platform | PR Metadata Auto-Heal and Scoped Validation | Active | 2026-01-0? | The platform's metadata validation workflow was blocking PRs due to: 1. **Full-repo scanning**: Any`.md`file change triggered validation of the entire repository, causing unrelated failures 2. **Ma... |
| [ADR-0102](ADR-0102-terraform-fast-validation.md) | Platform | Layer 2 Terraform Validation (Fast Feedback Loop) | Proposed | 2026-01-0? | Currently, Terraform validation primarily occurs during the`env=dev`integration tests (`infra-terraform-apply-dev.yml`) or via`pr-terraform-plan.yml`. These workflows require AWS credentials, backe... |
| [ADR-0103](ADR-0103-automated-workflow-docs.md) | Platform | Automated CI Workflow Documentation | Superseded | 2026-01-06 | As the complexity of the platform grows, the number of GitHub Actions workflows has increased significantly (>30 workflows). Maintaining a manual index of these workflows (`ci-workflows/CI_WORKFLOW... |
| [ADR-0104](ADR-0104-automated-script-docs.md) | Platform | Automated Script Documentation | Superseded | 2026-01-06 | The platform relies on a large suite of Python and Shell scripts (~25) for governance, documentation, and delivery. Maintaining a manual index of these scripts (`scripts/index.md`) is tedious and e... |
| [ADR-0110](ADR-0110-idp-knowledge-graph-architecture.md) | Platform | IDP Knowledge Graph Node Architecture | Proposed | 2026-01-06 | The GoldenPath IDP currently uses disconnected YAML sidecars (`metadata.yaml`) to track component attributes. While metadata compliance is high (98.7%), we lacks a structured way to understand **re... |
| [ADR-0111](ADR-0111-platform-documentation-auto-healing.md) | Platform | Automated Documentation Auto-Healing | Proposed | 2026-01-0? | Our platform uses automated indexing scripts (`generate_script_index.py`,`generate_workflow_index.py`) to maintain documentation portals (`scripts/index.md`,`ci-workflows/CI_WORKFLOWS.md`). |
| [ADR-0112](ADR-0112-automated-adr-index-generation.md) | Platform | Automated ADR Index Generation | Proposed | 2026-01-06 | As the number of Architecture Decision Records (ADRs) grows (currently 100+), keeping the`01_adr_index.md`in sync manually has become error-prone. We frequently observe drift in statuses, dates, an... |
| [ADR-0113](ADR-0113-platform-queryable-intelligence-enums.md) | Platform | Platform Queryable Intelligence Enums | Proposed | 2026-01-06 | The GoldenPath IDP relies on metadata sidecars to drive automated governance, health reporting, and Knowledge Graph traversal. However, drift has been identified in the values used for key fields (... |
| [ADR-0114](ADR-0114-automated-enum-consistency-validation.md) | Platform | Automated Enum Consistency Validation | Proposed | 2026-01-06 | With the introduction of unified enums in [ADR-0113](ADR-0113-platform-queryable-intelligence-enums.md), we need a mechanism to enforce these values across the repository. Manual review is insuffic... |
| [ADR-0115](ADR-0115-enhanced-enum-validation-engine.md) | Platform | Enhanced Enum Validation Engine | Proposed | 2026-01-06 | ADR-0114 introduced the`validate_enums.py`script to enforce metadata consistency. However, the initial implementation relied on flat field matching, making it difficult to validate nested objects l... |
| [ADR-0116](ADR-0116-emoji-usage-policy-and-enforcement.md) | Platform | Emoji Usage Policy & Automated Enforcement | Proposed | 2026-01-06 | Documentation quality and professional neutrality are core tenets of the platform. Excessive or semi-random emoji usage in authoritative documents (ADRs, Policies, Schemas) can obscure meaning and ... |
| [ADR-0117](ADR-0117-conclusive-governance-routing-architecture.md) | Platform | Conclusive Governance Routing & Compliance Engine | Proposed | 2026-01-06 | As the platform grows, managing which teams review which changes (and what documentation is required) has become a manual overhead. Architectural rigor for high-risk areas like AI Agents and Securi... |
| [ADR-0118](ADR-0118-config-driven-metadata-governance.md) | Platform | Config-Driven Metadata Governance Architecture | Proposed | 2026-01-06 | The platform's metadata standardization and validation logic was previously hardcoded in monolithic Python scripts. This created a maintenance bottleneck where architectural changes required code d... |
| [ADR-0119](ADR-0119-grand-metadata-healing-and-contextual-alignment.md) | Platform | Grand Metadata Healing & Contextual Alignment | Proposed | 2026-01-0? | As the Golden Path IDP scales, we have transitioned to a config-driven metadata model (ADR-0118). However, a repository-wide audit revealed over 475 instances of "Governance Debt," where legacy rec... |
| [ADR-0120](ADR-0120-metadata-inheritance-and-active-governance.md) | Platform | metadata | Proposed | 2026-01-0? | As we reach V1 readiness for the Golden Path IDP, we need a metadata system that is both robust and fluid. Maintaining 500+ explicit metadata files is a velocity bottleneck, while a static "set and... |
| [ADR-0121](ADR-0121-value-quantification-framework.md) | Platform | Value Quantification (VQ) Framework | Proposed | 2026-01-07 | As the Golden Path Platform grows, engineering efforts often become "invisible" to business stakeholders. Manual governance, schema refactors, and pipeline optimizations are critical for stability ... |
| [ADR-0122](ADR-0122-automated-vq-enforcement-and-mission-recovery.md) | Platform | Automated VQ Enforcement and Mission Recovery | Proposed | 2026-01-0? | With the introduction of the Value Quantification (VQ) framework ([ADR-0121](./ADR-0121-value-quantification-framework.md)), the platform now has a vocabulary for ROI. However, without automated en... |
| [ADR-0123](ADR-0123-delivery-automation-suite.md) | Platform | Delivery Automation Suite (ECR & Logs) | Proposed | 2026-01-0? | The GoldenPath IDP requires a standardized set of utilities to handle ECR registry provisioning and build/teardown telemetry. These utilities were developed early in the project but lacked formal a... |
| [ADR-0124](ADR-0124-documentation-and-visibility-suite.md) | Platform | Documentation & Visibility Suite | Proposed | 2026-01-0? | Maintaining a large documentation-as-code repository requires automated validation of freshness, structure, and relationships. These tools were built to prevent "Doc Drift" and ensure the Knowledge... |
| [ADR-0125](ADR-0125-compliance-and-maintenance-suite.md) | Platform | Compliance & Maintenance Suite | Proposed | 2026-01-0? | The GoldenPath IDP requires continuous auditing and maintenance of its metadata and governance state. These utilities provide the "Janitorial" and "Auditing" functions for the platform. |
| [ADR-0126](ADR-0126-idp-automation-confidence-matrix.md) | Platform | IDP Automation Confidence Matrix (Five-Star Approval) | Proposed | 2026-01-0? | As the GoldenPath IDP moves at high velocity, the accumulation of "Dark History" (undocumented/untested scripts) and brittle automation poses a risk to platform stability. We need a rigorous, multi... |
| [ADR-0127](ADR-0127-backstage-deployment-roi-telemetry.md) | Platform | Backstage Helm Deployment with ROI Telemetry | Proposed | 2026-01-0? | We need a deterministic, repeatable method to deploy the Backstage portal while simultaneously quantifying the value (ROI) of our platform automation. |
| [ADR-0128](ADR-0128-automated-ecr-catalog-sync.md) | Platform | Automated IDP Catalog Mapping for AWS ECR | Proposed | 2026-01-0? | To minimize "Friction Tax," developers need visibility into container registries without leaving the IDP. Manually maintaining this inventory in Backstage is error-prone and leads to documentation ... |
| [ADR-0129](ADR-0129-platform-eventual-consistency-ecr-governance.md) | Platform | Eventual Consistency for ECR Registry Governance | Proposed | 2026-01-0? | The Backstage catalog currently faces a "Truth" divergence regarding AWS ECR. While only one physical ECR registry exists, previous automation (Scaffolder runs) created separate`Kind: Resource`YAML... |
| [ADR-0130](ADR-0130-platform-catalog-zoned-defense-security.md) | Platform | Zoned Defense for Catalog Ingestion Security | Proposed | 2026-01-0? | The previous catalog configuration allowed any registered location (even user-contributed ones) to define security-sensitive entities like`Domain`,`Group`, and`User`. This created a "Shadow IT" ris... |
| [ADR-0131](ADR-0131-platform-health-outcome-metrics.md) | Platform | Outcome Metrics for Platform Health | Proposed | 2026-01-0? | The platform health dashboard currently focuses on governance inputs (metadata compliance, ADR activity, changelog volume) but lacks outcome-based signals that reflect delivery reliability and time... |
| [ADR-0132](ADR-0132-platform-container-registry-system.md) | Platform | Model ECR Registry as a Dedicated Backstage System | Proposed | 2026-01-0? | The ECR registry powers build, publish, and deploy workflows across the platform and creates downstream operational effects (promotion, rollbacks, and catalog visibility). Today, the ECR registry i... |
| [ADR-0133](ADR-0133-human-in-the-loop-backstage-docs-prs.md) | Platform | Human-in-the-Loop PRs for Backstage Docs Generation | Proposed | 2026-01-0? | Backstage documentation entities are generated by`scripts/generate_backstage_docs.py`. Today this step is run manually, which creates drift risk between the docs (`docs/`) and the Backstage catalog... |
| [ADR-0134](ADR-0134-metadata-inheritance-active-governance-and-leak-protection.md) | Platform | metadata | Proposed | 2026-01-0? | As we reach V1 readiness for the Golden Path IDP, we need a metadata system that is both robust and fluid. Maintaining 500+ explicit metadata files is a velocity bottleneck, while a static "set and... |
| [ADR-0135](ADR-0135-platform-secrets-manager-eso-foundation.md) | Platform | Secrets Manager + External Secrets Operator foundation | Proposed | 2026-01-0? | We need a deterministic, auditable secrets flow for the IDP golden path. Today, secrets handling is ad hoc, and does not provide a governed path for app teams. We want a consistent source of truth ... |
| [ADR-0136](ADR-0136-platform-tooling-config-identity.md) | Platform | Tooling config identity sidecars | Proposed | 2026-01-0? | We want every artifact that influences platform behavior to have a clear identity, owner, and audit trail. Tooling configs such as`.pre-commit-config.yaml`,`.yamllint`,`.markdownlint.json`, and`mkd... |
| [ADR-0137](ADR-0137-metadata-placement-configs-and-reports.md) | Platform | Metadata placement for configs and reports | Proposed | 2026-01-0? | We need a single, consistent rule for where metadata lives for non-doc artifacts (config YAML/JSON and generated reports). Mixing frontmatter and sidecars has led to confusion, validation gaps, and... |
| [ADR-0138](ADR-0138-automated-secret-scanning-gitleaks-trufflehog.md) | Platform | Automated Secret Scanning with Gitleaks and TruffleHog | Proposed | 2026-01-0? | As we transition to using **AWS Secrets Manager** and **External Secrets Operator (ESO)** for credential management, we must ensure that secrets do not bypass these governed systems and leak into t... |
| [ADR-0139](ADR-0139-portable-secrets-manager-infra-module.md) | Platform | Portable Secrets Manager Infrastructure Module | Proposed | 2026-01-0? | We need to manage AWS Secrets Manager instances across`dev`,`test`,`staging`, and`prod`. Historically, infrastructure for different environments was handled with varying degrees of duplication. To ... |
| [ADR-0140](ADR-0140-platform-doc-scaffold-metadata-autofix.md) | Platform | Doc scaffolding and metadata auto-fix | Proposed | 2026-01-0? | New docs are often created without the required metadata headers. The missing frontmatter is usually only discovered at PR time, which creates friction and burns review cycles. We need a path that ... |
| [ADR-0141](ADR-0141-backstage-ecr-dispatch-workflow.md) | Platform | Backstage ECR requests use GitHub Actions dispatch | Proposed | 2026-01-0? | The Backstage ECR scaffolder was creating PRs directly using`fetch:plain`+`command:execute`+`publish:github:pull-request`. That path requires a custom Backstage backend image with the command actio... |
| [ADR-0142](ADR-0142-declarative-platform-contracts.md) | Platform | Strategic Adoption of Declarative Platform Contracts | Proposed | 2026-01-0? | As the Golden Path IDP scales, the gap between developer intent and infrastructure implementation (Terraform, Helm, IAM) is widening. Currently, infrastructure requests are handled via manual code ... |
| [ADR-0143](ADR-0143-secret-request-contract.md) | Platform | Secret Request Contract (V1) | Active | 2026-01-0? | This contract defines how teams request application secrets through the platform in a governed, auditable way. It désigne kind: SecretRequest as the primary interface for managing sensitive data, b... |
| [ADR-0144](ADR-0144-intent-to-projection-parser.md) | Platform | Architecture of the Intent-to-Projection Parser (The Golden Path Core) | Proposed | 2026-01-0? | As the Golden Path IDP matures, we face a fundamental challenge: **How do we allow developers to request complex infrastructure without requiring them to become cloud engineers?** |
| [ADR-0145](ADR-0145-governance-registry-mirror.md) | Platform | Governance Registry Mirror Pattern | Proposed | 2026-01-0? | High-velocity interaction between humans and machine agents creates a "Commit Tug-of-War" when automated scripts attempt to mutate active development branches. Specifically, scripts updating`PLATFO... |
| [ADR-0146](ADR-0146-schema-driven-script-certification.md) | Platform | Schema-Driven Script Certification | Active | 2026-01-12 | The platform currently relies on dozens of Python and Bash scripts to manage critical lifecycle events (metadata standardization, registry mirroring, secret management). While we have a high-level ... |
| [ADR-0147](ADR-0147-automated-governance-backfill.md) | Platform | Automated Governance Backfill | Active | 2026-01-12 | Following the ratification of [ADR-0146](ADR-0146-schema-driven-script-certification.md), the platform faces a "Migration Gap". We have stringent new rules (CNT-001) but a legacy codebase that viol... |
| [ADR-0148](ADR-0148-seamless-build-deployment-with-immutability.md) | Platform | Seamless Build Deployment with Build ID Immutability | Proposed | 2026-01-0? | The platform requires a deployment process that: |
| [ADR-0153](ADR-0153-cluster-provisioning-identity.md) | Platform | Cluster Provisioning Identity and Script Resilience | Proposed | 2026-01-14 | During the implementation of the "Seamless Build Deployment" (ADR-0148), two significant operational blockers were identified that affected the reliability and portability of the build process: |
| [ADR-0154](ADR-0154-promote-bootstrap-v3.md) | Platform | Promote Bootstrap V3 as Default | Proposed | 2026-01-14 | The platform bootstrap logic (`bootstrap/`) has evolved through versions`v1`(legacy),`v2`(interim), and`v3`(current). The default`Makefile`configuration pointed to`v1`. However, during the implemen... |
| [ADR-0155](ADR-0155-ci-governance-registry-fetch.md) | Platform | CI Governance Registry Fetch for Build ID Validation | Proposed | 2026-01-0? | The build_id immutability guard in`envs/dev/main.tf`validates that a build_id has not been previously used by checking the governance-registry branch CSV file. However, there is a vulnerability in ... |
| [ADR-0156](ADR-0156-platform-ci-build-timing-capture.md) | Platform | CI Build Timing Capture at Source | Proposed | 2026-01-0? | Build timing data for ephemeral cluster deployments was not being captured in the governance-registry`build_timings.csv`when deployments ran through CI workflows. |
| [ADR-0157](ADR-0157-platform-multi-tenant-rds-architecture.md) | Platform | Multi-Tenant RDS for Platform Tooling Applications | Superseded | 2026-01-0? | Platform tooling applications (Keycloak, Backstage) require persistent PostgreSQL databases. Three options exist: |
| [ADR-0158](ADR-0158-platform-standalone-rds-bounded-context.md) | Platform | Standalone RDS as Bounded Context with Deletion Protection | Proposed | 2026-01-0? | ADR-0157 established multi-tenant RDS for platform tooling but coupled it to the EKS cluster Terraform state. This creates problems: |
| [ADR-0159](ADR-0159-backstage-catalog-registry-sync.md) | Platform | Backstage Catalog Sync to Governance Registry | Proposed | 2026-01-0? | The Backstage Software Catalog provides self-service templates for developers to provision resources (ECR registries, RDS databases, etc.). Previously, the catalog URL in Backstage configuration po... |
| [ADR-0160](ADR-0160-rds-optional-toggle-integration.md) | Platform | RDS Optional Toggle Integration | Proposed | 2026-01-15 | ADR-0158 introduced RDS as a standalone bounded context (`envs/dev-rds/`) to ensure data persistence across cluster rebuilds. This works well for users who need decoupled lifecycle management and i... |
| [ADR-0161](ADR-0161-ephemeral-infrastructure-stack.md) | Platform | Standard Ephemeral Infrastructure Stack | Proposed | 2026-01-15 | Our platform supports multiple deployment contexts: |
| [ADR-0162](ADR-0162-kong-ingress-dns-strategy.md) | Platform | Kong Ingress DNS Strategy for Platform Tooling | Proposed | 2026-01-16 | Platform tooling applications (Backstage, Keycloak, ArgoCD, Grafana) are deployed on EKS clusters and need to be accessible to developers and operators. Previously, access required kubectl port-for... |
| [ADR-0163](ADR-0163-agent-collaboration-governance.md) | Platform | Agent Collaboration Governance and Living Registry | Proposed | 2026-01-16 | The platform now relies on multiple AI agents running locally and in CI. We already have policy guardrails for agents, but we lack a single, living source of truth that defines who each agent is, w... |
| [ADR-0164](ADR-0164-teardown-v3-enhanced-reliability.md) | Platform | Teardown V3 with Enhanced Reliability and RDS Support | Active | 2026-01-0? | ### Problem Statement |
| [ADR-0165](ADR-0165-rds-user-db-provisioning-automation.md) | Platform | Automated RDS User and Database Provisioning | Proposed | 2026-01-16 | Terraform currently creates Secrets Manager entries for database credentials but does not create the corresponding Postgres roles or databases. This leaves a manual gap (psql access) and introduces... |
| [ADR-0166](ADR-0166-rds-dual-mode-automation-and-enum-alignment.md) | Platform | Dual-Mode RDS Automation with Enum-Aligned Requests | Proposed | 2026-01-16 | The platform intentionally supports two RDS deployment modes: |
| [ADR-0167](ADR-0167-session-capture-guardrail.md) | Platform | Session Capture Append-Only Guardrail | Proposed | 2026-01-17 | Session captures are intended to preserve context for AI and human collaboration, but without enforcement they can drift, be overwritten, or lose traceability. We need a standardized, append-only f... |
| [ADR-0168](ADR-0168-eks-request-parser-and-mode-aware-workflows.md) | Platform | EKS Request Parser and Mode-Aware Workflows | Proposed | 2026-01-17 | EKS provisioning needed the same contract-driven, parser-first path used for RDS and Secrets, but EKS requests were either implicit (Terraform edits) or blocked by the scope gate. This created drif... |
| [ADR-0169](ADR-0169-secret-request-system-generated-ids.md) | Platform | System-Generated SecretRequest IDs with CI Immutability Guard | Proposed | 2026-01-17 | SecretRequest identifiers are used for governance, auditability, and traceability across request files, generated tfvars, and Terraform targets. When IDs are manually entered, they are prone to col... |
| [ADR-0170](ADR-0170-build-pipeline-architecture.md) | Platform | Build Pipeline Architecture and Multi-Repo Strategy | Accepted | 2026-01-19 | GoldenPath IDP needs a standardized build pipeline that: |
| [ADR-0170](ADR-0170-s3-self-service-request-system.md) | Platform | S3 Self-Service Request System | Proposed | 2026-01-17 | S3 buckets are the third pillar of the core infrastructure trio (RDS, ECR, S3). Currently, bucket provisioning requires direct Terraform access or manual requests, creating inconsistent configurati... |
| [ADR-0171](ADR-0171-platform-application-packaging-strategy.md) | Platform | Application Packaging Strategy - Helm vs Kustomize | Active | 2026-01-0? | ADR-0020 established that we use a hybrid approach (Helm + Kustomize) but did not provide clear guidance on **when to choose each tool**. This led to inconsistent decisions and confusion about whet... |
| [ADR-0172](ADR-0172-cd-promotion-strategy-with-approval-gates.md) | Platform | CD Promotion Strategy with Approval Gates | Active | 2026-01-0? | With CI pipelines building and pushing images to ECR, we need a clear strategy for how those images get promoted through environments. Key requirements: |
| [ADR-0173](ADR-0173-governance-doc-naming-migration.md) | Platform | Governance Doc Naming Migration Strategy | Proposed | 2026-01-0? | A new naming convention for governance docs has been proposed:`GOV-xxxx-description-of-file.md`. The current repository uses a mix of numerical prefixes (for example`04_PR_GUARDRAILS.md`) and domai... |
| [ADR-0174](ADR-0174-pipeline-decoupling-from-cluster-bootstrap.md) | Platform | Pipeline enablement intentionally decoupled from cluster bootstrap | Active | 2026-01-0? | GoldenPath IDP clusters are bootstrapped through a multi-stage process that provisions EKS, ArgoCD, monitoring, and foundational workloads. A separate concern is enabling the CI/CD pipeline that al... |
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
