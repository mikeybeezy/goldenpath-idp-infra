---
id: ADR-0102
title: Layer 2 Terraform Validation (Fast Feedback Loop)
status: accepted
type: decision
category: architecture
version: 1.0
owner: platform-team
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-04
  breaking_change: false
relates_to:
  - ADR-0034
  - CL-0064
date: 2026-01-06
---

# ADR-0102: Layer 2 Terraform Validation (Fast Feedback Loop)

## Context
Currently, Terraform validation primarily occurs during the `env=dev` integration tests (`infra-terraform-apply-dev.yml`) or via `pr-terraform-plan.yml`. These workflows require AWS credentials, backend initialization (S3/DynamoDB), and significant runtime overhead (~2-5 minutes). 

Developers who make syntax errors (e.g., invalid attribute references) or formatting mistakes often wait several minutes only to receive a failure that could have been caught instantly offline. There is no lightweight, "offline" gate that blocks invalid HCL code from entering the repository.

## Decision
We will implement a **Layer 2** validation workflow (`ci-terraform-lint.yml`) that serves as a fast, blocking gate for all Pull Requests involving Terraform code.

This workflow will:
1.  **Run Offline**: Use `terraform init -backend=false` to skip S3 state initialization, removing the need for AWS credentials or network access.
2.  **Validate Broadly**: Dynamically discover all `.tf` directories (modules and environments) and validate them in parallel or sequence, ensuring module-level syntax compliance.
3.  **Enforce Formatting**: Run `terraform fmt -check`, failing immediately on style violations.

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
