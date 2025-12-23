# Governance Model – Golden Path IDP (V1 Draft)

This document captures the initial operating model for the Golden Path Internal Developer Platform. It outlines how platform capabilities are governed in V1, including observability, security, CI/CD flows, and change control.

---

## 1. Scope & Principles

1. **Platform is the product** – run the IDP like a product: version-controlled infrastructure, PR-driven changes, and clear ownership.
2. **Golden paths before options** – V1 supports a narrow set of service archetypes (stateless web/API) plus a single runtime (Kubernetes via EKS).
3. **Familiar tools, convergent outcomes** – developers can use GitHub Actions, GitLab CI, or Tekton pipelines, provided they adhere to the platform contracts (artifact signing, manifests in GitOps repos, tests passing).
4. **Security & observability are invisible** – baseline guardrails (SSO, RBAC, secrets, logging) come preconfigured; developers shouldn’t have to wire them manually.

---

## 2. Observability & SLO Governance

### Ownership Split

| Layer | Owner (RACI) | Required Signals | Tooling | Notes |
|-------|--------------|------------------|---------|-------|
| **Platform (EKS, networking, GitOps, Backstage)** | Platform Team **(R/A)**, Security **(C)**, App Teams **(I)** | Latency, traffic, errors, saturation (Golden Signals) + control-plane health | Prometheus, Loki, Fluent Bit, Tempo/Jaeger, Grafana | Platform maintains dashboards/alerts and publishes platform SLOs (e.g., ingress availability ≥ 99.99%). |
| **Shared Services (Ingress, IdP, CI)** | Service Owner **(R)**, Platform **(A)** | Availability, throughput, error rate, queue depth | Prometheus, synthetic checks | Service owner documents SLO + runbooks in Backstage; platform ensures telemetry plumbing. |
| **Applications / Workloads** | App Team **(R/A)**, Platform **(C)**, Security **(I)** | Golden signals + business SLOs (availability, latency, error budget) | OpenTelemetry SDKs, platform-provided log/trace exporters | Apps must register SLOs in Backstage, wire alerts to their on-call rotation, and honor error budgets. |

### Enforcement Rules

1. All workloads emit the four golden signals through platform-provided exporters.
2. Grafana dashboards and Prometheus alert rules for platform SLOs are centrally managed; app teams inherit templates but tune thresholds.
3. Fluent Bit ships logs to Loki; required labels: `environment`, `namespace`, `application`, `service`.
4. Tempo/Jaeger collects traces tagged with service + environment; new templates include tracing instrumentation by default.
5. SLOs: Platform owns platform-grade SLOs (ingress, cluster health, GitOps latency). App teams own their service SLOs and error budgets.

### Log & Metric Pipeline

- **Metrics**: Prometheus scrapes clusters + workloads; dashboards shipped in Grafana per environment.
- **Logs**: Fluent Bit → Loki (default 14-day retention; archival optional).
- **Traces**: Tempo/Jaeger for distributed traces; mandatory instrumentation baked into templates.
- **SLO Registry**: Backstage stores links to service SLO docs and current targets.

---

## 3. Security & Identity

| Area | Governance Decision | Implementation Notes |
|------|--------------------|----------------------|
| **Identity Provider** | OIDC via Keycloak/Auth0/Ory (final selection based on org preference). | Integrate with Backstage, Argo CD, and Kubernetes API via OIDC. |
| **RBAC** | Namespace-level roles (dev, ops, read-only). | Managed through Terraform modules; no direct cluster-admin for app teams. |
| **Secrets** | HashiCorp Vault as primary, AWS Secrets Manager fallback. | External Secrets operator syncs secrets into namespaces. Switching backends is a configuration choice in env tfvars. |
| **Image scanning** | Baseline scanning in CI plus periodic registry scans. | Enforce via GitHub/GitLab/Tekton pipelines; log results in Backstage. |
| **Policy enforcement** (V2) | OPA/Kyverno to ensure required labels, resource limits, etc. | Defer to V2 once core identity + secrets are stable. |

---

## 4. CI/CD & GitOps Workflow

