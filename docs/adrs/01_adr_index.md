# ADR Index (GoldenPath IDP)

This index lists Architecture Decision Records (ADRs) for GoldenPath IDP.

## How to use this

- ADRs document **what we decided**, **why**, and **tradeoffs**.
- Decisions should be changed by **superseding** an ADR (create a new one), not rewriting history.

> Location: `docs/adrs/`

---

## Active ADRs

| ADR | Domain | Title | Status | Date | Summary |
| --- | --- | --- | --- | --- | --- |
| [ADR-0001](ADR-0001-platform-argocd-as-gitops-operator.md) | Platform | Adopt Argo CD as GitOps controller for platform deployments | Accepted | 2025-12-26 | Argo CD is the source of truth for in-cluster platform apps and reconciliation. |
| [ADR-0002](ADR-0002-platform-Kong-as-ingress-API-gateway.md) | Platform | Use Kong as the primary ingress/API gateway behind an internal NLB | Accepted | 2025-12-26 | Kong is the front door; internal NLB is the secure-by-default entrypoint. |
| [ADR-0003](ADR-0003-platform-AWS-IAM-bootstrap-IRSA-SSM-.md) | Platform | Use AWS IAM bootstrap, IRSA for pod-to-AWS, and SSM for node break-glass | Accepted | 2025-12-26 | IAM for bootstrap, IRSA for least-privilege controllers, SSM replaces SSH by default. |
| [ADR-0004](ADR-0004-platform-datree-policy-as-code-in-ci.md) | Platform | Use Datree as Kubernetes policy-as-code gate in CI | Accepted | 2025-12-26 | CI policy gate blocks obvious manifest violations before GitOps applies. |
| [ADR-0005](ADR-0005-app-keycloak-as-identity-provider-for-human-sso.md) | Application | Adopt Keycloak for platform SSO (humans), separate from IRSA | Accepted | 2025-12-26 | Keycloak planned for SSO; not a hard V1 bootstrap dependency. |
| [ADR-0006](ADR-0006-platform-secrets-strategy.md) | Platform | Use AWS Secrets Manager/SSM + External Secrets; no secrets in Git | Accepted | 2025-12-26 | AWS is system of record; cluster secrets are hydrated via ESO; block secret commits. |
| [ADR-0007](ADR-0007-platform-environment-model.md) | Platform | Environment model balances cost, speed, and credible separation | Accepted | 2025-12-26 | V1 starts single-cluster/4 namespaces; upgrade path to 2 clusters; 4 clusters deferred. |
| [ADR-0008](ADR-0008-app-backstage-portal.md) | Application | Use Backstage as developer portal and V1 demo app for promotion | Accepted | 2025-12-26 | Backstage deployed via GitOps; used to prove CI→GitOps→promotion loop. |
| [ADR-0009](ADR-0009-app-delivery-insights.md) | Application | CI/CD observability via OpenTelemetry (“Delivery Insights”) | Accepted | 2025-12-26 | Optional OTel-based delivery insights for CI pipelines. |
| [ADR-0010](ADR-0010-platform-terraform-lockfile-stability.md) | Platform | Enforce Terraform lockfile stability in CI | Accepted | 2025-12-26 | CI validates against committed lockfiles; upgrades are manual and reviewed. |
| [ADR-0012](ADR-0012-platform-repo-decoupling-options.md) | Platform | Repo decoupling options for infra and platform tooling | Accepted | 2025-12-26 | Monorepo now; move to two-repo split when dev baseline is stable. |
| [ADR-0013](ADR-0013-platform-argo-app-management-approach.md) | Platform | Argo CD app management approach for current scale | Accepted | 2025-12-26 | Use app-of-apps now; defer ApplicationSet until scale demands it. |
| [ADR-0014](ADR-0014-platform-ci-local-preflight-checks.md) | Platform | Local preflight checks before PRs | Proposed | 2025-12-26 | Baseline local checks; CI remains authoritative; `act` is recommended. |
| [ADR-0015](ADR-0015-platform-aws-oidc-for-github-actions.md) | Platform | Use AWS OIDC for GitHub Actions authentication | Proposed | 2025-12-26 | Replace long-lived AWS keys with short-lived OIDC role assumption. |
| [ADR-0016](ADR-0016-platform-ci-environment-separation.md) | Platform | CI environment separation and manual promotion gates | Proposed | 2025-12-26 | Single workflow; environment approvals; per-env roles and backends. |
| [ADR-0017](ADR-0017-platform-policy-as-code.md) | Platform | Policy as code for infrastructure changes | Proposed | 2025-12-26 | Enforce Terraform guardrails in CI with a minimal policy set. |
| [ADR-0018](ADR-0018-platform-container-registry-standard.md) | Platform | Container registry standard — ECR default, GHCR supported, Docker Hub discouraged | Proposed | 2025-12-27 | Opinionated default registry for AWS/EKS with supported alternatives. |
| [ADR-0019](ADR-0019-platform-pre-commit-hooks.md) | Platform | Pre-commit hooks as local quality gates | Proposed | 2025-12-27 | Require local hooks; CI remains authoritative. |
| [ADR-0020](ADR-0020-platform-helm-kustomize-hybrid.md) | Platform | Hybrid GitOps approach with Helm and Kustomize | Proposed | 2025-12-27 | Use Helm for packaged apps and Kustomize for env overlays. |
| [ADR-0021](ADR-0021-platform-pr-terraform-plan.md) | Platform | PR Terraform plan with automated comments | Proposed | 2025-12-27 | PR plan output posted as a comment; no apply. |
| [ADR-0022](ADR-0022-platform-post-apply-health-checks.md) | Platform | Post-apply health checks for platform readiness | Proposed | 2025-12-27 | Health checks gate apply success. |
| [ADR-0023](ADR-0023-platform-ci-image-scanning.md) | Platform | CI image scanning standard | Proposed | 2025-12-27 | Trivy default gate; optional layers. |
| [ADR-0024](ADR-0024-platform-security-floor-v1.md) | Platform | Security floor for V1 | Proposed | 2025-12-27 | Minimal security baseline for V1. |
| [ADR-0025](ADR-0025-platform-boundaries-contract.md) | Platform | Platform boundaries and contract | Proposed | 2025-12-27 | Single boundary contract referenced by governance and onboarding. |
| [ADR-0026](ADR-0026-platform-cd-deployment-contract.md) | Platform | CD deployment contract | Proposed | 2025-12-27 | Formal deployment semantics for GitOps. |
| [ADR-0027](ADR-0027-platform-design-philosophy.md) | Platform | Platform design philosophy and reference implementation | Proposed | 2025-12-27 | Preserve the founding philosophy and treat the platform as the reference path. |
| [ADR-0028](ADR-0028-platform-dev-branch-gate.md) | Platform | Dev branch gate before main | Proposed | 2025-12-27 | Require dev branch apply success before promotion to main. |
| [ADR-0029](ADR-0029-platform-dev-plan-gate.md) | Platform | Dev plan gate before dev apply | Accepted | 2025-12-27 | Require a dev plan before any dev apply on the same SHA. |
| [ADR-0030](ADR-0030-platform-precreated-iam-policies.md) | Platform | Pre-create IAM policies for IRSA controllers in V1 | Accepted | 2025-12-28 | Pre-create autoscaler and LB controller policies; attach via ARNs. |
| [ADR-0031](ADR-0031-platform-bootstrap-irsa-service-accounts.md) | Platform | Create IRSA service accounts during bootstrap | Accepted | 2025-12-28 | Bootstrap creates required IRSA service accounts before controllers. |
| [ADR-0032](ADR-0032-platform-eks-access-model.md) | Platform | EKS access model (bootstrap admin vs steady-state access) | Accepted | 2025-12-28 | Use access entries for humans; split CI bootstrap vs steady-state access. |
| [ADR-0033](ADR-0033-platform-ci-orchestrated-modes.md) | Platform | CI orchestrated modes for infra lifecycle | Accepted | 2025-12-28 | Explicit build+bootstrap, bootstrap-only, teardown modes. |
| [ADR-0034](ADR-0034-platform-ci-environment-contract.md) | Platform | CI environment contract | Accepted | 2025-12-27 | Formalize CI environment variables as a governed interface. |
| [ADR-0035](ADR-0035-platform-iam-audit-cadence.md) | Platform | IAM audit cadence for CI roles | Proposed | 2025-12-28 | Periodic IAM audits to tighten CI roles based on actual usage. |
| [ADR-0037](ADR-0037-platform-resource-tagging-policy.md) | Platform | Platform resource tagging policy | Accepted | 2025-12-28 | Standard tag set for audit, cost, and cleanup consistency. |
| [ADR-0038](ADR-0038-platform-teardown-orphan-cleanup-gate.md) | Platform | Gate orphan cleanup in CI teardown with explicit modes | Proposed | 2025-12-29 | Cleanup mode is explicit (`delete`, `dry_run`, `none`) with a default delete for ephemeral runs. |
| [ADR-0039](ADR-0039-platform-tag-scoped-iam-policy-template.md) | Platform | Tag-scoped IAM policy template for destructive automation | Proposed | 2025-12-29 | Standard template for tag-scoped deletes; read-only discovery remains unscoped. |
| [ADR-0040](ADR-0040-platform-lifecycle-aware-state-keys.md) | Platform | Lifecycle-aware Terraform state keys for BuildId isolation | Proposed | 2025-12-29 | Ephemeral runs use per-BuildId state keys; persistent uses a stable key. |
| [ADR-0041](ADR-0041-platform-orphan-cleanup-deletion-order.md) | Platform | Deterministic orphan cleanup deletion order | Proposed | 2025-12-29 | Enforce a dependency-safe deletion order for tagged orphan cleanup. |
| [ADR-0042](ADR-0042-platform-branching-strategy.md) | Platform | Branching strategy (development → main) | Proposed | 2025-12-29 | All changes merge into development first; only development promotes to main. |
| [ADR-0043](ADR-0043-platform-teardown-lb-eni-wait.md) | Platform | Teardown waits for LoadBalancer ENIs before subnet delete | Proposed | 2025-12-30 | Add an ENI wait gate and break-glass LB delete to prevent subnet hangs. |
| [ADR-0045](ADR-0045-platform-teardown-lb-delete-default.md) | Platform | Default LB delete when ENIs persist during teardown | Proposed | 2025-12-30 | Default to cluster-scoped LB deletion when ENIs linger. |
| [ADR-0046](ADR-0046-platform-pr-plan-validation-ownership.md) | Platform | PR plan owns validation (no auto infra checks dispatch) | Proposed | 2025-12-30 | Remove infra-checks auto-dispatch; PR plan is the validation gate. |
| [ADR-0047](ADR-0047-platform-teardown-destroy-timeout-retry.md) | Platform | Retry Terraform destroy after timeout with cluster-scoped LB cleanup | Proposed | 2025-12-30 | Cap destroy time, clean up cluster-tagged LBs, and retry once. |
| [ADR-0048](ADR-0048-platform-teardown-version-selector.md) | Platform | Versioned teardown runners with selectable entrypoint | Proposed | 2025-12-30 | Keep v1 stable while iterating on v2; selection via `TEARDOWN_VERSION`. |
| [ADR-0049](ADR-0049-platform-pragmatic-observability-baseline.md) | Platform | Pragmatic observability baseline for V1 (RED + Golden Signals) | Proposed | 2025-12-31 | Metrics-first baseline; traces deferred to V1.1. |
| [ADR-0050](ADR-0050-platform-changelog-label-gate.md) | Platform | Label-gated changelog entries | Proposed | 2025-12-31 | Require changelog entries only when a PR carries a label. |
| [ADR-0051](ADR-0051-platform-reliability-metrics-contract-minimums.md) | Platform | Minimal reliability metrics and contract minimums | Proposed | 2025-12-31 | Build/teardown timing summary plus minimal tag/CI/changelog contract. |
| [ADR-0052](ADR-0052-platform-kube-prometheus-stack-bundle.md) | Platform | Use kube-prometheus-stack as the V1 monitoring bundle | Proposed | 2025-12-31 | Replace standalone Prometheus/Grafana/Alertmanager with a single bundle and PVC-backed persistence. |
| [ADR-0053](ADR-0053-platform-storage-lifecycle-separation.md) | Platform | Separate storage lifecycle from bootstrap and teardown | Proposed | 2025-12-31 | Storage add-ons required at bootstrap; cleanup is an explicit workflow. |
| [ADR-0054](ADR-0054-platform-observability-exporters-otel-split.md) | Platform | Exporter vs OpenTelemetry split for platform observability | Proposed | 2025-12-31 | Infra metrics stay on exporters; app telemetry uses OpenTelemetry; cAdvisor via kubelet. |
| [ADR-0055](ADR-0055-platform-tempo-tracing-backend.md) | Platform | Tempo as the standard tracing backend (V1.1) | Proposed | 2025-12-31 | Tempo selected for OTel traces when tracing is enabled; deployed separately from kube-prometheus-stack. |
| [ADR-0056](ADR-0056-platform-loki-deployment-mode.md) | Platform | Loki deployment mode for V1 | Proposed | 2025-12-31 | Default to single-binary Loki; switch to simple scalable when scale/HA demands it. |
| [ADR-0057](ADR-0057-platform-ci-terraform-force-unlock-workflow.md) | Platform | CI Terraform force-unlock workflow (break-glass) | Proposed | 2025-12-31 | Manual CI workflow to force-unlock stuck Terraform state keys. |
| [ADR-0058](ADR-0058-platform-grafana-config-workflow.md) | Platform | Separate Grafana config workflow with readiness guard | Proposed | 2025-12-31 | Grafana config applied via manual workflow with readiness check. |
| [ADR-0059](ADR-0059-platform-ci-workflow-index-and-ownership.md) | Platform | CI workflow index, ownership, and UI grouping | Proposed | 2025-12-31 | Single workflow index with naming prefixes and owner/runbook metadata. |
| [ADR-0060](ADR-0060-platform-ephemeral-update-workflow.md) | Platform | Separate update workflow for existing ephemeral dev clusters | Proposed | 2025-12-31 | Manual update workflow with plan and state guards for existing BuildIds. |
| [ADR-0061](ADR-0061-platform-observability-provisioning-boundary.md) | Platform | Observability provisioning boundary (Helm in-cluster, Terraform external) | Proposed | 2025-12-31 | Helm for in-cluster observability; Terraform for external/SaaS observability. |
| [ADR-0062](ADR-0062-platform-app-template-contract.md) | Platform | App template contract for team-owned deployments | Proposed | 2025-12-31 | Reference app bundle with explicit platform vs app ownership. |
| [ADR-0072](ADR-0072-platform-pr-checklist-template.md) | Platform | PR checklist template in PR gates guide | Proposed | 2026-01-02 | Copy PR checklist into PR gates doc to reduce guardrail friction. |
| [ADR-0073](ADR-0073-platform-bootstrap-v3-irsa-skip.md) | Platform | Bootstrap v3 skips Terraform IRSA apply in Stage 3B | Proposed | 2026-01-02 | v3 bootstrap validates service accounts only to avoid IRSA plan failures. |
| [ADR-0074](ADR-0074-platform-ops-workflow-branch-guard.md) | Platform | Ops workflows restricted to main and development | Accepted | 2026-01-03 | Guard ops workflows to reduce drift from feature branches. |
| [ADR-0075](ADR-0075-app-example-deployments.md) | Platform | App example deployments via Argo CD, Helm, and Kustomize | Accepted | 2026-01-03 | Standardize example app packaging and GitOps app manifests. |
| [ADR-0076](ADR-0076-platform-infracost-ci-visibility.md) | Platform | Lightweight CI cost visibility with Infracost | Accepted | 2026-01-03 | Post cost visibility in PRs without gating. |
| [ADR-0077](ADR-0077-platform-ci-build-teardown-log-automation.md) | Platform | CI build/teardown log automation | Proposed | 2026-01-03 | Auto-generate build and teardown log entries from CI runs. |
| [ADR-0078](ADR-0078-platform-governed-repo-scaffolder.md) | Platform | Governance-driven app repository scaffolder | Proposed | 2026-01-03 | Scaffolds app repos with required metadata via Backstage or workflow. |
| [ADR-0079](ADR-0079-platform-ai-agent-governance.md) | Platform | AI agent governance and auditability | Proposed | 2026-01-03 | Establish guardrails, QA expectations, and auditability for AI changes. |
| [ADR-0080](ADR-0080-platform-github-agent-roles.md) | Platform | GitHub App roles for AI/automation access | Proposed | 2026-01-03 | Define least-privilege roles without human accounts. |
| [ADR-0081](ADR-0081-platform-repo-wide-linting.md) | Platform | Repo-wide linting for knowledge-graph hygiene | Proposed | 2026-01-03 | Run Markdown/YAML lint repo-wide with template ignores. |
| [ADR-0082](ADR-0082-platform-metadata-validation.md) | Platform | Metadata validation strategy | Proposed | 2026-01-03 | Validate metadata frontmatter for governance and traceability. |
| [ADR-0083](ADR-0083-platform-metadata-backfill-protocol.md) | Platform | Metadata backfill campaign protocol | Proposed | 2026-01-03 | Define deterministic backfill steps and audit artifacts. |

---

## Superseded ADRs

- [ADR-0069](ADR-0069-platform-observability-baseline-golden-signals.md) — superseded by `ADR-0049-platform-pragmatic-observability-baseline.md`.
- [ADR-0036](ADR-0036-platform-orphan-cleanup-workflow.md) — superseded by `ADR-0038-platform-teardown-orphan-cleanup-gate.md`.
- [ADR-0043](ADR-0043-platform-teardown-lb-eni-wait.md) — superseded by `ADR-0045-platform-teardown-lb-delete-default.md`.
- [ADR-0044](ADR-0044-platform-infra-checks-ref-mode.md) — superseded by `ADR-0046-platform-pr-plan-validation-ownership.md`.

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
