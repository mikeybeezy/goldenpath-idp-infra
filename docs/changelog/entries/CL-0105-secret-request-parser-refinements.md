---
id: CL-0105
title: 'CL-0105: Secret Request Parser refinements and security upgrades'
type: changelog
status: active
owner: platform-team
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0143
  - ADR-0139
supported_until: 2028-01-11
breaking_change: false
---

## CL-0105: Secret Request Parser refinements and security upgrades

Date: 2026-01-11
Owner: platform-team
Scope: Secret Manager Infrastructure, `secret_request_parser.py`
Related: PR #216, docs/adrs/ADR-0143-secret-request-contract.md, docs/adrs/ADR-0144-intent-to-projection-parser.md

## Summary

- Enhanced the `SecretRequest` contract and parser to support granular IAM security principals.
- Upgraded the `aws_secrets_manager` module with resource-level security policy generation.
- Realigned the `risk` variable contract across Secret and ECR modules.
- Formally documented the "Parser-Centric" architecture philosophy.

## Impact

- Developers can now declare mandatory access control for secrets at request time.
- Security posture is automatically enforced through shift-left governance gates in CI.
- Infrastructure and intent are 100% decoupled via the platform's parser intelligence.

## Changes

### Added

- `readPrincipals`, `writePrincipals`, and `breakGlassPrincipals` to the Secret Request contract.
- Resource-level IAM policy resource in the Secrets Manager module.
- High-integrity architectural documentation for the Secret Request Flow.

### Changed

- Reverted `risk_tier` to `risk` across all platform modules for external-contract consistency.
- Updated the dev environment `terraform.tfvars` with granular principal hooks.
- Refined secret deletion logic to allow immediate purge (recovery window = 0).

### Fixed

- Inconsistent variable naming between ECR and Secret modules.
- Parser validation to strictly enforce rotation for high-risk assets.

## Rollback / Recovery

- Revert PR #216.

## Validation

- Verified contract-to-projection parity using the simulated SEC-0007 manifest.
- Validated Terraform planning with the new security policy components.
