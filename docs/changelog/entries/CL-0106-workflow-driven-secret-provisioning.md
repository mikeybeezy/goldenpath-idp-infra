---
id: CL-0106-workflow-driven-secret-provisioning
title: metadata
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0144
  - CL-0106
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
---
# CL-0106: Workflow-Driven Secret Provisioning and Auto-Apply

## Summary
Introduced a fully automated, workflow-driven "Golden Path" for requesting and provisioning application secrets. Developers can now initiate secret requests via a guided GitHub Actions UI, receive immediate feedback through automated Pull Requests with real Terraform plans, and have the infrastructure automatically provisioned upon PR approval and merge.

## Details
- **Self-Service Workflow**: Added the `Request App Secret` manual dispatch workflow with enriched inputs (dropdowns for secret type, domain, owner, and rotation) to standardize secret creation.
- **Automated PR Engine**: The dispatch workflow automatically generates the necessary `SecretRequest` YAML, creates a feature branch, and opens a Pull Request.
- **High-Fidelity Feedback**: Implemented real, targeted Terraform plans in the PR descriptions and as comments, providing developers and reviewers with exact infrastructure delta.
- **GitOps Auto-Apply**: Enhanced the `Secret Requests (Apply)` workflow to automatically execute surgical `terraform apply` operations using `-target` and `-var-file` flags upon PR merge.
- **Artifact Generation**: Automated the generation of Terraform `.tfvars.json` and Kubernetes `ExternalSecret` manifests as part of the CI/CD pipeline.
- **Governance Standards**: Aligned workflow inputs with `enums.yaml` and established a robust documentation framework (ADR-0144, RB-0026).

## Related
- ADR-0144: Intent-to-Projection Parser Architecture
- RB-0026: Local Secret Generation & Targeting
- SECRET_REQUEST_FLOW.md
