---
id: CAPABILITY_LEDGER
title: IDP Capability Ledger
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 1
relates_to:
  - ADR-0027
  - ADR-0092
  - PLATFORM_HEALTH.md
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# IDP Capability Ledger

The Golden Path IDP is built on the principle of **"Governance as a Service,"** where infrastructure management, security compliance, and developer experience are unified into a single, automated lifecycle.

## 1. Multi-State Platform Health Dashboard
The platform provides a real-time, high-integrity view of its own health and governance posture through the [**`PLATFORM_HEALTH.md`**](../../../PLATFORM_HEALTH.md) dashboard.
- **Continuous Auditing**: The dashboard is automatically updated on every change and daily at midnight, providing a stateful record of platform maturity.
- **Injection Coverage**: Unique tracking of how well metadata is propagated into live cluster resources, identifying "Dark Infrastructure" gaps in real-time.
- **Automated Audit Log**: Transitioned from a mutable "Live-View" only model to a high-integrity dual-state architecture, maintaining an append-only [**`HEALTH_AUDIT_LOG.md`**](../../10-governance/reports/HEALTH_AUDIT_LOG.md) for historical compliance and audit trails.
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
- **Enum Consistency Enforcement**: The **`validate_enums.py`** gate ensures that all metadata (Status, Risk, Type) adheres to the platform's unified [Queryable Intelligence enums](../../../schemas/metadata/enums.yaml), eliminating semantic drift.

## 7. "Born Governed" Service Scaffolding
The IDP ensures that every new service is compliant from Day 0 by embedding governance into the core scaffolding process.
- **Scaffolding Logic**: Automatically creates a new repository with a production-ready Node.js foundation for ECR services.
- **Governance-First Compliance**: Injects a `metadata.yaml` sidecar and `catalog-info.yaml` so the service is immediately compliant and visible in the [health dashboard](../../../PLATFORM_HEALTH.md).
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
- **Eventually Consistent Governance**: Decouples immediate scaffolding from catalog visibility to ensure 100% referential integrity. The "Mirror Model" eliminates "Ghost Resources" by reconciling the catalog against the physical cloud state on a 3-minute heartbeat (via ADR-0129).
- **Advisory Decommissioning**: Separates documentation cleanup from physical infrastructure teardown. Removing a resource from the governance logic results in an immediate "Soft Delete" from Backstage (re-rendering), while the sync script flags the physical resource as an "Orphan" in advisory mode rather than performing destructive auto-deletion.

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
- **Functional Type Resolution**: Automatically upgrades generic records to high-fidelity artifact types (ADR, Contract, Runbook), ensuring the [IDP Knowledge Graph](../../../PLATFORM_HEALTH.md) remains accurate and searchable.
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

- **Config-Driven Access Control**: Access lists for sensitive bypasses (hotfixes, build-ids) are externalized to a governed [**`access.yaml`**](../../../schemas/governance/access.yaml) configuration.
  - **Value**: Zero-friction onboarding for new team members.
  - **Cognitive Load Eliminated**: Removes the need to modify source code to update team membership, centralizing "who is allowed to do what" into a single, visible file.

- **Soft Enum Validation**: The validation engine now supports a `--soft` warning mode for non-production environments.
  - **Value**: Decouples governance vocabulary growth from infrastructure stability.
  - **Cognitive Load Eliminated**: Eliminates hard CI blocks for minor metadata typos or newly proposed tags, providing actionable guidance (via [RB-0015](docs/70-operations/runbooks/RB-0015-extending-governance-vocabulary.md)) instead of silent failures.

- **Human-In-The-Loop (HITL) Healing**: Replaced race-condition-prone "Auto-Push" bots with actionable local commands (`bin/governance heal`).
  - **Value**: Returns control to the developer and eliminates git merge conflicts caused by CI.
  - **Cognitive Load Eliminated**: Ends the "Git Push War" where CI and developers fight over the same branch, reducing frustration and manual rebase cycles.

- **Environment Parity CLI**: The [**`bin/governance`**](../../../bin/governance) suite provides 1:1 parity between a developer's laptop and the CI environment.
  - **Value**: "Born Green" development where issues are caught *before* they ever reach a PR.
  - **Cognitive Load Eliminated**: Eliminates the "Passes locally, fails in CI" syndrome, saving hours of debugging time by ensuring the local environment is always correctly configured with dependencies and hooks.

---

## 18. Contract-Driven Secret Provisioning (Request-to-Projection)
The platform transforms raw developer intent into governed cloud infrastructure and cluster-side secrets through a deterministic **Secret Request Parser**.
- **Contract-to-IaC Translation**: Performs high-fidelity translation of developer "intent" YAML into platform-grade Terraform configuration, decoupling implementation complexity from the user.
- **Shift-Left Governance Engine**: Enforces platform security policies (e.g., mandatory rotation for high-risk secrets) during the PR phase, blocking non-compliant requests before they reach AWS.
- **Dual-Target Projection**: Simultaneously generates cloud infrastructure (Terraform) and Kubernetes projection manifests (ESO), ensuring 1:1 parity between cloud resources and cluster access.
- **Automated IAM Least-Privilege**: Dynamically calculates and applies resource-level IAM policies for secrets based on declared `read`/`write` access principals in the contract.
- **Deterministic Namespace Isolation**: Enforces standardized naming and namespace mapping to prevent cross-tenant collisions and ensure strict environment separation.

---

