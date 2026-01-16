---
id: ADR-0100-standardized-ecr-lifecycle-and-documentation
title: Standardized ECR Lifecycle and Documentation
type: adr
status: accepted
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0092
  - ADR-0093
  - ADR-0097
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# ADR-0100: Standardized ECR Lifecycle and Documentation

## Context
The previous ECR registry creation process required manual input for multiple redundant fields (name and ID) and suffered from a "drift gap" where the human-readable [REGISTRY_CATALOG.md](../REGISTRY_CATALOG.md) was not automatically updated when new registries were added to the YAML source. Additionally, security settings were hardcoded in Python, violating the "Single Source of Truth" principle.

## Decision
We have implemented a standardized lifecycle for ECR registries that automates ID generation, ensures documentation synchronization, and centralizes security policy definitions.

### Key Decisions
1.  **Automated Identity**: Remove manual `id` input in the [create-ecr-registry.yml](../../.github/workflows/create-ecr-registry.yml) workflow. The ID is now auto-calculated from the registry name (e.g., `app-foo` -> `REGISTRY_APP_FOO`).
2.  **Continuous Documentation Sync**: The registry creation workflow now triggers the documentation generator script as a mandatory step, ensuring Markdown and YAML catalogs never drift.
3.  **Externalized Security Policies**: Move risk-based security settings (encryption, retention, scanning) out of hardcoded Python logic and into a shared [ecr-risk-settings.yaml](../10-governance/policies/ecr-risk-settings.yaml). This file serves as the source of truth for both documentation and Terraform enforcement.
4.  **Domain-Agnostic Engine**: Refactor `generate_catalog_docs.py` to be domain-agnostic, supporting multiple resource types (S3, RDS, etc.) as per the domain-based resource catalog strategy (ADR-0097).
5.  **HCL Integrity Guard**: Implement an automated `terraform fmt` check in the workflow to validate `terraform.tfvars` after every automated modification.
6.  **Standardized Build Tooling**: Provide a platform-standard [ecr-build-push.sh](../../scripts/ecr-build-push.sh) script to enforce consistent tagging (Git SHA + Version) for all application teams.

### 7. Atomic Documentation Sync
To prevent documentation from becoming a "second-class citizen," the GitHub Workflow treats the documentation update as an atomic part of the resource proposal. The `REGISTRY_CATALOG.md` is updated programmatically by the CI runner before the PR is even created.

### 8. Metadata Inheritance & Governance
Generated documentation files (like `REGISTRY_CATALOG.md`) must not be "governance blind." The generator script is mandated to inject standard platform frontmatter (metadata) into the Markdown files it creates. This ensures they are tracked by the repository's health metrics and schema validation tools.

## Consequences
- **Positive**: Reduced user friction during registry requests.
- **Positive**: Guarantees that documentation is always a true reflection of the infrastructure state.
- **Positive**: Simplifies governance by centralizing security settings in a single YAML file.
- **Positive**: Generated documentation is now fully compliant with the platform's metadata governance scheme.
- **Negative**: Increased complexity in the documentation script to support multiple domains and metadata injection.
- **Negative**: Adds a dependency on `terraform` CLI in the registry creation workflow.
