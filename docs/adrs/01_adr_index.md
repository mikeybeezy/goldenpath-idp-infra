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
| [ADR-0011](ADR-0011-platform-observability-baseline-golden-signals.md) | Platform | Observability baseline for golden signals in production | Proposed | 2025-12-23 | Minimal stack for golden signals: metrics, logs, traces, alerts. |
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

---

## Superseded ADRs

- [ADR-0011](ADR-0011-platform-ci-environment-contract) — superseded by `ADR-0034-platform-ci-environment-contract.md`.
- [ADR-0036](ADR-0036-platform-orphan-cleanup-workflow.md) — superseded by `ADR-0038-platform-teardown-orphan-cleanup-gate.md`.

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
