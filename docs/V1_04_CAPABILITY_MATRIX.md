# Capability Matrix – Golden Path IDP Infra

| Capability | Description | Modules / Components | Status | Notes |
| ------------ | ------------- | ---------------------- | -------- | ------- |
| **Networking Core** | Foundational VPC, IGW, and basic routing for every environment. | `modules/vpc`, `modules/aws_route_table` | ✅ In place | VPC + optional public route table created per env; route-table reuse supported. |
| **Subnet Topology** | Public/private subnets across AZs with consistent tagging. | `modules/aws_subnet` | ✅ In place | Driven entirely via `envs/<env>/terraform.tfvars`; supports multiple AZ entries. |
| **Security Boundaries** | Base security groups for web/ingress traffic. | `modules/aws_sg` | ✅ In place | Allows HTTPS ingress + full egress; additional rules can be layered per env. |
| **Compute (EC2)** | Optional EC2 instance template with managed ENI. | `modules/aws_compute`, `modules/aws_nic` | ⚙️ Disabled by default | Toggle via `compute_config.enabled` in each env’s tfvars. Handles ENI + root volume config. |
| **EKS Control Plane** | Managed Kubernetes cluster + node group. | `modules/aws_eks` | ⚙️ Staged (commented) | Module exists but env usage is commented out. Enable by uncommenting `eks_config` blocks. |
| **Environment Overlays** | Per-environment Terraform stacks controlling providers/backends. | `envs/dev`, `envs/test`, `envs/staging`, `envs/prod` | ✅ In place | Each env has `main.tf`, `variables.tf`, `terraform.tfvars`, `backend.tf`. |
| **Automation Wrapper** | Makefile wrappers for init/plan/apply per environment. | `Makefile` | ✅ In place | `make init ENV=dev` etc. simplifies Terraform invocation. |
| **Documentation & Onboarding** | Root README, module-level READMEs, capability overview. | `README.md`, `modules/*/README.md`, `CAPABILITY_MATRIX.md` | 🚧 In progress | VPC module doc complete; other modules pending the same format. |
| **Teardown determinism (LB/ENI cleanup)** | Bounded retry with cluster-scoped LB cleanup and ENI wait to unblock subnet deletes. | teardown scripts + runbooks | ✅ In place | Eventual consistency remains; break-glass defaults are scoped by cluster tag. |
| **Observability/SLO governance** | Ownership split: platform team owns CI/infra SLOs; app teams own service SLOs. | docs/V1_01_SCOPE_AND_TIMELINE.md | 🚧 In progress | Ownership model needs formal doc + review cadence. |
| **Change management / release workflow** | PR → plan → apply → bootstrap → add teardown; approvals and gates codified. | workflows + docs/21_CI_ENVIRONMENT_CONTRACT.md | 🚧 In progress | Flow documented; enforcement still evolving. |
| **Incident response expectations** | Clear lead, comms channel, postmortem cadence, and response steps. | runbooks | 🚧 In progress | Requires defined owner and SLA targets. |
| **Secret rotation cadence** | Rotation schedule + trigger ownership for AWS Secrets Manager/SSM. | AWS Secrets Manager / SSM (TBD) | 🚧 In progress | Define cadence and audit evidence. |
| **Compliance / audit logging** | Decisions and changes tracked with ADRs + changelog; retention expectations defined. | docs/adrs, docs/changelog | 🚧 In progress | Formalize retention + review cadence. |

## Legend

- ✅ In place – capability is implemented and active.
- ⚙️ Disabled / staged – capability exists but requires toggling or is not active by default.
- 🚧 In progress – documentation or automation partially complete.
