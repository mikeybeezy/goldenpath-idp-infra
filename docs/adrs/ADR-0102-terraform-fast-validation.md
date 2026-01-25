<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0102
title: Layer 2 Terraform Validation (Fast Feedback Loop)
type: adr
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0034 (CI Environment Contract)
  - ADR-0034-platform-ci-environment-contract
  - ADR-0102
  - CL-0064 (Terraform Lint Workflow)
  - CL-0064-terraform-lint-workflow
  - SCRIPT_CERTIFICATION_AUDIT
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
version: 1.0
---

## ADR-0102: Layer 2 Terraform Validation (Fast Feedback Loop)

## Context

Currently, Terraform validation primarily occurs during the `env=dev` integration tests (`infra-terraform-apply-dev.yml`) or via `pr-terraform-plan.yml`. These workflows require AWS credentials, backend initialization (S3/DynamoDB), and significant runtime overhead (~2-5 minutes).

Developers who make syntax errors (e.g., invalid attribute references) or formatting mistakes often wait several minutes only to receive a failure that could have been caught instantly offline. There is no lightweight, "offline" gate that blocks invalid HCL code from entering the repository.

## Decision

We will implement a **Layer 2** validation workflow (`ci-terraform-lint.yml`) that serves as a fast, blocking gate for all Pull Requests involving Terraform code.

This workflow will:

1. **Run Offline**: Use `terraform init -backend=false` to skip S3 state initialization, removing the need for AWS credentials or network access.
2. **Validate Broadly**: Dynamically discover all `.tf` directories (modules and environments) and validate them in parallel or sequence, ensuring module-level syntax compliance.
3. **Enforce Formatting**: Run `terraform fmt -check`, failing immediately on style violations.

## Consequences

### Positive

- **Faster Feedback**: Syntax errors are caught in <30 seconds instead of minutes.
- **Reduced Cloud Ops**: Reduces unnecessary API calls to AWS and S3 state locking.
- **Security**: Basic validation runs without requiring OIDC role assumption.

### Negative

- **Duplicate Checks**: Some redundancy with `pr-terraform-plan.yml`, which also validates but as part of a larger, stateful plan operation.
- **Strictness**: Developers cannot merge unformatted code (intentional).

## Implementation

- Workflow: `.github/workflows/ci-terraform-lint.yml`
- Triggers: `pull_request` (on `.tf` changes)
