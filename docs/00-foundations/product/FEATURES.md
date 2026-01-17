---
id: FEATURES
title: IDP Features
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
  - CAPABILITY_LEDGER
---
## Golden Path IDP Features

The Golden Path IDP provides a streamlined, self-service experience for developers to provision infrastructure, manage applications, and adhere to governance standards. This document provides a high-level overview of available features, while the [**Capability Ledger**](./CAPABILITY_LEDGER.md) provides a detailed technical breakdown of every platform ability.

---

## 🛡️ Platform Governance & Trust

*Ensuring the ecosystem stays "Born Governed" without slowing down engineering velocity.*

- **Metadata Sidecars**: Every resource carries its own identity, ownership, and risk profile.
- **Closed-Loop Governance**: Automated "Heal-Inject-Verify" loops that keep infrastructure in sync with policy.
- **Federated Quality Gates**: Shift-left validation that catches compliance issues before they reach production.
- **Config-Driven Governance**: Manage platform rules via a Schema-First YAML control plane.
- **Zero-Touch Auto-Healing**: Automatic metadata initialization for new assets to eliminate governance debt.
- **HITL Governance**: Human-In-The-Loop guidance that replaces friction with actionable remediation.
- **Policy-as-Code Guardrails**: Automated enforcement of security best-practices (encryption, rotation, retention) at the intent layer.
- **Heal-First Workflow**: Pass 15+ governance gates on the first pull request with a single remediation command that aligns files with platform standards automatically.
- **Script Certification**: Verifiable trust for automation scripts through cryptographic proofs and a rigorous "Born Governed" lifecycle.

## 🚀 Delivery & Self-Service

*Automating the path from local code to a production-ready, governed environment.*

- **Repository Scaffolding**: One-click creation of governed GitHub repositories with pre-configured CI/CD.
- **Service Scaffolding**: Strategic templates for Node.js, Python, and Go that bake in security and standards.
- **Resource Provisioning**: Governed workflows for AWS ECR, S3, RDS, and VPC components.
- **Unified Secret Request Flow**: A streamlined, single-contract interface for managing the entire secret lifecycle across AWS and Kubernetes.
- **GitOps Secret Projection**: Automated bridging of AWS Secrets Manager to Kubernetes namespaces via the External Secrets Operator.
- **CI/CD Guardrails**: Automated branch policies and PR gates to protect the main development branch.
- **Standalone Platform RDS**: Persistent multi-tenant PostgreSQL database as a bounded context, surviving cluster rebuilds with CI-enforced secret rotation and multi-layer deletion protection.

## Observability & Intelligence

*Providing visibility into the state, cost, and architecture of the entire platform.*

- **Platform Health Dashboard**: A real-time audit of governance coverage and infrastructure health.
- **Knowledge Graph**: A programmatic map of relationships between ADRs, docs, and code.
- **Relationship Graph Sync**: Automated relationship extraction keeps the knowledge graph current across ADRs, docs, and code.
- **Self-Healing Documentation**: Zero-drift documentation that updates itself based on source code changes.
- **System Map Inventory**: Auto-generated platform map (`PLATFORM_SYSTEM_MAP.md`) that lists doc domains, counts, and validators.
- **FinOps / Cost Visibility**: Pre-provisioning cost signals that make infrastructure spend visible in PRs.
- **OOTB Golden Signals**: Instant RED metrics (Rate, Errors, Duration) and correlated logs for every application, with zero configuration required.

## Foundations (Internal)

*The core engineering systems that power the Golden Path experience.*

- **Enum Consistency**: Unified vocabulary across all metadata and automation engines.
- **Schema-First Control Plane**: Decoupling governance logic from code using high-fidelity YAML schemas.
- **Validation Engines**: High-performance metadata and structural integrity checkers.
- **Injection Coverage**: Metrics-driven tracking of how well metadata propagates into live cluster resources.
