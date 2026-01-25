<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0167-outcome-driven-ci
title: 'CL-0167: Outcome-driven CI - workflows call Make targets'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - .github/workflows/infra-terraform-apply-dev.yml
  - Makefile
  - bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ROADMAP-102
  - ADR-0180-argocd-orchestrator-contract
  - CL-0166-ci-iam-comprehensive-permissions
supersedes: []
superseded_by: []
tags:
  - ci
  - make
  - outcome-driven
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: 🔵 MV/HQ
  impact_tier: medium
  potential_savings_hours: 2.0
version: '1.0'
breaking_change: false
---

# CL-0167: Outcome-driven CI - workflows call Make targets

Date: 2026-01-23
Owner: platform-team
Scope: CI/CD, Makefile
Related: ROADMAP-102, ADR-0180

## Summary

- Refactored `infra-terraform-apply-dev.yml` to call Make targets instead of inline terraform commands
- Added `bootstrap_version` input to workflow (default: v4)
- Implements "CLI first, CI mirrors" principle: CI says WHAT, Make says HOW

## Impact

- **Platform team**: Local `make deploy-persistent` now produces same result as CI
- **Debugging**: Can reproduce CI behavior locally
- **CI portability**: Easier to switch CI providers (implementation is in Makefile)

## Changes

### Added

- `bootstrap_version` workflow input (v3 or v4, default v4)
- Outcome-driven deployment step that calls Make targets
- Header comments explaining the pattern (ROADMAP-102)

### Changed

- Replaced inline terraform apply + RDS provisioning + bootstrap with single Make call
- Persistent: `make deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4 CREATE_RDS=true`
- Ephemeral: `make deploy ENV=dev BUILD_ID=X BOOTSTRAP_VERSION=v4`
- CI now only handles:
  - Validation (plan succeeded check)
  - AWS credentials (OIDC)
  - Terraform init (backend config from secrets)
  - Governance registry recording

### Documented

- Added ROADMAP-102 reference to workflow header
- Pattern explanation: "CI says WHAT (inputs/outcomes), Make says HOW (terraform/kubectl)"

### Fixed

- Bootstrap v4 now handles fresh deployments with two-pass terraform apply
  - Pass 1: Creates EKS cluster (K8s resources disabled)
  - Pass 2: Creates K8s resources (ArgoCD, addons)
  - Resolves Kubernetes provider chicken-and-egg problem where provider tries to connect before cluster exists

### Known limitations

- Ephemeral path may need adjustment for EKS access setup (currently handled by `deploy` target)
- v3 bootstrap for ephemeral still uses shell orchestration pattern
- Two-pass apply adds ~30s to fresh deployments (one-time cost)

## Rollback / Recovery

- Git revert to previous workflow version
- No infrastructure impact (same terraform operations, different orchestration)

## Validation

- `make -n deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4` - dry-run shows expected flow
- Compare workflow steps before/after
- Full validation requires CI run with `lifecycle=persistent`

## Before/After Comparison

**Before (inline implementation):**
```yaml
- name: Terraform apply
  run: terraform -chdir=envs/dev apply -var "cluster_lifecycle=..."
- name: Provision RDS
  run: python3 scripts/rds_provision.py ...
- name: Setup EKS access
  run: aws eks create-access-entry ...
- name: Run bootstrap
  run: make bootstrap ...
```

**After (outcome-driven):**
```yaml
- name: Deploy (Make target)
  run: make deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4 CREATE_RDS=true
```

## Pattern Reference

> "CLI first, CI mirrors. CI says WHAT (inputs/outcomes), Make says HOW (terraform/kubectl). Enables local reproducibility and CI portability."
> — ROADMAP-102
