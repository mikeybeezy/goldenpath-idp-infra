---
id: CL-0050-infracost-activation
title: 'CL-0050: Activated Infracost Cost Visibility'
type: changelog
category: changelog
version: 1.0
owner: platform-team
status: active
dependencies:
  - CL-0049-ci-optimization
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2026-06-01
  breaking_change: false
relates_to:
  - ADR-0076
  - IDP_PRODUCT_FEATURES
---

# CL-0050: Activated Infracost Cost Visibility

**Date:** 2026-01-04
**Owner:** Platform Team
**Scope:** GitHub Actions, Terraform
**Related:** ADR-0076, CL-0030

## Summary

Activated the Infracost integration for the `Plan - PR Terraform Plan` workflow. This enables automated cost estimation for all Terraform changes, surfacing financial impact directly in Pull Requests via comments.

## Changes

### Activated
- **Infracost Integration**: Enabled by configuring the `INFRACOST_API_KEY` repository secret.
- **Robust Key Detection**: Updated [pr-terraform-plan.yml](file:///Users/mikesablaze/goldenpath-idp-infra/.github/workflows/pr-terraform-plan.yml) to verify keys from both `secrets` and `vars` contexts for improved reliability.
- **Manual Trigger**: Added `workflow_dispatch` event to the workflow to allow for ad-hoc validation and cost checks without commits.

### Documentation
- **Product Features**: Added "FinOps / Cost Visibility" to [IDP_PRODUCT_FEATURES.md](file:///Users/mikesablaze/goldenpath-idp-infra/docs/product/IDP_PRODUCT_FEATURES.md).
- **ADR Status**: Updated [ADR-0076](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0076-platform-infracost-ci-visibility.md) to "Implemented".

## Validation

### Automated Verification
- Manual execution of `Plan - PR Terraform Plan` (Run ID: 20699727360) confirmed successful authentication and cost breakdown generation.
- Logs show correct `infracost configure set api_key` execution.

## Impact

**FinOps Maturity**: Moved from "Blind" to "Cost Aware" provisioning. Engineers now receive immediate feedback on the financial consequences of their infrastructure code.
