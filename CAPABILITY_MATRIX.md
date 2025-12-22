# Capability Matrix – Golden Path IDP Infra

| Capability | Description | Modules / Components | Status | Notes |
|------------|-------------|----------------------|--------|-------|
| **Networking Core** | Foundational VPC, IGW, and basic routing for every environment. | `modules/vpc`, `modules/aws_route_table` | ✅ In place | VPC + optional public route table created per env; route-table reuse supported. |
| **Subnet Topology** | Public/private subnets across AZs with consistent tagging. | `modules/aws_subnet` | ✅ In place | Driven entirely via `envs/<env>/terraform.tfvars`; supports multiple AZ entries. |
| **Security Boundaries** | Base security groups for web/ingress traffic. | `modules/aws_sg` | ✅ In place | Allows HTTPS ingress + full egress; additional rules can be layered per env. |
| **Compute (EC2)** | Optional EC2 instance template with managed ENI. | `modules/aws_compute`, `modules/aws_nic` | ⚙️ Disabled by default | Toggle via `compute_config.enabled` in each env’s tfvars. Handles ENI + root volume config. |
| **EKS Control Plane** | Managed Kubernetes cluster + node group. | `modules/aws_eks` | ⚙️ Staged (commented) | Module exists but env usage is commented out. Enable by uncommenting `eks_config` blocks. |
| **Environment Overlays** | Per-environment Terraform stacks controlling providers/backends. | `envs/dev`, `envs/test`, `envs/staging`, `envs/prod` | ✅ In place | Each env has `main.tf`, `variables.tf`, `terraform.tfvars`, `backend.tf`. |
| **Developer Experience (Backstage)** | Minimal Backstage portal for catalog, scaffolds, docs. | Backstage stack (planned) | ⚙️ Planned | V1: 1–2 service templates, doc links, gentle scorecards. |
| **Golden Path Templates** | Narrow set of service archetypes (stateless web/API) with contracts. | Template repos (planned) | ⚙️ Planned | Keeps onboarding boring + predictable; expands later. |
| **CI/CD Optionality** | GitHub Actions, GitLab CI, or Tekton feeding same contracts. | CI templates/pipelines (planned) | ⚙️ Planned | Leverages existing muscle memory while converging on GitOps outputs. |
| **GitOps Delivery** | Argo CD / Flux applying manifests to Kubernetes. | GitOps controller + repos (planned) | ⚙️ Planned | Single runtime, single delivery path per env. |
| **Ingress / API Gateway** | North-south entry via Kong or Gateway API + Traefik. | Ingress controller stack (planned) | ⚙️ Planned | Provides baseline routing; extensible per tenant. |
| **Service Mesh** | East-west security/observability via Istio/Linkerd (when needed). | Mesh stack (future) | 🚧 V2 | Defer until workloads justify mTLS/policy overhead. |
| **Identity & Security** | OIDC (Keycloak/Auth0/Ory), namespace RBAC, image scanning. | IdP, RBAC templates, scanning pipeline | ⚙️ Planned | Security is invisible to devs; enforcement centralised. |
| **Secrets Management** | HashiCorp Vault (primary) or AWS Secrets Manager (fallback) via External Secrets. | Vault / AWS Secrets Manager, External Secrets | ⚙️ Planned | Pick Vault for rich policy; use Secrets Manager when Vault unavailable. |
| **Policy Enforcement** | OPA/Kyverno guardrails for clusters + workloads. | Policy engine (future) | 🚧 V2 | Add after core identity/secrets land. |
| **Observability** | Prometheus, Loki/ELK, Tempo/Jaeger, basic SLO templates. | Observability stack (planned) | ⚙️ Planned | Metrics/logs/traces on by default; custom frameworks deferred. |
| **Automation & Quality Gates** | Makefile wrappers, fmt/validate/tflint/tfsec, Datree, Atlantis workflows. | `Makefile`, CI pipeline, Datree, Atlantis (planned) | ⚙️ In progress | Makefile + linting live; Datree catches K8s manifest issues upstream; Atlantis + remaining gates next. |
| **Documentation & Onboarding** | Root README, module-level docs, capability overview. | `README.md`, `modules/*/README.md`, `CAPABILITY_MATRIX.md` | 🚧 In progress | VPC module doc complete; remaining modules next. |

