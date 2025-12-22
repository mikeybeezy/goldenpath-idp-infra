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

| Layer | Signals | Tooling | Governance Notes |
|-------|---------|---------|------------------|
| **Platform (EKS, networking, control plane)** | Four golden signals (latency, traffic, errors, saturation), plus health checks on cluster components. | Prometheus, Loki, Fluent Bit, Tempo/Jaeger, Grafana dashboards. | Platform team owns dashboards + alerting rules. Targets: 99.5% control plane availability, GitOps sync latency < 5 minutes, cluster node health SLOs per environment. |
| **Shared services (Ingress, GitOps, Backstage)** | Availability, request rate, error rate, queue depth. | Prometheus + Loki + synthetic checks. | Service owners define SLOs (e.g., Backstage 99.0% availability) and publish runbooks linked from the catalog. |
| **Application tier** | Golden signals instrumented via OpenTelemetry SDKs/shims. | Developers emit traces/logs/metrics; platform ships Fluent Bit DaemonSet to forward logs. | Platform enforces instrumentation defaults (Helm chart values) so new services emit metrics/logs/traces automatically. Teams define app-specific SLOs but must register them in Backstage. |

### Log & Metric Pipeline
- **Metrics**: Prometheus scrapes cluster + workload metrics; Grafana dashboards provided for platform and app teams.
- **Logs**: Fluent Bit ships logs to Loki (or ELK if required). Default retention 14 days; longer retention optional via centralized bucket/archive.
- **Traces**: Tempo/Jaeger stack collects distributed traces tagged by service/environment.
- **SLO Management**: Basic SLO templates provided (e.g., availability/error budget). Teams document SLO targets in Backstage.

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
   - Argo CD / Flux watches a dedicated GitOps repo per environment.
   - Promotion via PR merge into target environment folder (`envs/{dev|staging|prod}`).
   - No direct `kubectl apply`; drift is reconciled by the GitOps controller.

3. **Automation Wrapper**
   - `Makefile` targets (`make init/plan/apply ENV=...`) standardize Terraform usage.
   - Transition plan to introduce Atlantis for PR-driven plan/apply with manual approval on infra repos.

---

## 5. Change Management

| Change Type | Process | Approvers |
|-------------|---------|-----------|
| **Infrastructure (Terraform)** | PR with plan screenshot or Atlantis comment; requires one platform engineer approval. | Platform team (at least 1 reviewer). |
| **GitOps Manifests** | PR to GitOps repo; requires service owner + platform review for prod. | Service owner + platform (prod only). |
| **Backstage Templates** | PR to template repo; test scaffold locally. | DX/Platform duo. |
| **Observability/SLO tweaks** | Update dashboards/SLO docs; note change in Backstage entity. | Service owner; platform review for global dashboards. |

Release cadence: weekly for non-prod, twice monthly for prod. Emergency fixes go through accelerated review but must be post-reviewed.

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

This governance README will evolve as each capability graduates from planned to in-place. Use it as the source of truth for expectations around platform adoption and operations.***
