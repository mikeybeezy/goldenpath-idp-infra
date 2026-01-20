---
id: CL-0111
title: Secret Request Pipeline Stabilization
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - docs/20-contracts/secret-requests
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0129
  - ADR-0169
  - CL-0111
supersedes: []
superseded_by: []
tags:
  - fix
  - ci
  - secrets
  - terraform
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 1.5
supported_until: '2028-01-01'
---
## CL-0111: Secret Request Pipeline Stabilization

## Summary

Resolved pathing and lifecycle issues in the automated Secret Request CI/CD pipeline, ensuring that Terraform plans are correctly surfaced in PR comments.

## Details

- **Path Mismatch Fix**: Corrected the output redirection of `terraform show` in the PR workflow. Previously, the plan was emitted to the repository root but searched for in `envs/dev/`, causing the PR comment step to fail.
- **Enabled Secret Workflows**: Restored and enabled `secret-request-pr.yml` and `secret-request-apply.yml` to support automated provisioning of requested secrets.
- **Artifact Security**: Added a `retention-days: 1` policy to generated secret previews to minimize the exposure window of sensitive (though non-secret) configuration artifacts in GitHub Actions.
- **Workflow Integrity Check**: Verified that the Terraform backend configuration (`bucket`, `dynamodb_table`) in the CI pipelines remains consistent with the physical `envs/dev` infrastructure.

## Impact

Enables the "Self-Service" secret provisioning flow, allowing developers to request secrets via YAML and see the infrastructure impact directly in their PR before merge.
