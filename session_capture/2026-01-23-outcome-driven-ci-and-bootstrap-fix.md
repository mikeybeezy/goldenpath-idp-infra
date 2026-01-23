---
id: 2026-01-23-outcome-driven-ci-and-bootstrap-fix
title: Outcome-Driven CI and Bootstrap v4 Two-Pass Fix
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - CL-0167-outcome-driven-ci
  - ROADMAP-102
  - ADR-0180-argocd-orchestrator-contract
---

# Outcome-Driven CI and Bootstrap v4 Two-Pass Fix

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-23
**Timestamp:** 2026-01-23T13:00:00Z
**Branch:** development

## Scope

- Implement outcome-driven CI pattern (ROADMAP-102)
- Fix Kubernetes provider chicken-and-egg problem for fresh deployments
- Clean up stale Terraform state from deleted EKS cluster

## Work Summary

- Refactored `infra-terraform-apply-dev.yml` to call Make targets instead of inline terraform commands
- Added `bootstrap_version` workflow input (v3/v4, default v4)
- Implemented two-pass terraform apply in bootstrap v4 script for fresh deployments
- Cleaned up stale Terraform state (EKS cluster was deleted but state remained)
- Created changelog CL-0167

## Issues Diagnosed and Fixed

| Issue | Root Cause | Fix |
|-------|------------|-----|
| `Error: Get "http://localhost/api/v1/namespaces/external-secrets"` | Kubernetes provider tried to connect before EKS cluster exists. State had stale cluster reference; actual cluster deleted. | 1. Removed stale k8s/EKS resources from state. 2. Implemented two-pass terraform apply in bootstrap v4: Pass 1 creates EKS (k8s disabled), Pass 2 creates k8s resources. |
| CI workflow had inline terraform commands | Violated "CLI first, CI mirrors" principle; couldn't reproduce CI locally | Replaced inline terraform with Make target calls (`make deploy-persistent`, `make deploy`) |

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| How to handle K8s provider chicken-and-egg | Two-pass terraform apply (detect cluster existence first) | Keeps single `make deploy-persistent` command; adds ~30s overhead only for fresh deployments |
| PR plan vs Apply variable drift | Option C: Accept drift (inline plan in PR, Make for apply) | Faster iteration; PR plan uses tfvars, apply uses Make vars. User accepted tradeoff. |
| Industry pattern for CI/Make | Make-as-interface (Kubernetes, HashiCorp style) | CLI first, CI mirrors. Enables local reproducibility and CI portability. |

## Artifacts Touched (links)

### Modified

- `.github/workflows/infra-terraform-apply-dev.yml` - Outcome-driven deployment via Make targets
- `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh` - Two-pass apply for fresh deployments
- `docs/changelog/entries/CL-0167-outcome-driven-ci.md` - Added Fixed section
- `docs/production-readiness-gates/ROADMAP.md` - Updated item 102 to In-Progress

### Added

- `docs/changelog/entries/CL-0167-outcome-driven-ci.md` - New changelog entry

### Referenced / Executed

- `envs/dev/main.tf` - Analyzed Kubernetes provider configuration
- `envs/dev/terraform.tfvars` - Checked lifecycle/build_id settings
- `Makefile` - Verified deploy-persistent and bootstrap-persistent-v4 targets

## Validation

- `terraform -chdir=envs/dev state list` - Verified clean state after removing stale resources
- `make -n deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4 CREATE_RDS=false` - Dry-run shows correct flow
- `terraform -chdir=envs/dev plan -var="cluster_lifecycle=persistent" -var="enable_k8s_resources=false"` - Plan succeeds: 47 to add

## Current State / Follow-ups

- **Ready for testing**: `make deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4 CREATE_RDS=false REGION=eu-west-2`
- **State cleaned**: Stale EKS cluster/IAM resources removed from Terraform state
- **Two-pass implemented**: Bootstrap v4 detects if cluster exists and uses single-pass or two-pass accordingly
- **Follow-up**: Apply same pattern to staging/prod workflows (ROADMAP-102 next step)

Signed: Claude Opus 4.5 (2026-01-23T13:30:00Z)

---

## Technical Details

### Two-Pass Apply Logic (bootstrap v4)

```bash
# Check if EKS cluster exists in AWS
if aws eks describe-cluster --name "${EXPECTED_CLUSTER}" --region "${REGION}" &>/dev/null; then
  # Single-pass: cluster exists
  terraform apply -var="apply_kubernetes_addons=true" -var="enable_k8s_resources=true"
else
  # Two-pass: fresh deployment
  # Pass 1: Create EKS (k8s disabled)
  terraform apply -var="apply_kubernetes_addons=false" -var="enable_k8s_resources=false"
  # Pass 2: Create k8s resources
  terraform apply -var="apply_kubernetes_addons=true" -var="enable_k8s_resources=true"
fi
```

### Outcome-Driven CI Pattern

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

### State Cleanup Commands Executed

```bash
# Remove stale kubernetes namespace
terraform -chdir=envs/dev state rm 'kubernetes_namespace_v1.external_secrets[0]'

# Remove stale EKS IAM resources
terraform -chdir=envs/dev state rm 'module.eks[0].aws_iam_role.cluster' \
  'module.eks[0].aws_iam_role_policy_attachment.cluster["arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"]' \
  'module.eks[0].aws_iam_role_policy_attachment.cluster["arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"]'
```

---

## Pattern Reference

> "CLI first, CI mirrors. CI says WHAT (inputs/outcomes), Make says HOW (terraform/kubectl). Enables local reproducibility and CI portability."
> — ROADMAP-102