## 19. Heal-First, Push-Once Workflow (Frictionless PR Gates)
The platform optimizes developer experience by replacing manual compliance chores with an automated **Heal-First, Push-Once** workflow.
- **The Healer (`bin/governance heal`)**: A remediation engine that automatically formats YAML/Markdown, injects missing metadata, and aligns files with platform standards to ensure 100% gate compatibility before push.
- **Minimal Conflict Enforcement**: Implements a 'Specific Owner Wins' policy to prevent environment-level automation from overwriting app-level identities, eliminating the CI oscillation that typically blocks multi-team PRs.
- **Marker-Based Stability**: Uses non-destructive comment markers to inject auto-generated tables (Indices, Workflows) into hand-managed documentation, maintaining both source truth and human readability.

---

## 20. Governance Registry Mirror (Audit Ledger)
The platform implements a **Governance Registry Mirror Pattern** to decouple machine-generated audit artifacts from human development branches, eliminating the "Commit Tug-of-War" while preserving high-integrity audit trails.
- **Dedicated Branch Architecture**: All platform health reports, documentation indices, and audit logs are written to the CI-owned `governance-registry` branch, preventing merge conflicts on active development branches.
- **Chain-of-Custody Enforcement**: Every artifact includes mandatory provenance metadata (`source.sha`, `pipeline.run_id`, `generated_at`) ensuring reproducibility and forensic traceability without requiring an external database.
- **Ledger Integrity Validation**: The `validate_govreg.py` enforcer runs on every registry commit, blocking manual patches and validating folder structure, preventing the branch from becoming polluted with untracked files.
- **Atomic State Mirroring**: Updates to the registry are atomic—updating both the "Latest View" and the "Historical Snapshot" in a single commit, with concurrency guards preventing race conditions during high-velocity merges.
- **Relates-To**: [ADR-0145](/docs/adrs/ADR-0145-governance-registry-mirror.md), [RB-0028](/docs/70-operations/runbooks/RB-0028-governance-registry-operations.md)

---

## 21. "Born Governed" Script Automation
The platform ensures that all automation code is treated as a first-class citizen with strict contracts, verifying safety and quality before execution.
- **Contract-Driven Execution**: Every script carries a self-describing contract (ID, Owner, Risk, Test Strategy) that determines how it is validated and run.
- **Legacy Backfill Injection**: The **Backfill Injector** automatically upgrades legacy scripts to the "Born Governed" standard, ensuring 100% repository compliance.
- **Cryptographic Trust**: Critical scripts are verified via cryptographic proofs (`proof-*.json`) minted by the **Verified Runner**, ensuring that "Trusted Code" has actually passed its tests in the current context.
- **Pre-Execution Safety**: The **Validator Gate** blocks any script execution if the contract is violated or if the proof is stale, preventing "works on my machine" unsafe operations.
- **Real-Time Visibility**: The **Certification Matrix** provides a live, auto-generated dashboard of script maturity (M3 Certified vs M1 Tracked).

---

## 22. Standalone Platform RDS (Persistent Data Layer)

The platform provides a **Bounded Context** data layer that decouples persistent database infrastructure from ephemeral compute, enabling true cluster ephemerality while maintaining data continuity.

- **Standalone Terraform Root**: RDS is deployed via its own Terraform state (`envs/{env}-rds/`), completely independent of EKS cluster state—enabling clusters to be destroyed and recreated without data loss.
- **Multi-Tenant Database Engine**: A single PostgreSQL instance hosts isolated databases for platform tooling (Keycloak, Backstage), reducing operational overhead and cost while maintaining logical separation.
- **VPC Discovery Pattern**: RDS discovers its target VPC via resource tags rather than direct Terraform references, enabling true state isolation between compute and data layers.
- **Multi-Layer Deletion Protection**: Intentionally difficult deletion through AWS `deletion_protection`, Terraform `prevent_destroy` lifecycle, and absence of any `rds-destroy` Makefile target—requiring manual console intervention for destruction.
- **CI-Enforced Secret Rotation**: Daily scheduled compliance checks (`secret-rotation-check.yml`) alert when credentials approach rotation deadlines, with soft PR gates warning on infrastructure changes without blocking velocity.
- **Region-Agnostic Configuration**: Zero hardcoded AWS regions—all regional configuration flows through variables, enabling multi-region deployment patterns.
- **Production-Grade Observability**: Auto-provisioned CloudWatch alarms for CPU, memory, storage, connections, and latency with configurable warning/critical thresholds.
- **Relates-To**: [ADR-0158](/docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md), [RB-0029](/docs/70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md), [RB-0030](/docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md)

---

## 23. Out-of-the-Box Observability (Golden Signals & RED)
The platform delivers "Zero-Config Observability," ensuring that every deployed service is immediately visible, measurable, and debuggable without manual dashboard creation.
- **Golden Signals Standard**: Every application automatically receives a standardized dashboard visualizing the **RED** method (Rate, Errors, Duration) and Saturation (CPU/Memory) signals.
- **Logs RED Integration**: Real-time application logs are correlated directly with metrics, allowing engineers to instantly jump from a "Spike in Errors" (Metric) to the "Stack Trace" (Log) in a single view.
- **Auto-Discovery Engine**: The Grafana sidecar automatically detects and imports dashboard ConfigMaps from any namespace, enabling a decentralized, self-service observability model where dashboards live alongside application code.

## Technical Foundation
- **Platform Core**: AWS EKS (Ubuntu/Bottlerocket)
- **GitOps Engine**: Argo CD
- **Governance**: Metadata-Schema V1.0
- **Observability**: Kube-Prometheus-Stack (Gold Tier)
- **Data Layer**: AWS RDS PostgreSQL (Bounded Context)

