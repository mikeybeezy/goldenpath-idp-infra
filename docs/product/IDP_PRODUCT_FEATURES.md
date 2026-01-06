---
id: IDP_PRODUCT_FEATURES
title: 'GoldenPath IDP: Core Product Features'
type: product
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - 00_DESIGN_PHILOSOPHY
  - 34_PLATFORM_SUCCESS_CHECKLIST
  - 37_V1_SCOPE_AND_TIMELINE
  - READINESS_CHECKLIST
  - V1_04_CAPABILITY_MATRIX
---

# GoldenPath IDP: Core Product Features

The GoldenPath IDP transforms complex AWS/EKS infrastructure into a developer-centric product. Unlike raw infrastructure, the IDP focuses on **Discoverability, Self-Healing, and Lifecycle Management**.

## 1. Automated Platform Health Dashboard
Every resource in the GoldenPath (from documentation to Helm charts) is tracked via a standardized governance schema, surfacing in a persistent "Living Dashboard."
- **Persistent Visibility**: Automated generation of [**`PLATFORM_HEALTH.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md) that maps ownership, risk, and compliance across 300+ components.
- **Continuous Auditing**: The dashboard is automatically updated on every change and daily at midnight, providing a stateful record of platform maturity.
- **Injection Coverage**: Unique tracking of how well metadata is propagated into live cluster resources, identifying "Dark Infrastructure" gaps in real-time.
- **Immutable Audit Log**: Transitioned from a mutable "Live-View" only model to a high-integrity dual-state architecture, maintaining an append-only [**`HEALTH_AUDIT_LOG.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/governance/reports/HEALTH_AUDIT_LOG.md) for historical compliance and audit trails.
- **Knowledge Graph Integration**: Every component knows its dependencies, allowing for automated impact analysis and relationship mapping.

## 2. Infrastructure Metadata Sidecars (Sidecar-as-Standard)
The platform strictly forbids "Dark Infrastructure." Every component in the GitOps tree must carry an "Identity Card" via `metadata.yaml`.
- **Structural Enforcement**: Enforced at the PR level across all Helm charts, environments, tooling, and **Core Applications**.
- **Sidecar-as-Standard**: Every new resource is automatically provisioned with a standardized governance sidecar.

## 3. Closed-Loop Governance (Heal, Inject, Verify, Report)
The IDP features a fully automated governance engine that bridges the gap between static documentation and live cluster resources.
- **HEAL**: The **`standardize_metadata.py`** engine (The Healer) performs automated schema remediation and sidecar generation, ensuring 100% repository compliance.
- **INJECT**: The **Governance Injection Pass** automatically propagates metadata (Owner, ID, Risk) from sidecars into Helm `values.yaml` and ArgoCD manifest annotations.
- **VERIFY**: Quality Gates (**`validate_metadata.py`**) verify "Injection Integrity," ensuring that governance data is successfully baked into the deployment configuration.
- **REPORT**: The **`platform_health.py`** reporter audits the entire estate, surfacing **"Injection Coverage"** metrics and identifying any remaining "Dark Infrastructure" gaps.

## 4. Federated Quality Gates
Quality is enforced at the source, ensuring that no resource enters the platform without its "Identification Card."
- **Shift-Left Validation**: Pre-commit hooks and GitHub Actions ensure 100% metadata compliance, correct ADR formatting, and changelog presence.
- **Zero-Trust Metadata**: All IDs are validated against the repository's path-based naming convention, preventing ID shadowing.

## 5. "Born Governed" Service Scaffolding
The IDP ensures that every new service is compliant from Day 0 by embedding governance into the core scaffolding process.
- **Template-First Compliance**: All Backstage templates come pre-configured with `metadata.yaml` sidecars and automated annotation injection.
- **Zero-Manual-Setup**: Developers don't need to "add" governance later; services are born with ownership, risk, and reliability data already baked in.

## 6. Automated Knowledge Graph
The platform programmatically maps relationships between thousands of resources, transforming static docs into a dynamic graph.
- **Relationship Discovery**: The **`extract_relationships.py`** engine automatically identifies ADR dependencies, changelog links, and cross-component mentions.
- **Impact Analysis**: Programmatic tracking allows engineers to see exactly which components or environments are affected by a change before it is merged.

## 7. Single-Submission Repository Scaffolding
The IDP enables "Push-Button" repository creation, transforming a single form submission into a fully provisioned, governed GitHub repository.
- **Unified Onboarding**: Using the **`repo-scaffold-app.yml`** workflow or Backstage Software Templates, developers Fill out a single form to automate repo creation, branch protection, and team permissions.
- **Render-on-the-Fly**: The **`render_template.py`** engine dynamically injects governance IDs and service metadata into the scaffolded code before it is even pushed to GitHub.

## 8. Self-Service Cloud Resource Provisioning
The IDP transforms manual cloud resource requests into governed, one-click workflows—eliminating configuration errors and ensuring security compliance from Day Zero.
- **Atomic Catalog Sync**: Resource catalogs (YAML) and human-readable documentation (Markdown) update together in the same PR, preventing documentation drift.
- **Risk-Based Security Automation**: Security controls (encryption, mutability, retention, scanning) are auto-applied based on declared risk levels—compliance is enforced, not optional.
- **Domain-Agnostic Engine**: A single catalog generator supports multiple AWS resource types (ECR, S3, RDS), enabling rapid expansion to new services.
- **Day Zero Guidance**: Every provisioning PR includes direct links to operational runbooks, ensuring developers know exactly how to use newly created resources.

## 9. Workload-Centric Abstractions (Planned)
Future evolution focuses on the "Score" implementation to allow developers to define **WHAT** they need, hiding the complexity of **HOW** it is provisioned.
- **Zero-YAML Onboarding**: Moving away from complex K8s manifests toward workload-centric descriptors.

---

## Technical Foundation
- **Platform Core**: AWS EKS (Ubuntu/Bottlerocket)
- **GitOps Engine**: Argo CD
- **Governance**: Metadata-Schema V1.0
- **Observability**: Kube-Prometheus-Stack (Gold Tier)
