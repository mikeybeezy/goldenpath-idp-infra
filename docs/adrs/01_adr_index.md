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
<!-- ADR_RELATE_END -->
---

# ADR Index (GoldenPath IDP)

This index lists Architecture Decision Records (ADRs) for GoldenPath IDP.

## How to use this

- ADRs document **what we decided**, **why**, and **tradeoffs**.
- Decisions should be changed by **superseding** an ADR (create a new one), not rewriting history.

> Location: `docs/adrs/`

---

## Active ADRs

<!-- ADR_TABLE_START -->
| [ADR-0001](ADR-0001-platform-argocd-as-gitops-operator.md) | Unknown | Adopt Argo CD as GitOps controller for platform deployments | Active | 2026-01-0?  | We need a deterministic, auditable mechanism to deploy and reconcile platform components (Kong, cert-manager, autoscaler, etc.) on EKS. |
| [ADR-0002](ADR-0002-platform-Kong-as-ingress-API-gateway.md) | Unknown | Use Kong as the primary ingress/API gateway behind an internal NLB | Active | 2026-01-0?  | We need a consistent “front door” for platform and workloads on EKS. |
| [ADR-0003](ADR-0003-platform-AWS-IAM-bootstrap-IRSA-SSM-.md) | Unknown | Use AWS IAM for bootstrap access, IRSA for pod-to-AWS access, and SSM for node break-glass | Active | 2026-01-0?  | We need secure and deterministic access patterns: |
| [ADR-0004](ADR-0004-platform-datree-policy-as-code-in-ci.md) | Unknown | Use Datree as Kubernetes policy-as-code gate in CI | Active | 2026-01-0?  | We need governance that is opinionated but not authoritarian: |
| [ADR-0005](ADR-0005-app-keycloak-as-identity-provider-for-human-sso.md) | Unknown | Adopt Keycloak for platform SSO (humans) and keep IRSA for pod-to-AWS auth | Active | 2026-01-0?  | We want a consistent identity layer for platform UIs and developer experience: |
| [ADR-0006](ADR-0006-platform-secrets-strategy.md) | Unknown | Use AWS Secrets Manager/SSM as system of record for secrets and External Secrets to hydrate Kubernetes | Active | 2026-01-0?  | The platform is frequently rebuilt and clusters are disposable. Any secret stored only inside the cluster risks loss and encourages manual fixes. |
| [ADR-0007](ADR-0007-platform-environment-model.md) | Unknown | Adopt an environment model that balances cost, iteration speed, and credible separation | Active | 2026-01-0?  | We want a V1 platform that demonstrates: |
| [ADR-0008](ADR-0008-app-backstage-portal.md) | Unknown | Use Backstage as the developer portal and the V1 demo application for env promotion | Active | 2026-01-0?  | We want the IDP to feel like a product, not just installed tooling. We also need a credible demonstration that: |
| [ADR-0009](ADR-0009-app-delivery-insights.md) | Unknown | CI/CD observability via OpenTelemetry ("Delivery Insights") | Active | 2026-01-0?  | Delivery (build → package → promote) represents a significant portion of value creation in the platform. Traditional CI feedback (pass/fail + logs) is insufficient to: |
| [ADR-0010](ADR-0010-platform-terraform-lockfile-stability.md) | Unknown | Enforce Terraform lockfile stability in CI | Active | 2026-01-0?  | CI should validate infrastructure code exactly as reviewed and committed. Allowing CI to upgrade providers or modules introduces drift and can cause changes in behavior that were not explicitly app... |
| [ADR-0011](ADR-0011-platform-ci-environment-contract.md) | Unknown | CI Environment Contract (Superseded) | Active | 2026-01-0?  | No context provided. |
| [ADR-0012](ADR-0012-platform-repo-decoupling-options.md) | Unknown | Repo decoupling options for infra and platform tooling | Active | 2026-01-0?  | We need to plan how to separate infrastructure and platform tooling repositories once the platform stabilizes. Today everything lives in one monorepo, which is simple but mixes ownership and expand... |
| [ADR-0013](ADR-0013-platform-argo-app-management-approach.md) | Unknown | Argo CD app management approach for current scale | Active | 2026-01-0?  | We need to decide how to manage Argo CD applications in production. The two options are: |
| [ADR-0014](ADR-0014-platform-ci-local-preflight-checks.md) | Unknown | Local preflight checks before PRs | Active | 2026-01-0?  | We want consistent, low-friction quality gates while avoiding false confidence from local tooling that does not perfectly match CI. Teams should run fast, local checks before opening PRs, but CI re... |
| [ADR-0015](ADR-0015-platform-aws-oidc-for-github-actions.md) | Unknown | Use AWS OIDC for GitHub Actions authentication | Active | 2026-01-0?  | GitHub Actions currently needs AWS credentials to run infrastructure workflows. Long-lived access keys stored as GitHub secrets increase the risk of leakage and require rotation. We want a safer, a... |
| [ADR-0016](ADR-0016-platform-ci-environment-separation.md) | Unknown | CI environment separation and manual promotion gates | Active | 2026-01-0?  | We need a CI/CD model that scales safely from early-stage usage to later growth without frequent rework. Infrastructure changes must be reviewed, environment-scoped, and applied with explicit human... |
| [ADR-0017](ADR-0017-platform-policy-as-code.md) | Unknown | Policy as code for infrastructure and application changes | Active | 2026-01-0?  | As the platform scales, we need consistent guardrails that prevent unsafe infrastructure and application changes without relying solely on manual review. With Backstage as our first client, we must... |
| [ADR-0018](ADR-0018-platform-container-registry-standard.md) | Unknown | Container registry standard — ECR default, GHCR supported, Docker Hub discouraged | Active | 2026-01-0?  | GoldenPath V1 targets an AWS-first, EKS-based platform with: |
| [ADR-0019](ADR-0019-platform-pre-commit-hooks.md) | Unknown | Pre-commit hooks as local quality gates | Active | 2026-01-0?  | We want fast, consistent feedback for contributors before changes reach CI. Local pre-commit hooks can prevent common formatting and lint issues while keeping the CI pipeline authoritative. The pla... |
| [ADR-0020](ADR-0020-platform-helm-kustomize-hybrid.md) | Unknown | Hybrid GitOps approach with Helm and Kustomize | Active | 2026-01-0?  | The repo already includes Helm-based GitOps and Kustomize overlays. We want a consistent, scalable approach that keeps packaging benefits for third-party tools while making environment-specific cha... |
| [ADR-0021](ADR-0021-platform-pr-terraform-plan.md) | Unknown | PR Terraform plan with automated comments | Active | 2026-01-0?  | We want Terraform plan feedback on pull requests without introducing Atlantis or requiring manual copy/paste. The goal is to surface infrastructure changes early while keeping apply manual and cont... |
| [ADR-0022](ADR-0022-platform-post-apply-health-checks.md) | Unknown | Post-apply health checks for platform readiness | Active | 2026-01-0?  | Terraform apply and bootstrap do not guarantee that the platform is usable. We need a deterministic, binary signal that the environment is healthy after apply so that promotions and demos are safe ... |
| [ADR-0023](ADR-0023-platform-ci-image-scanning.md) | Unknown | CI image scanning standard | Active | 2026-01-0?  | We need a registry-agnostic image vulnerability gate in CI. The platform should provide a default scanner that works with ECR, GHCR, or other registries, while keeping future options open. |
| [ADR-0024](ADR-0024-platform-security-floor-v1.md) | Unknown | Security floor for V1 | Active | 2026-01-0?  | We need a minimal, non-negotiable security baseline that reduces catastrophic risk without slowing delivery. V1 must be secure-by-default and leave heavier DevSecOps capabilities to V2. |
| [ADR-0025](ADR-0025-platform-boundaries-contract.md) | Unknown | Platform boundaries and contract | Active | 2026-01-0?  | The platform and workload planes must be separated explicitly to avoid duplicate governance and confusion. A clear contract defines what the platform guarantees and what teams own. |
| [ADR-0026](ADR-0026-platform-cd-deployment-contract.md) | Unknown | CD deployment contract | Active | 2026-01-0?  | GoldenPath uses GitOps-based continuous deployment to apply and reconcile desired state across environments. We need to make deployment expectations explicit to ensure deterministic promotion, clea... |
| [ADR-0027](ADR-0027-platform-design-philosophy.md) | Unknown | Platform design philosophy and reference implementation | Active | 2026-01-0?  | GoldenPath is intended to be operable without a single maintainer and usable by humans and machines. That requires durable, explicit documentation and a clear statement of the platform’s founding p... |
| [ADR-0028](ADR-0028-platform-dev-branch-gate.md) | Unknown | Dev branch gate before main | Active | 2026-01-0?  | We want quality gates that prove changes run in a real environment before they reach `main`. Relying solely on plans or post-merge applies weakens the value of the dev environment as a gate. A simp... |
| [ADR-0029](ADR-0029-platform-dev-plan-gate.md) | Unknown | Dev plan gate before dev apply | Active | 2026-01-0?  | The dev apply workflow currently checks for any successful plan on the same SHA. Because the plan workflow supports multiple environments, a non-dev plan can unlock a dev apply. This weakens the de... |
| [ADR-0030](ADR-0030-platform-precreated-iam-policies.md) | Unknown | Pre-create IAM policies for IRSA controllers in V1 | Active | 2026-01-0?  | The Terraform apply role used by GitHub Actions is intentionally scoped and cannot create IAM policies. Some IRSA controller roles (Cluster Autoscaler, AWS Load Balancer Controller) require custom ... |
| [ADR-0031](ADR-0031-platform-bootstrap-irsa-service-accounts.md) | Unknown | Create IRSA service accounts during bootstrap | Active | 2026-01-0?  | The AWS Load Balancer Controller and Cluster Autoscaler require IRSA-backed service accounts to exist before the controllers are installed. Early runs failed when the controllers were installed fir... |
| [ADR-0032](ADR-0032-platform-eks-access-model.md) | Unknown | EKS access model (bootstrap admin vs steady-state access) | Active | 2026-01-0?  | EKS grants cluster-admin access to the IAM principal that creates the cluster. In our case, that is the GitHub Actions bootstrap role. This is useful for initial provisioning, but it is a risk if l... |
| [ADR-0033](ADR-0033-platform-ci-orchestrated-modes.md) | Unknown | CI orchestrated modes for infra lifecycle | Active | 2026-01-0?  | The infra lifecycle requires multiple phases (apply, bootstrap, teardown). When operators must manually toggle flags, the workflow becomes brittle and error-prone. We saw repeated failures caused b... |
| [ADR-0034](ADR-0034-platform-ci-environment-contract.md) | Unknown | CI Environment Contract | Active | 2026-01-0?  | GoldenPath relies on CI pipelines to provision infrastructure, bootstrap clusters, deploy platform tooling, and tear environments down deterministically. As the system evolved, pipeline behavior be... |
| [ADR-0035](ADR-0035-platform-iam-audit-cadence.md) | Unknown | IAM Audit Cadence for CI Roles | Active | 2026-01-0?  | CI roles are intentionally broad during early iterations to keep the platform moving. Over time, unused permissions should be removed to reduce risk and increase confidence in least-privilege acces... |
| [ADR-0036](ADR-0036-platform-orphan-cleanup-workflow.md) | Unknown | Orphan Cleanup Is Manual and Decoupled From Teardown | Superseded | 2026-01-0?  | CI teardown can hang or fail when orphan cleanup is executed inline, especially when tagging permissions or AWS eventual consistency create long-running or retry-heavy cleanup loops. This reduces c... |
| [ADR-0037](ADR-0037-platform-resource-tagging-policy.md) | Unknown | Platform resource tagging policy | Active | 2026-01-0?  | GoldenPath creates and tears down short-lived environments frequently. Without consistent tags, it is difficult to audit cost, identify owners, and safely clean up orphans. We already rely on tags ... |
| [ADR-0038](ADR-0038-platform-teardown-orphan-cleanup-gate.md) | Unknown | Gate Orphan Cleanup in CI Teardown with Explicit Modes | Active | 2026-01-0?  | Teardown reliability is the weakest part of the infra lifecycle. We have seen teardown loops hang when GitOps recreates LoadBalancer Services and when orphan cleanup takes too long or is ambiguous ... |
| [ADR-0039](ADR-0039-platform-tag-scoped-iam-policy-template.md) | Unknown | Tag-Scoped IAM Policy Template for Destructive Automation | Active | 2026-01-0?  | Teardown and cleanup automation requires destructive permissions. Broad IAM policies raise the risk of deleting unintended resources, especially in shared accounts. We already enforce a platform-wi... |
| [ADR-0040](ADR-0040-platform-lifecycle-aware-state-keys.md) | Unknown | Lifecycle-aware Terraform state keys for BuildId isolation | Active | 2026-01-0?  | Ephemeral builds were reusing the persistent Terraform state key. New BuildIds would still load old state, leading to stale plans, drift reconciliation, and accidental reuse of resources. We need a... |
| [ADR-0041](ADR-0041-platform-orphan-cleanup-deletion-order.md) | Unknown | Deterministic orphan cleanup deletion order | Active | 2026-01-0?  | Orphan cleanup can fail when AWS resources are deleted out of dependency order (for example, trying to delete a subnet that still has ENIs or a route table that is still associated). We need a dete... |
| [ADR-0042](ADR-0042-platform-branching-strategy.md) | Unknown | Branching strategy (development → main) | Active | 2026-01-0?  | We need a simple, enforced branching model that keeps `main` stable and prevents direct merges from ad hoc branches. Recent work involved multiple short-lived branches, so we need a clear, document... |
| [ADR-0043](ADR-0043-platform-teardown-lb-eni-wait.md) | Unknown | Teardown waits for LoadBalancer ENIs before subnet delete | Superseded | 2026-01-0?  | Teardown has been hanging at subnet deletion because network load balancer ENIs remain after Kubernetes LoadBalancer Services are deleted. Terraform destroy or AWS deletes then fail with `Dependenc... |
| [ADR-0044](ADR-0044-platform-infra-checks-ref-mode.md) | Unknown | Configurable ref for infra checks dispatch | Superseded | 2026-01-0?  | PR Terraform Plan dispatches Infra Terraform Checks for validation. Teams need clarity on where those checks run: on the PR branch, on the target branch, or both. The default should remain simple, ... |
| [ADR-0045](ADR-0045-platform-teardown-lb-delete-default.md) | Unknown | Default LB delete when ENIs persist during teardown | Active | 2026-01-0?  | Even with the ENI wait gate, teardowns can still hang when NLB ENIs linger and the load balancer does not delete in time. Operators consistently choose the break-glass option to delete remaining cl... |
| [ADR-0046](ADR-0046-platform-pr-plan-validation-ownership.md) | Unknown | PR plan owns validation (no auto infra checks dispatch) | Active | 2026-01-0?  | The PR plan workflow has been dispatching Infra Terraform Checks automatically. This adds an extra workflow hop and creates confusion about what must run before apply. We already enforce the critic... |
| [ADR-0047](ADR-0047-platform-teardown-destroy-timeout-retry.md) | Unknown | Retry Terraform destroy after timeout with cluster-scoped LB cleanup | Active | 2026-01-0?  | Teardown can stall when Terraform destroy reaches subnet deletion while Kubernetes-created Network Load Balancer ENIs are still present. The LB cleanup step removes services, but AWS eventual consi... |
| [ADR-0048](ADR-0048-platform-teardown-version-selector.md) | Unknown | Versioned teardown runners with selectable entrypoint | Active | 2026-01-0?  | Teardown reliability depends on managed-service cleanup timing (LBs/ENIs) and Terraform destroy behaviors. Iterating on teardown logic is necessary, but changing the primary teardown script directl... |
| [ADR-0049](ADR-0049-platform-pragmatic-observability-baseline.md) | Unknown | Pragmatic observability baseline for V1 (RED + Golden Signals) | Active | 2026-01-0?  | V1 priorities emphasize reliable deployment and teardown with low operational overhead. Full distributed tracing and deep SLO mechanics are valuable, but they increase implementation complexity and... |
| [ADR-0050](ADR-0050-platform-changelog-label-gate.md) | Unknown | Label-gated changelog entries | Active | 2026-01-0?  | Changelog updates are required for material behavior changes but not for mechanical refactors or formatting fixes. A lightweight gate is needed to require entries only when change impact warrants i... |
| [ADR-0051](ADR-0051-platform-reliability-metrics-contract-minimums.md) | Unknown | Minimal reliability metrics and contract minimums | Active | 2026-01-0?  | V1 needs visible proof that build/teardown are reliable without adopting full CI observability. We also need a minimal platform contract that keeps lifecycle runs deterministic and auditable withou... |
| [ADR-0052](ADR-0052-platform-kube-prometheus-stack-bundle.md) | Unknown | Use kube-prometheus-stack as the V1 monitoring bundle | Active | 2026-01-0?  | V1 needs a deterministic, productized monitoring baseline. Today Prometheus, Grafana, and Alertmanager are installed as separate Helm charts, which increases config drift, operational overhead, and... |
| [ADR-0053](ADR-0053-platform-storage-lifecycle-separation.md) | Unknown | Separate storage lifecycle from bootstrap and teardown | Active | 2026-01-0?  | Monitoring components require PVCs to persist data. If storage add-ons are not ready at bootstrap, kube-prometheus-stack pods stay Pending and monitoring is not available. Teardown can be delayed b... |
| [ADR-0054](ADR-0054-platform-observability-exporters-otel-split.md) | Unknown | Exporter vs OpenTelemetry split for platform observability | Active | 2026-01-0?  | We need a clear and minimal observability baseline that separates infrastructure metrics from application telemetry. There has been ambiguity about whether OpenTelemetry replaces Prometheus exporte... |
| [ADR-0055](ADR-0055-platform-tempo-tracing-backend.md) | Unknown | Tempo as the standard tracing backend (V1.1) | Active | 2026-01-0?  | V1 focuses on metrics-first observability, with distributed tracing deferred to V1.1. When tracing is enabled, we need a default backend that aligns with the Grafana/Prometheus/Loki stack and integ... |
| [ADR-0056](ADR-0056-platform-loki-deployment-mode.md) | Unknown | Loki deployment mode for V1 | Active | 2026-01-0?  | We need a log storage baseline that is simple to operate in V1 while still allowing a clear path to scale and HA when log volume grows. Loki offers two common deployment modes: Single Binary and Si... |
| [ADR-0057](ADR-0057-platform-ci-terraform-force-unlock-workflow.md) | Unknown | CI Terraform force-unlock workflow (break-glass) | Active | 2026-01-0?  | Teardown and destroy runs can leave Terraform state locks when runs fail, runner pods are canceled, or a prior step exits without releasing the lock. Local `force-unlock` is risky and often unavail... |
| [ADR-0058](ADR-0058-platform-grafana-config-workflow.md) | Unknown | Separate Grafana config workflow with readiness guard | Active | 2026-01-0?  | Grafana configuration (dashboards, datasources, alert rules) is managed as code via Terraform in `idp-tooling/grafana-config/`. The Grafana API must be reachable and stable before the provider can ... |
| [ADR-0059](ADR-0059-platform-ci-workflow-index-and-ownership.md) | Unknown | CI workflow index, ownership, and UI grouping | Active | 2026-01-0?  | The CI workflow list is growing. Without a single index, naming conventions, and clear ownership markers, workflows become hard to find, easy to misuse, and harder to audit. This creates operationa... |
| [ADR-0060](ADR-0060-platform-ephemeral-update-workflow.md) | Unknown | Separate update workflow for existing ephemeral dev clusters | Active | 2026-01-0?  | Ephemeral clusters are created through a new-build workflow that enforces `new_build=true`. When operators need to update an existing ephemeral cluster (same BuildId), that guard blocks the apply. ... |
| [ADR-0061](ADR-0061-platform-observability-provisioning-boundary.md) | Unknown | Observability provisioning boundary (Helm in-cluster, Terraform external) | Active | 2026-01-0?  | We need a consistent rule for how observability is provisioned to avoid drift between GitOps (Helm/Argo) and Terraform provider configurations. Today the platform uses Helm for in-cluster observabi... |
| [ADR-0062](ADR-0062-platform-app-template-contract.md) | Unknown | App template contract for team-owned deployments | Active | 2026-01-0?  | App teams need a consistent, self-serve starting point for deploying services without re-learning platform conventions each time. Today there is no single, opinionated template that makes ownership... |
| [ADR-0063](ADR-0063-platform-terraform-helm-bootstrap.md) | Unknown | Terraform Helm Provider for Bootstrap | Active | 2026-01-0?  | Running the platform requires a complex sequence of operations: provisioning AWS infrastructure (Terraform) and then installing Kubernetes controllers like ArgoCD (Bash scripts/Helm). |
| [ADR-0064](ADR-0064-platform-dev-bootstrap-defaults.md) | Unknown | Dev bootstrap defaults off for k8s resources and storage | Active | 2026-01-0?  | Recent bootstrap runs failed when Terraform-managed Kubernetes service accounts and storage add-on checks were enabled by default. The CI bootstrap role and cluster readiness were not consistently ... |
| [ADR-0065](ADR-0065-platform-branch-policy-guard.md) | Unknown | Restore branch policy guard for main | Active | 2026-01-0?  | We require a consistent release path that flows through the development branch before reaching main. Recent changes temporarily relaxed the branch policy guard, allowing non-development branches to... |
| [ADR-0066](ADR-0066-platform-dashboards-as-code.md) | Unknown | Platform Dashboards as Code | Active | 2026-01-0?  | Observability dashboards are critical operational artifacts. However, managing them via the Grafana UI ("ClickOps") leads to: |
| [ADR-0067](ADR-0067-platform-labeler-base-ref.md) | Unknown | Use base ref for labeler checkout | Active | 2026-01-0?  | The PR labeler workflow checked out the base commit SHA. When the base SHA pointed to an older labeler config, the v5 labeler action failed due to config schema drift. This blocked PRs even when th... |
| [ADR-0068](ADR-0068-platform-review-cadence-output.md) | Unknown | Fix review cadence output delimiter | Active | 2026-01-0?  | The production readiness review cadence workflow writes multi-line output to `GITHUB_OUTPUT`. The current quoted heredoc delimiter breaks note parsing and causes the check to fail even when the scr... |
| [ADR-0069](ADR-0069-platform-observability-baseline-golden-signals.md) | Unknown | Observability baseline for golden signals in production | Superseded | 2026-01-0?  | Production needs consistent visibility into the golden signals: latency, traffic, errors, and saturation. The platform should provide an opinionated baseline that is production-grade but not overki... |
| [ADR-0070](ADR-0070-platform-terraform-aws-lb-controller.md) | Unknown | Terraform Management of AWS Load Balancer Controller | Active | 2026-01-0?  | The AWS Load Balancer Controller is a critical component that bridges Kubernetes Ingress objects to AWS Application Load Balancers (ALBs). Without it, Ingress resources (like Kong) remain in a pend... |
| [ADR-0071](ADR-0071-doc-taxonomy-refactor.md) | Unknown | Standardized Documentation Taxonomy | Active | 2026-01-0?  | The documentation structure has grown organically, leading to scattered "product-like" definitions (Requirements, Catalog, SLAs) and ambiguous homes for operational policies (Upgrade/Deprecation ru... |
| [ADR-0072](ADR-0072-platform-pr-checklist-template.md) | Unknown | PR checklist template in PR gates guide | Active | 2026-01-0?  | The PR guardrails require checklist selections in the PR body. The checklist template lives in GitHub, but contributors often do not discover it until the PR guard fails. This adds friction for onb... |
| [ADR-0073](ADR-0073-platform-bootstrap-v3-irsa-skip.md) | Unknown | Bootstrap v3 skips Terraform IRSA apply in Stage 3B | Active | 2026-01-0?  | Bootstrap Stage 3B runs a targeted Terraform apply for IRSA service accounts. When the service accounts already exist, the plan reports "No changes" and the bootstrap guard treats that as a failure... |
| [ADR-0074](ADR-0074-platform-ops-workflow-branch-guard.md) | Unknown | Ops workflow branch guard | Active | 2026-01-0?  | Ops workflows (bootstrap, teardown, orphan cleanup, managed LB cleanup) can be invoked from any branch via workflow dispatch. That increases risk of running operational jobs from stale or experimen... |
| [ADR-0075](ADR-0075-app-example-deployments.md) | Unknown | App example deployments via Argo CD, Helm, and Kustomize | Active | 2026-01-0?  | Example applications were added under `apps/`, but they lacked a consistent, repeatable packaging format for GitOps deployment. We need deterministic example apps that can be deployed via Argo CD u... |
| [ADR-0076](ADR-0076-platform-infracost-ci-visibility.md) | Unknown | Lightweight CI cost visibility with Infracost | Active | 2026-01-0?  | We want early, low-friction cost visibility for Terraform changes without blocking delivery. Cost information should surface in PRs to build a habit of cost awareness before introducing hard gates. |
| [ADR-0077](ADR-0077-platform-ci-build-teardown-log-automation.md) | Unknown | CI build/teardown log automation | Active | 2026-01-0?  | Build, bootstrap, and teardown logs provide a durable record of run outcomes, flags, and timings. Capturing them manually is inconsistent and slows post-run analysis. We need an automated, low-fric... |
| [ADR-0078](ADR-0078-platform-governed-repo-scaffolder.md) | Unknown | Governance-driven app repository scaffolder | Active | 2026-01-0?  | App repos are created ad-hoc today, which leads to missing catalog metadata, inconsistent guardrails, and drift from platform standards. We need a single, deterministic path that scaffolds a repo w... |
| [ADR-0079](ADR-0079-platform-ai-agent-governance.md) | Unknown | AI Agent Governance and Auditability | Active | 2026-01-0?  | AI agents are increasingly used for documentation, workflow updates, and automation changes. Without explicit governance, changes risk drift, poor traceability, and inconsistent QA. |
| [ADR-0080](ADR-0080-platform-github-agent-roles.md) | Unknown | GitHub App Roles for AI/Automation Access | Active | 2026-01-0?  | We need a way to grant AI and automation roles without creating new human GitHub accounts. The solution must be auditable, least-privilege, and easy to rotate. |
| [ADR-0081](ADR-0081-platform-repo-wide-linting.md) | Unknown | Repo-wide linting for knowledge-graph hygiene | Active | 2026-01-0?  | We are introducing a knowledge-graph footprint that relies on consistent YAML and Markdown. Path-scoped linting misses drift when files move or when new schemas appear across the repo. |
| [ADR-0082](ADR-0082-platform-metadata-validation.md) | Unknown | Platform Metadata Validation Strategy | Active | 2026-01-0?  | As the Golden Path IDP scales, we are introducing a "Knowledge Graph" approach to link artifacts (Code, Docs, Decisions). We need a way to enforce the integrity of these links. |
| [ADR-0083](ADR-0083-platform-metadata-backfill-protocol.md) | Unknown | Metadata Backfill Campaign Protocol | Active | 2026-01-0?  | We are adopting a metadata strategy that enables traceability and automated governance. The validator currently enforces metadata on a subset of docs, and Terraform tags are not yet validated autom... |
| [ADR-0084](ADR-0084-platform-enhanced-metadata-schema.md) | Adrs | Enhanced Metadata Schema for Knowledge Graph | Active | 2026-01-0?  | The repository contains 300+ markdown files across documentation, modules, applications, and infrastructure code. To enable Knowledge Graph capabilities and semantic search, we need a comprehensive... |
| [ADR-0085](ADR-0085-score-implementation.md) | Unknown | Implementing Score in V1 | Active | 2026-01-0?  | Our current IDP handles application scaffolding via Backstage Templates that generate standard Kubernetes manifests. While functional, this "bakes in" the platform's K8s logic into every developers... |
| [ADR-0086](ADR-0086-federated-metadata-validation.md) | Unknown | Federated Metadata Validation Strategy | Active | 2026-01-0?  | Our current metadata compliance engine (`validate_metadata.py`) is locked within the `goldenpath-idp-infra` repository. As the platform scales, new application repositories (workloads) are being cr... |
| [ADR-0087](ADR-0087-k8s-metadata-sidecars.md) | Unknown | Integration of Governance Metadata with Kubernetes Resources | Active | 2026-01-0?  | The repository has achieved 100% metadata compliance across all documentation and markdown files. This metadata enables automated health reporting, risk assessment, and lifecycle management. Howeve... |
| [ADR-0088](ADR-0088-automated-metadata-remediation.md) | Unknown | Automated Metadata Remediation over Manual Compliance | Active | 2026-01-0?  | As the repository grows (currently 316+ files), maintaining a consistent metadata schema becomes increasingly difficult if left to manual developer effort. Traditional "governance" relies on blocki... |
| [ADR-0089](ADR-0089-closed-loop-metadata-injection.md) | Unknown | Closed-Loop Metadata Injection | Active | 2026-01-0?  | We have established a robust metadata governance system using sidecars (`metadata.yaml`). However, this metadata remained isolated from the live running resources in Kubernetes. To enable field-lev... |
| [ADR-0090](ADR-0090-automated-platform-health-dashboard.md) | Unknown | Automated Platform Health Dashboard | Active | 2026-01-0?  | As the GoldenPath IDP grows, manual auditing of metadata compliance, risk profiles, and "Dark Infrastructure" becomes unsustainable. We have a reporter script (`platform_health.py`), but its output... |
| [ADR-0092](ADR-0092-ecr-registry-product-strategy.md) | Unknown | ECR Registry Product-Based Strategy & Shared Responsibility Model | Active | 2026-01-0?  | We need a clear strategy for ECR registry management that aligns with Domain-Driven Design principles and establishes clear ownership boundaries between platform and application teams. |
| [ADR-0093](ADR-0093-automated-policy-enforcement.md) | Unknown | Automated Policy Enforcement Framework | Active | 2026-01-0?  | We need policies to be enforceable, not just documentation. Manual enforcement doesn't scale and policies become stale without automation. |
| [ADR-0094](ADR-0094-automated-catalog-docs.md) | Unknown | Automated Registry Catalog Documentation | Active | 2026-01-0?  | The ECR registry catalog (`docs/registry-catalog.yaml`) is the single source of truth for all container registries, but YAML is not easily scannable for humans. Teams need a quick, readable referen... |
| [ADR-0095](ADR-0095-self-service-registry-creation.md) | Unknown | Self-Service ECR Registry Creation Workflow | Active | 2026-01-0?  | Application teams need to request ECR registries, but the current process requires manual file editing and Terraform knowledge. This creates friction and bottlenecks the platform team. |
| [ADR-0096](ADR-0096-risk-based-ecr-controls.md) | Governance | Risk-Based ECR Security Controls | Accepted | 2026-01-0?  | ECR registries have different security requirements based on their risk level. Production workloads need stronger controls (KMS encryption, immutable tags) while development environments can use li... |
| [ADR-0097](ADR-0097-domain-based-resource-catalogs.md) | Architecture | Domain-Based Resource Catalogs | Accepted | 2026-01-0?  | As the platform grows, we need to manage multiple resource types (ECR registries, RDS databases, S3 buckets, EKS clusters, etc.). We must decide between: |
| [ADR-0098](ADR-0098-standardized-pr-gates.md) | Adrs | Standardized PR Gates for ECR Pipeline | Accepted | 2026-01-0?  | The ECR pipeline PRs were experiencing repeated CI failures due to inconsistent guardrail checks, YAML linting errors, and missing metadata. Multiple workflows needed to trigger on both `main` and ... |
| [ADR-0099](ADR-0099-standardized-iam-policy-management.md) | Security | Standardized IAM Policy Management | Active | 2026-01-0?  | Previously, IAM JSON policy fragments were scattered across documentation files or placed loosely in the `docs/policies/` directory. This made it difficult to: 1.  Verify exactly what permissions w... |
| [ADR-0100](ADR-0100-standardized-ecr-lifecycle-and-documentation.md) | Governance | Standardized ECR Lifecycle and Documentation | Accepted | 2026-01-0?  | The previous ECR registry creation process required manual input for multiple redundant fields (name and ID) and suffered from a "drift gap" where the human-readable [REGISTRY_CATALOG.md](docs/REGI... |
| [ADR-0101](ADR-0101-pr-metadata-auto-heal.md) | Governance | PR Metadata Auto-Heal and Scoped Validation | Active | 2026-01-0?  | The platform's metadata validation workflow was blocking PRs due to: 1. **Full-repo scanning**: Any `.md` file change triggered validation of the entire repository, causing unrelated failures 2. **... |
| [ADR-0102](ADR-0102-terraform-fast-validation.md) | Architecture | Layer 2 Terraform Validation (Fast Feedback Loop) | Accepted | 2026-01-06 | Currently, Terraform validation primarily occurs during the `env=dev` integration tests (`infra-terraform-apply-dev.yml`) or via `pr-terraform-plan.yml`. These workflows require AWS credentials, ba... |
| [ADR-0103](ADR-0103-automated-workflow-docs.md) | Documentation | Automated CI Workflow Documentation | Superseded | 2026-01-06 | As the complexity of the platform grows, the number of GitHub Actions workflows has increased significantly (>30 workflows). Maintaining a manual index of these workflows (`ci-workflows/CI_WORKFLOW... |
| [ADR-0104](ADR-0104-automated-script-docs.md) | Documentation | Automated Script Documentation | Superseded | 2026-01-06 | The platform relies on a large suite of Python and Shell scripts (~25) for governance, documentation, and delivery. Maintaining a manual index of these scripts (`scripts/index.md`) is tedious and e... |
| [ADR-0110](ADR-0110-idp-knowledge-graph-architecture.md) | Architecture | IDP Knowledge Graph Node Architecture | Accepted | 2026-01-06 | The GoldenPath IDP currently uses disconnected YAML sidecars (`metadata.yaml`) to track component attributes. While metadata compliance is high (98.7%), we lacks a structured way to understand **re... |
| [ADR-0111](ADR-0111-platform-documentation-auto-healing.md) | Documentation | Automated Documentation Auto-Healing | Accepted | 2026-01-0?  | Our platform uses automated indexing scripts (`generate_script_index.py`, `generate_workflow_index.py`) to maintain documentation portals (`scripts/index.md`, `ci-workflows/CI_WORKFLOWS.md`). |
| [ADR-0112](ADR-0112-automated-adr-index-generation.md) | Architecture | Automated ADR Index Generation | Accepted | 2026-01-06 | As the number of Architecture Decision Records (ADRs) grows (currently 100+), keeping the `01_adr_index.md` in sync manually has become error-prone. We frequently observe drift in statuses, dates, ... |
<!-- ADR_TABLE_END -->