### Legend
- ✅ In place – capability is implemented and active.
- ⚙️ Disabled / staged – capability exists but requires toggling or is not active by default.
- 🚧 In progress – documentation or automation partially complete.


Synthasise  calibrate what we've done alraedy, your awarness of what the big picture vision is and use the below information to propose how the points captured can be embeded into the Cabibility Matrix for V1 with out duplicatiion or repition  point out what should stay in V1 and what can be moved into v2 or if eeverything listed deserves to be in V1 that is ok 

-------

Golden Path Architecture (High Level)
Developer Experience

Backstage Portal as the primary UX
Golden Path templates for service creation
Self-service onboarding with guardrails
CI Optionality (Convergent Optionality)

Teams may choose:

GitHub + GitHub Actions
GitLab + GitLab CI
Tekton (Kubernetes-native)
All paths converge on the same platform contracts.

Delivery & Runtime

GitOps via Argo CD / Flux
Kubernetes as the runtime substrate
Ingress / API Gateway for north-south traffic
Service Mesh for east-west traffic (where needed)
Security & Identity

Central identity via OIDC (Keycloak/Auth0/Ory)
Secrets managed via Vault / External Secrets
Policy enforcement via OPA/Kyverno
Observability

Metrics: Prometheus
Logs: Loki / ELK
Traces: Tempo / Jaeger
SLOs as first-class citizens


Ingress / API Gateway 
- Kong 
- Gateway api with bolt on's like traefik


# **V1 Scope (What’s IN)**

**1.**

**Golden Path (Very Narrow)**

- 1–2 service types max
    - Stateless web service
    - API service
- Opinionated structure
- Clear contracts

V1 golden path should feel boring — and relieving.

**2.**

**Single Runtime**

- Kubernetes (one cluster type)
- One deployment model
- One GitOps flow

No:

- multi-cluster routing
- multi-cloud abstraction
- custom per-team logic

**3.**

**CI/CD (Choice, Not Chaos)**

- Support existing muscle memory
    - GitHub Actions or
    - GitLab CI or
    - Tekton
- 
- Same outcome, different entry points

V1 respects familiarity.

**4.**

**Identity & Security (Invisible)**

- SSO via Keycloak/Auth0
- Namespace RBAC
- Secrets via External Secrets/Vault
- Image scanning (baseline)

Security exists, but never asks devs to think about it.

**5.**

**Observability (Default, Not Custom)**

- Pre-wired dashboards
- Open telementry
- Logs, metrics, traces ON by default
- Basic SLO templates

No custom observability frameworks yet.

**6.**

**Backstage (Minimal)**

- Service catalog
- Scaffolding
- Docs
- Scorecards (optional, gentle)

Backstage is a doorway, not a control center in V1.


**Golden Path (Very Narrow)**

- 1–2 service types max
    - Stateless web service
    - API service
- Opinionated structure
- Clear contracts

V1 golden path should feel boring — and relieving.

**2.**

**Single Runtime**

- Kubernetes (one cluster type)
- One deployment model
- One GitOps flow

No:

- multi-cluster routing
- multi-cloud abstraction
- custom per-team logic

**3.**

**CI/CD (Choice, Not Chaos)**

- Support existing muscle memory
    - GitHub Actions or
    - GitLab CI or
    - Tekton
- 
- Same outcome, different entry points

V1 respects familiarity.

**4.**

**Identity & Security (Invisible)**

- SSO via Keycloak/Auth0
- Namespace RBAC
- Secrets via External Secrets/Vault
- Image scanning (baseline)

Security exists, but never asks devs to think about it.

**5.**

**Observability (Default, Not Custom)**

- Pre-wired dashboards
- Open telementry
- Logs, metrics, traces ON by default
- Basic SLO templates

No custom observability frameworks yet.

**6.**

**Backstage (Minimal)**

- Service catalog
- Scaffolding
- Docs
- Scorecards (optional, gentle)

Backstage is a doorway, not a control center in V1.

Recommended MVP Tool Stack (Optimised)

Core
•	Terraform
•	Terragrunt (env + state only)
•	GitHub Actions (validation)
•	AWS (single provider)

Workflow
•	Atlantis (PR-driven plan/apply)
•	Manual approval via PR review

Quality Gates
•	terraform fmt / validate
•	tflint
•	tfsec / checkov
•	1–2 Terratest examples (optional but powerful)

Ci pipeline for infra and testing
