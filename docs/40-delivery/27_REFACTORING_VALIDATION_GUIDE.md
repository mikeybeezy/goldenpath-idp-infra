---
id: 27_REFACTORING_VALIDATION_GUIDE
title: Refactoring Validation Guide
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# Refactoring Validation Guide

Doc contract:

- Purpose: Standard Operating Procedure (SOP) for validating deep infrastructure refactors using ephemeral environments.
- Owner: platform
- Status: living
- Related: docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md

---

## 1. When to use this guide

Use this procedure when making "High Risk" changes such as:

- Refactoring bootstrap logic.
- Upgrading Kubernetes versions.
- Changing core network modules (VPC, Subnets).
- Replacing provider versions.

## 2. Validation Workflow

We rely on **Ephemeral Environments** to validate changes safely without impacting the shared `dev` environment.

### Phase 1: Local Dry Run

Before pushing code, ensure the plan is valid locally.

```bash
# Validates syntax and provider schema
terraform -chdir=envs/dev validate

# Checks for destructive changes (red text)
terraform -chdir=envs/dev plan
```

### Phase 2: Manual Plan (Required)

The `Apply` workflow enforces that a successful `Plan` has run for the specific commit. Since we are testing a feature branch, we must trigger this manually.

1. Navigate to **Actions** -> **Plan - Infra Terraform Checks**.
2. **Use workflow from**: Select your branch (e.g., `feature/terraform-bootstrap`).
3. Run workflow with inputs:
    - `env`: **dev**
    - `lifecycle`: **ephemeral**
    - `build_id`: **<your-initials>-01**
    - `new_build`: **true**
4. **Wait for success (Green Tick).**

### Phase 3: Ephemeral CI Environment (Apply)

1. Navigate to **Actions** -> **Infra Terraform Apply (dev)**.
2. **Use workflow from**: Select your branch (`feature/terraform-bootstrap`).
3. Run workflow with inputs:
    - `lifecycle`: **ephemeral**
    - `confirm_apply`: **apply**
    - `build_id`: **<your-initials>-01**
    - `new_build`: **true**

**Why?** This creates a brand new EKS cluster from scratch using your code. If the bootstrap logic is broken, it will fail here, leaving `dev` untouched.

### Phase 4: Verification Checks

Once the CI job succeeds, connect to the ephemeral cluster:

```bash
# Update local kubeconfig
aws eks update-kubeconfig --name goldenpath-dev-msk-01 --region eu-west-2

# Verify Nodes
kubectl get nodes

# Verify ArgoCD (Critical System)
kubectl -n argocd get pods
kubectl -n argocd get applications

# Verify Access
kubectl -n kong-system get svc
```

### Phase 5: Teardown

To avoid unnecessary costs, destroy the environment immediately after verification.

1. Navigate to **Actions** -> **Teardown**.
2. **Use workflow from**: Select your branch again.
3. Run workflow with:
    - `lifecycle`: **ephemeral**
    - `build_id`: **<your-initials>-01**
    - `cleanup_orphans`: **true**

## 3. Merge Criteria

You may merge your PR when:

1. Ephemeral environment created successfully (Green CI).
2. Core addons (ArgoCD) are healthy.
3. Teardown completed successfully.
