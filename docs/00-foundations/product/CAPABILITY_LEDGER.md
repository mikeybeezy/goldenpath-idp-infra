---
id: CAPABILITY_LEDGER
title: IDP Capability Ledger
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
schema_version: 1
relates_to:
  - ADR-0027
  - ADR-0092
  - PLATFORM_HEALTH.md
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
supported_until: 2028-01-01
breaking_change: false
---

# IDP Capability Ledger

The Golden Path IDP is built on the principle of **"Governance as a Service,"** where infrastructure management, security compliance, and developer experience are unified into a single, automated lifecycle.

## 1. Multi-State Platform Health Dashboard
The platform provides a real-time, high-integrity view of its own health and governance posture through the [**`PLATFORM_HEALTH.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md) dashboard.
- **Continuous Auditing**: The dashboard is automatically updated on every change and daily at midnight, providing a stateful record of platform maturity.
- **Injection Coverage**: Unique tracking of how well metadata is propagated into live cluster resources, identifying "Dark Infrastructure" gaps in real-time.
- **Automated Audit Log**: Transitioned from a mutable "Live-View" only model to a high-integrity dual-state architecture, maintaining an append-only [**`HEALTH_AUDIT_LOG.md`**](file:///Users/mikesablaze/goldenpath-idp-infra/docs/10-governance/reports/HEALTH_AUDIT_LOG.md) for historical compliance and audit trails.
- **Knowledge Graph Integration**: Every component knows its dependencies, allowing for automated impact analysis and relationship mapping.

## 2. Infrastructure Metadata Sidecars (Sidecar-as-Standard)
The platform strictly forbids "Dark Infrastructure." Every component in the GitOps tree must carry an "Identity Card" via `metadata.yaml`.
- **Structural Enforcement**: Enforced at the PR level across all Helm charts, environments, tooling, and **Core Applications**.
- **Sidecar-as-Standard**: Every new resource is automatically provisioned with a standardized governance sidecar.

## 3. Closed-Loop Governance (Heal, Inject, Verify, Report)
The IDP features a fully automated, **Schema-First** governance engine that bridges the gap between static documentation and live cluster resources.
- **HEAL**: The **`standardize_metadata.py`** engine (The Healer) performs automated schema remediation and sidecar generation, dynamically driven by the repository's metadata schemas.
- **INJECT**: The **Governance Injection Pass** automatically propagates metadata (Owner, ID, Risk) from sidecars into Helm `values.yaml` and ArgoCD manifest annotations.
- **VERIFY**: Quality Gates (**`validate_metadata.py`**) verify "Injection Integrity," ensuring that governance data is successfully baked into the deployment configuration as defined by the canonical schemas.
- **REPORT**: The **`platform_health.py`** reporter audits the entire estate, surfacing **"Injection Coverage"** metrics and identifying any remaining "Dark Infrastructure" gaps.

## 4. Federated Quality Gates
Quality is enforced at the source, ensuring that no resource enters the platform without its "Identification Card."
- **Shift-Left Validation**: Pre-commit hooks and GitHub Actions ensure 100% metadata compliance, correct ADR formatting, and changelog presence.
- **Zero-Trust Metadata**: All IDs are validated against the repository's path-based naming convention, preventing ID shadowing.

## 5. Automated CI/CD Guardrails
The platform protects the production environment by enforcing strict gates on every change.
- **Policy as Code**: ADRs are automatically validated for schema compliance and status consistency.
- **Plan Enforcement**: Terraform plans must be attached and validated before any infrastructure change is allowed.

## 6. Automated Validation & Quality Gates
The platform enforces its own rules through self-testing mechanisms, preventing technical debt from accumulating.
- **Script Governance**: The **`generate_script_index.py --validate`** gate ensures no automation script enters the repo without proper documentation headers.
- **Workflow Auditing**: CI pipelines are automatically indexed, and any "orphaned" or undocumented workflows are flagged.
- **Terraform Linting**: A "Layer 2" offline validation gate blocks malformed Infrastructure-as-Code before it ever reaches the cloud.
- **Enum Consistency Enforcement**: The **`validate_enums.py`** gate ensures that all metadata (Status, Risk, Type) adheres to the platform's unified [Queryable Intelligence enums](file:///Users/mikesablaze/goldenpath-idp-infra/schemas/metadata/enums.yaml), eliminating semantic drift.

## 7. "Born Governed" Service Scaffolding
The IDP ensures that every new service is compliant from Day 0 by embedding governance into the core scaffolding process.
- **Scaffolding Logic**: Automatically creates a new repository with a production-ready Node.js foundation for ECR services.
- **Governance-First Compliance**: Injects a `metadata.yaml` sidecar and `catalog-info.yaml` so the service is immediately compliant and visible in the [health dashboard](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md).
- **One-Click Deployment**: Seamlessly integrates with GitHub and the Backstage Software Scaffolder for zero-manual-setup on-boarding.
- **Zero-Manual-Setup**: Developers don't need to "add" governance later; services are born with ownership, risk, and reliability data already baked in.

## 8. Automated Knowledge Graph
The platform programmatically maps relationships between thousands of resources, transforming static docs into a dynamic graph.
- **Relationship Discovery**: The **`extract_relationships.py`** engine automatically identifies ADR dependencies, changelog links, and cross-component mentions.
- **Impact Analysis**: Programmatic tracking allows engineers to see exactly which components or environments are engagement affected by a change before it is merged.

## 9. Self-Healing Documentation
The IDP's documentation is no longer a static artifact; it is a live representation of the platform's state, driven directly by the code.
- **Automated Indexes**: Workflows (`CI_WORKFLOWS.md`) and Scripts (`scripts/index.md`) are auto-generated from source code, ensuring zero documentation drift.
- **Source-Driven Truth**: Documentation accurately reflects the current state of governance, infrastructure, and delivery pipelines without manual intervention.
- **Categorized & Visualized**: Automated tools parse, categorize, and even visualize complex systems (like ASCII workflow trees), making the platform easier to navigate and understand.

## 10. Single-Submission Repository Scaffolding
The IDP enables "Push-Button" repository creation, transforming a single form submission into a fully provisioned, governed GitHub repository.
- **Unified Onboarding**: Using the **`repo-scaffold-app.yml`** workflow or Backstage Software Templates, developers Fill out a single form to automate repo creation, branch protection, and team permissions.
- **Render-on-the-Fly**: The **`render_template.py`** engine dynamically injects governance IDs and service metadata into the scaffolded code before it is even pushed to GitHub.

## 11. Self-Service Cloud Resource Provisioning
The IDP transforms manual cloud resource requests into governed, one-click workflows—eliminating configuration errors and ensuring security compliance from Day Zero.
- **Atomic Catalog Sync**: Resource catalogs (YAML) and human-readable documentation (Markdown) update together in the same PR, preventing documentation drift.
- **Risk-Based Security Automation**: Security controls (encryption, mutability, retention, scanning) are auto-applied based on declared risk levels—compliance is enforced, not optional.
- **Domain-Agnostic Engine**: A single catalog generator supports multiple AWS resource types (ECR, S3, RDS), enabling rapid expansion to new services.
- **Day Zero Guidance**: Every provisioning PR includes direct links to operational runbooks, ensuring developers know exactly how to use newly created resources.

## 12. FinOps / Cost Visibility
The platform empowers engineers to be financially responsible by making cost impact visible *before* resources are provisioned.
- **Infracost Integration**: Automated cost estimation runs on every Terraform PR, surfacing the exact weekly/monthly cost impact of infrastructure changes.
- **Non-blocking Signals**: Developers get immediate feedback via PR comments, enabling "Cost Aware" decision making without slowing down velocity.

## 13. Config-Driven Metadata Governance
The platform has decoupled its governance logic from source code, moving the "Rules of the Platform" into human-readable YAML schemas.
- **Schema-First Control Plane**: Architects can add new metadata requirements or change valid enum values (e.g., adding a new team) by editing a single YAML file in `schemas/metadata/`, without touching any Python code.
- **Dynamic Standardization**: The remediation engine dynamically adapts its document "Skeletons" based on the latest schemas, ensuring that auto-healing is always perfectly aligned with current policy.
- **Zero-Code Evolution**: This allows the platform's governance model to evolve at high velocity, enabling O(1) schema updates across thousands of repository resources.

## 14. Contextual Metadata Auto-Healing
The IDP features an "Architecturally Aware" remediation engine that maintains repository integrity without developer intervention.
- **Contextual Inferencing**: The **`standardize_metadata.py`** engine intelligently maps legacy placeholders (like `unknown`) to precise architectural pillars (Delivery, Security, Observability) based on a file's location in the platform tree.
- **Functional Type Resolution**: Automatically upgrades generic records to high-fidelity artifact types (ADR, Contract, Runbook), ensuring the [IDP Knowledge Graph](file:///Users/mikesablaze/goldenpath-idp-infra/PLATFORM_HEALTH.md) remains accurate and searchable.
- **Automated Compliance**: Corrects 100% of enum violations and metadata gaps in a single, automated pass, eliminating governance debt at its source.

## 16. Zero-Touch Auto-Healing
The IDP ensures total governance coverage by automatically initializing metadata for any new platform asset without developer intervention.
- **Automated Discovery**: Any new directory created in a governed zone is automatically detected by the CI gate.
- **Contextual Inheritance**: The engine walks up the platform tree to inherit ownership, domain, and risk profiles from parent directories.
- **Zero-Manual-Setup**: Automatically generates and initializes a high-fidelity `metadata.yaml` sidecar and commits it back to the PR branch, ensuring the asset is "Born Governed."

## 15. Workload-Centric Abstractions (Planned)
Future evolution focuses on the "Score" implementation to allow developers to define **WHAT** they need, hiding the complexity of **HOW** it is provisioned.
- **Zero-YAML Onboarding**: Moving away from complex K8s manifests toward workload-centric descriptors.

## 17. Human-In-The-Loop (HITL) Governance & De-Friction
The platform prioritizes developer velocity by replacing "Automatic Policing" with "Guided Remediation," ensuring that governance is a path of least resistance rather than a blocker.

- **Config-Driven Access Control**: Access lists for sensitive bypasses (hotfixes, build-ids) are externalized to a governed [**`access.yaml`**](file:///Users/mikesablaze/goldenpath-idp-infra/schemas/governance/access.yaml) configuration.
  - **Value**: Zero-friction onboarding for new team members.
  - **Cognitive Load Eliminated**: Removes the need to modify source code to update team membership, centralizing "who is allowed to do what" into a single, visible file.

- **Soft Enum Validation**: The validation engine now supports a `--soft` warning mode for non-production environments.
  - **Value**: Decouples governance vocabulary growth from infrastructure stability.
  - **Cognitive Load Eliminated**: Eliminates hard CI blocks for minor metadata typos or newly proposed tags, providing actionable guidance (via [RB-0015](file:///Users/mikesablaze/goldenpath-idp-infra/docs/70-operations/runbooks/RB-0015-extending-governance-vocabulary.md)) instead of silent failures.

- **Human-In-The-Loop (HITL) Healing**: Replaced race-condition-prone "Auto-Push" bots with actionable local commands (`bin/governance heal`).
  - **Value**: Returns control to the developer and eliminates git merge conflicts caused by CI.
  - **Cognitive Load Eliminated**: Ends the "Git Push War" where CI and developers fight over the same branch, reducing frustration and manual rebase cycles.

- **Environment Parity CLI**: The [**`bin/governance`**](file:///Users/mikesablaze/goldenpath-idp-infra/bin/governance) suite provides 1:1 parity between a developer's laptop and the CI environment.
  - **Value**: "Born Green" development where issues are caught *before* they ever reach a PR.
  - **Cognitive Load Eliminated**: Eliminates the "Passes locally, fails in CI" syndrome, saving hours of debugging time by ensuring the local environment is always correctly configured with dependencies and hooks.

---

## Technical Foundation
- **Platform Core**: AWS EKS (Ubuntu/Bottlerocket)
- **GitOps Engine**: Argo CD
- **Governance**: Metadata-Schema V1.0
- **Observability**: Kube-Prometheus-Stack (Gold Tier)
