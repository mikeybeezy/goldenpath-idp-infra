---
id: V1_04_CAPABILITY_MATRIX
title: Capability Matrix – Golden Path IDP Infra
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - IDP_PRODUCT_FEATURES
  - 00_DESIGN_PHILOSOPHY
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - 37_V1_SCOPE_AND_TIMELINE
  - READINESS_CHECKLIST
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Capability Matrix – Golden Path IDP Infra

Last updated: 2026-01-03

| Capability | Description | Modules / Components | Status | Notes |
| ------ | ------- | ------------- | ----- | ---- |
| **Networking Core** | Foundational VPC, IGW, and basic routing for every environment. | `modules/vpc`, `modules/aws_route_table` | ✅ In place | VPC + optional public route table created per env; route-table reuse supported. |
| **Subnet Topology** | Public/private subnets across AZs with consistent tagging. | `modules/aws_subnet` | ✅ In place | Driven entirely via `envs/<env>/terraform.tfvars`; supports multiple AZ entries. |
| **Security Boundaries** | Base security groups for web/ingress traffic. | `modules/aws_sg` | ✅ In place | Allows HTTPS ingress + full egress; additional rules can be layered per env. |
| **Compute (EC2)** | Optional EC2 instance template with managed ENI. | `modules/aws_compute`, `modules/aws_nic` |  Disabled by default | Toggle via `compute_config.enabled` in each env’s tfvars. Handles ENI + root volume config. |
| **EKS Control Plane** | Managed Kubernetes cluster + node group. | `modules/aws_eks` |  Staged (commented) | Module exists but env usage is commented out. Enable by uncommenting `eks_config` blocks. |
| **Environment Overlays** | Per-environment Terraform stacks controlling providers/backends. | `envs/dev`, `envs/test`, `envs/staging`, `envs/prod` | ✅ In place | Each env has `main.tf`, `variables.tf`, `terraform.tfvars`, `backend.tf`. |
| **Automation Wrapper** | Makefile wrappers for init/plan/apply per environment. | `Makefile` | ✅ In place | `make init ENV=dev` etc. simplifies Terraform invocation. |
| **Documentation & Onboarding** | Root README, module-level READMEs, capability overview. | `README.md`, `modules/*/README.md`, `CAPABILITY_MATRIX.md` |  In progress | VPC module doc complete; other modules pending the same format. |
| **Teardown determinism (LB/ENI cleanup)** | Bounded retry with cluster-scoped LB cleanup and ENI wait to unblock subnet deletes. | teardown scripts + runbooks | ✅ In place | Eventual consistency remains; break-glass defaults are scoped by cluster tag. |
| **Observability baseline (RED + Golden Signals)** | Metrics-first RED signals with derived Golden Signals dashboards and minimal alerts. | Prometheus/Grafana + docs/50-observability/05_OBSERVABILITY_DECISIONS.md |  In progress | Traces deferred to V1.1; labels and dashboards are the V1 focus. |
| **Observability/SLO governance** | Ownership split: platform team owns CI/infra SLOs; app teams own service SLOs. | docs/00-foundations/37_V1_SCOPE_AND_TIMELINE.md |  In progress | Ownership model needs formal doc + review cadence. |
| **Stateless app template** | Standard stateless workload deployable via app template. | `apps/fast-api-app-template` | ⚠️ Dev-only | Template exists; multi-env deploy not validated. Updated 2026-01-03. |
| **Stateful app template** | Standard stateful workload with PVC + storage contract. | (TBD) |  Missing | No stateful template defined yet. Updated 2026-01-03. |
| **App observability (OOTB)** | App dashboards + ServiceMonitor shipped by default template. | `apps/fast-api-app-template` + kube-prometheus-stack | ⚠️ Partial | Depends on env EKS + observability stack. Updated 2026-01-03. |
| **Platform observability (OOTB)** | Prometheus/Grafana/Loki/Fluent Bit baseline per env. | `gitops/argocd/apps/<env>` | ⚠️ Partial | Wired per env but not validated beyond dev. Updated 2026-01-03. |
| **Change management / release workflow** | PR → plan → apply → bootstrap → add teardown; approvals and gates codified. | workflows + docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md |  In progress | Flow documented; enforcement still evolving. |
| **Incident response expectations** | Clear lead, comms channel, postmortem cadence, and response steps. | runbooks |  In progress | Requires defined owner and SLA targets. |
| **Secret rotation cadence** | Rotation schedule + trigger ownership for AWS Secrets Manager/SSM. | AWS Secrets Manager / SSM (TBD) |  In progress | Define cadence and audit evidence. |
| **Compliance / audit logging** | Decisions and changes tracked with ADRs + changelog; retention expectations defined. | docs/adrs, docs/changelog |  In progress | Formalize retention + review cadence. |
| **Poly-repo CI/CD** | Connect pipelines from external app repos to the IDP. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Multi-env Flow** | Verified promotion: Dev → Staging → Prod. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Prov: Stateless Apps** | Deploy standard web/worker services via PR/Backstage. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Prov: Stateful Apps** | Deploy apps with Database/PVC via PR/Backstage. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Prov: S3 Buckets** | Self-service S3 via PR/Backstage. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Prov: RDS** | Self-service RDS via PR/Backstage. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Prov: EC2/EBS** | Self-service Compute/Storage via PR/Backstage. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Prov: ECR** | Self-service Container Registry via PR/Backstage. | modules/aws_ecr, .github/workflows/create-ecr-registry.yml | ✅ Verified | Automated PR flow via Backstage confirmed. |
| **Prov: EKS** | Self-service EKS cluster via `make deploy`. | modules/aws_eks, Makefile, bootstrap/ | ✅ Verified | Build 14-01-26-06: Infrastructure + Platform in 18m. |
| **Image Automation** | Build/Push/Track images via PR/Backstage. | docs/antig-implementations/ECR_PROVISIONING_FLOW.md | ✅ Verified | Documented flow with deterministic provisioning. |
| **Ingress (Kong)** | Kong Ingress Controller shipped OOTB. | bootstrap/kong | ⚠️ Partial | Installed, config needs hardening. |
| **Identity (Keycloak)** | OIDC User/Group management via Keycloak. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Security Scanning (L1)** | Basic container and config scanning pipeline. | (TBD) | ❌ Missing | New V1 Requirement. |
| **Observability (OOTB)** | Health, Performance, Control dashboards. | (TBD) | ❌ Missing | New V1 Requirement. |
| **AI Agent Compatibility** | Platform traversable by AI (context, graph, tools). | docs/ | ⚠️ Early | Documentation graph exists; tool interfaces missing. |

## Legend

- ✅ In place – capability is implemented and active.
-  Disabled / staged – capability exists but requires toggling or is not active by default.
-  In progress – documentation or automation partially complete.
