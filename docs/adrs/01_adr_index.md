# ADR Index (GoldenPath IDP)

This index lists Architecture Decision Records (ADRs) for GoldenPath IDP.

**How to use this**
- ADRs document **what we decided**, **why**, and **tradeoffs**.
- Decisions should be changed by **superseding** an ADR (create a new one), not rewriting history.

> Location: `docs/adrs/`

- --

## Active ADRs

| ADR | Title | Status | Date | Summary |
|---|---|---|---|---|
| ADR-0001 | Adopt Argo CD as GitOps controller for platform deployments | Accepted | 2025-12-26 | Argo CD is the source of truth for in-cluster platform apps and reconciliation. |
| ADR-0002 | Use Kong as the primary ingress/API gateway behind an internal NLB | Accepted | 2025-12-26 | Kong is the front door; internal NLB is the secure-by-default entrypoint. |
| ADR-0003 | Use AWS IAM bootstrap, IRSA for pod-to-AWS, and SSM for node break-glass | Accepted | 2025-12-26 | IAM for bootstrap, IRSA for least-privilege controllers, SSM replaces SSH by default. |
| ADR-0004 | Use Datree as Kubernetes policy-as-code gate in CI | Accepted | 2025-12-26 | CI policy gate blocks obvious manifest violations before GitOps applies. |
| ADR-0005 | Adopt Keycloak for platform SSO (humans), separate from IRSA | Accepted | 2025-12-26 | Keycloak planned for SSO; not a hard V1 bootstrap dependency. |
| ADR-0006 | Use AWS Secrets Manager/SSM + External Secrets; no secrets in Git | Accepted | 2025-12-26 | AWS is system of record; cluster secrets are hydrated via ESO; block secret commits. |
| [ADR-0007](ADR-0007-environment-model.md) | Environment model balances cost, speed, and credible separation | Accepted | 2025-12-26 | V1 starts single-cluster/4 namespaces; upgrade path to 2 clusters; 4 clusters deferred. |
| [ADR-0008](ADR-0008-backstage-portal.md) | Use Backstage as developer portal and V1 demo app for promotion | Accepted | 2025-12-26 | Backstage deployed via GitOps; used to prove CI→GitOps→promotion loop. |
| [ADR-0009](ADR-0009-delivery-insights.md) | CI/CD observability via OpenTelemetry (“Delivery Insights”) | Accepted | 2025-12-26 | Optional OTel-based delivery insights for CI pipelines. |
| [ADR-0010](ADR-0010-terraform-lockfile-stability.md) | Enforce Terraform lockfile stability in CI | Accepted | 2025-12-26 | CI validates against committed lockfiles; upgrades are manual and reviewed. |
| [ADR-0011](ADR-0011-observability-baseline-golden-signals.md) | Observability baseline for golden signals in production | Proposed | 2025-12-23 | Minimal stack for golden signals: metrics, logs, traces, alerts. |
| [ADR-0012](ADR-0012-repo-decoupling-options.md) | Repo decoupling options for infra and platform tooling | Accepted | 2025-12-26 | Monorepo now; move to two-repo split when dev baseline is stable. |
| [ADR-0013](ADR-0013-argo-app-management-approach.md) | Argo CD app management approach for current scale | Accepted | 2025-12-26 | Use app-of-apps now; defer ApplicationSet until scale demands it. |
| [ADR-0014](ADR-0014-ci-local-preflight-checks.md) | Local preflight checks before PRs | Proposed | 2025-12-26 | Baseline local checks; CI remains authoritative; `act` is recommended. |
| [ADR-0015](ADR-0015-aws-oidc-for-github-actions.md) | Use AWS OIDC for GitHub Actions authentication | Proposed | 2025-12-26 | Replace long-lived AWS keys with short-lived OIDC role assumption. |

- --

## Superseded ADRs

_None yet._

- --

## Conventions

- **Numbering:** `ADR-0001`, `ADR-0002`, … (sequential, never reused)
- **Filename:** `ADR-XXXX-short-title.md`
- **Status values:** `Proposed`, `Accepted`, `Deprecated`, `Superseded`
- **Changing a decision:** write a new ADR that **supersedes** the old one and link both.
- --

## Adding a new ADR

1. Copy the standard template.

2. Create `docs/adrs/ADR-XXXX-title.md`.

3. Fill in context, decision, tradeoffs, and follow-ups.

4. Open a PR.

5. Update this index.