1. **CI Stage** (per repo)
   - Developers choose GitHub Actions, GitLab CI, or Tekton pipeline templates supplied by the platform.
   - Required quality gates: `terraform fmt/validate`, `tflint`, `tfsec/checkov` (infra), unit/integration tests (apps).
   - Successful CI publishes signed container images/artefacts referenced in GitOps manifests.

2. **GitOps Stage**
   - Argo CD watches a dedicated GitOps repo per environment.
   - Promotion via PR merge into target environment folder (`envs/{dev|staging|prod}`).
   - No direct `kubectl apply`; drift is reconciled by the GitOps controller.

3. **Automation Wrapper**
   - `Makefile` targets (`make init/plan/apply ENV=...`) standardize Terraform usage.
   - Transition plan to introduce Atlantis for PR-driven plan/apply with manual approval on infra repos.

---

## 5. Change Management & Release Workflow

| Step | Description | Approvers (RACI) |
|------|-------------|------------------|
| **Infrastructure (Terraform)** | PR raised against env modules; `make plan ENV=<env>` output (or Atlantis plan) attached. | Platform **R/A**, App Teams **C**, Security **I** |
| **GitOps Manifests** | PR into GitOps repo’s env folder; Argo CD applies post-merge. | Service Owner **R/A**, Platform **C** (prod), Security **I** |
| **Backstage Templates** | PR to template repo; scaffold tested locally. | Platform DX **R/A**, App Teams **C**, Security **I** |
| **Observability/SLO updates** | Update dashboards, Prometheus rules, and Backstage SLO docs. | Platform **R/A** for platform signals; App Teams **R/A** for app signals |

Cadence expectations:

- Non-prod: weekly release window (auto-approved if CI passes).
- Prod: twice monthly; prod merges require both service owner and platform sign-off.
- Emergency fixes: allowed with fast-track approval but must undergo post-incident review within 24 hours.

---

## 6. Responsibilities

| Domain | Platform Team | Application Teams |
|--------|---------------|-------------------|
| Infrastructure modules, env overlays | Own design, upkeep, and guardrails. | Consume modules; request new features via issues. |
| CI/CD templates | Provide + maintain templates, quality gates. | Use templates; extend only via approved hooks. |
| Observability stack | Maintain Prometheus/Loki/Tempo, dashboards, alert routing. | Ensure services emit metrics/logs/traces; define service SLOs. |
| Security (identity, secrets) | Operate IdP, Vault/ASM, RBAC policies. | Integrate apps with provided auth/secrets patterns. |
| Backstage catalog | Seed templates, maintain plugins. | Keep service metadata current, link runbooks/SLOs. |

---

## 7. Roadmap Notes

- **V1**: Deliver core networking, GitOps pipeline, optional compute module, Backstage basics, observability stack with golden signals, secrets via Vault/ASM, CI/CD templates.
- **V2**: Add service mesh, OPA/Kyverno policies, advanced scorecards, multi-cluster management, automated governance metrics.

This governance README will evolve as each capability graduates from planned to in-place. Use it as the source of truth for expectations around platform adoption and operations.

---

## 8. In-Progress Governance Items

| Area | Focus | Status | Notes |
|------|-------|--------|-------|
| **Incident Response & Runbooks** | Define incident commander roles, communication channels (Slack/Teams), escalation matrix, and postmortem SLAs. | 🚧 In progress | Platform team drafting runbook templates; app teams will link service runbooks via Backstage. Target: 24h postmortem policy. |
| **Secret Rotation & Key Management** | Document how AWS Secrets Manager entries are rotated (automation vs manual), trigger ownership, and notification paths. | 🚧 In progress | Evaluating EventBridge/Lambda rotation hooks; rotation cadence per secret class (DB creds monthly, API keys quarterly). Ownership split between platform (infra secrets) and app teams (app secrets). |
| **Compliance & Audit Logging** | Specify where platform decisions (approvals, infra changes) are logged, retention, and access controls. | 🚧 In progress | Plan: rely on Git history + Atlantis logs + centralized logging. Define retention (e.g., ≥12 months) and audit access policies per org requirements. |
