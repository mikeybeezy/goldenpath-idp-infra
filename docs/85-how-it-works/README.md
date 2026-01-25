---
id: HOW_IT_WORKS_INDEX
title: How It Works Index
type: documentation
relates_to:
  - CL-0127
---

This directory contains high-level, technical explanations of the platform's core mechanics. It focuses on the "Intent-based" model of the Golden Path, explaining the relationship between developer manifests and final infrastructure.

## Directory Structure

```text
85-how-it-works/
├── ci-terraform/          # CI/CD and Terraform workflows
├── governance/            # Platform governance mechanics
├── secrets-flow/          # Secret management flows
└── self-service/          # Self-service provisioning
```

## CI/CD & Terraform

- [CI Terraform Workflows](ci-terraform/CI_TERRAFORM_WORKFLOWS.md): GitHub Actions workflow architecture for plan/apply operations
- [Application Build Pipeline](ci-terraform/APP_BUILD_PIPELINE.md): End-to-end app build, promotion, and GitOps sync flow
- [Seamless Build Bootstrap Deployment](ci-terraform/SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT.md): Ephemeral cluster deployment mechanics

## Governance

- [PR Guardrails](governance/PR_GUARDRAILS.md): How the platform enforces quality and governance on code changes
- [Documentation Auto-Healing](governance/DOC_AUTO_HEALING.md): Keeping indices and dashboards synchronized with repository reality
- [Governance Registry Mirror](governance/GOVERNANCE_REGISTRY_MIRROR.md): Decoupled observation of platform health
- [Born Governed Lifecycle](governance/BORN_GOVERNED_LIFECYCLE.md): Schema-validated automation from creation

## Self-Service

### Golden Path Templates

- [Golden Path Overview](self-service/GOLDEN_PATH_OVERVIEW.md): Comprehensive comparison of the three Golden Paths and their state preservation characteristics
- [Stateless App Request Flow](self-service/STATELESS_APP_REQUEST_FLOW.md): Standard web services and APIs (Deployment)
- [Stateful App Request Flow](self-service/STATEFUL_APP_REQUEST_FLOW.md): Caches, queues, and local storage (StatefulSet + PVC)
- [Backend App + RDS Request Flow](self-service/BACKEND_APP_RDS_REQUEST_FLOW.md): Applications with managed database (Deployment + RDS)

### Infrastructure Provisioning

- [ECR Request Flow](self-service/ECR_REQUEST_FLOW.md): The self-service lifecycle of container registry provisioning
- [RDS Request Flow](self-service/RDS_REQUEST_FLOW.md): How RDS database requests flow from Backstage to Terraform
- [RDS Dual-Mode Automation](self-service/RDS_DUAL_MODE_AUTOMATION.md): Coupled vs standalone RDS automation mechanics
- [RDS User and DB Provisioning](self-service/RDS_USER_DB_PROVISIONING.md): Automated RDS role and database creation

## Secrets

- [Secret Request Flow](secrets-flow/SECRET_REQUEST_FLOW.md): How application secrets are governed and projected from Git to Kubernetes

## Platform Capabilities

- **Deterministic Scripting**: All platform automation is "Born Governed" with schema-validated headers
- **Continuous Traceability**: Machine-enforced linking between code, decisions, and history
- **Automated Remediation**: Self-healing documentation and configuration through governance "healers"
- **Registry Mirroring**: Decoupled observation of platform health to prevent commit contention