---

## Superseded ADRs

- [ADR-0069](ADR-0069-platform-observability-baseline-golden-signals.md) — superseded by `ADR-0049-platform-pragmatic-observability-baseline.md`.
- [ADR-0036](ADR-0036-platform-orphan-cleanup-workflow.md) — superseded by `ADR-0038-platform-teardown-orphan-cleanup-gate.md`.
- [ADR-0043](ADR-0043-platform-teardown-lb-eni-wait.md) — superseded by `ADR-0045-platform-teardown-lb-delete-default.md`.
- [ADR-0044](ADR-0044-platform-infra-checks-ref-mode.md) — superseded by `ADR-0046-platform-pr-plan-validation-ownership.md`.
- [ADR-0103](ADR-0103-automated-workflow-docs.md) — superseded by `ADR-0111-platform-documentation-auto-healing.md`.
- [ADR-0104](ADR-0104-automated-script-docs.md) — superseded by `ADR-0111-platform-documentation-auto-healing.md`.

Legacy aliases (kept to preserve historical links):

- `docs/adrs/ADR-0011-platform-ci-environment-contract.md` → `ADR-0034-platform-ci-environment-contract.md`

---

## New ADRs

When introducing a new ADR:

- Follow the Domain convention (Platform or Application).
- Use the filename pattern: `ADR-XXXX-(platform|app)-short-title.md`.
- Add the entry to the Active ADRs table with its Domain.

---

## Conventions

- **Numbering:** `ADR-0001`, `ADR-0002`, … (sequential, never reused)
- **Filename:** `ADR-XXXX-(platform|app)-short-title.md`
- **Domain:** `Platform` or `Application`
- **Status values:** `Proposed`, `Accepted`, `Deprecated`, `Superseded`
- **Changing a decision:** write a new ADR that **supersedes** the old one and link both.

---

## Adding a new ADR

1. Copy the standard template.

2. Create `docs/adrs/ADR-XXXX-(platform|app)-title.md`.

3. Fill in Domain, context, decision, tradeoffs, and follow-ups.

4. Open a PR.

5. Update this index.
