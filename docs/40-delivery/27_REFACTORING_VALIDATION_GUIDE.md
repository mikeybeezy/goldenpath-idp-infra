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

### Phase 2: Ephemeral CI Environment

1.  Push your feature branch to GitHub (e.g., `feature/terraform-bootstrap`).
2.  Navigate to **Actions** -> **Infra Terraform Apply (dev)**.
3.  **Use workflow from**: Select your branch (`feature/terraform-bootstrap`) from the dropdown. *This is critical to test your new code.*
4.  Run workflow with these inputs:
    *   `lifecycle`: **ephemeral**
    *   `confirm_apply`: **apply**
    *   `build_id`: **<your-initials>-01** (e.g., `msk-01`)
    *   `new_build`: **true**

**Why?** This creates a brand new EKS cluster from scratch using your code. If the bootstrap logic is broken, it will fail here, leaving `dev` untouched.

### Phase 3: Verification Checks

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

### Phase 4: Teardown

To avoid unnecessary costs, destroy the environment immediately after verification.

1.  Navigate to **Actions** -> **Teardown**.
2.  **Use workflow from**: Select your branch again.
3.  Run workflow with:
    *   `lifecycle`: **ephemeral**
    *   `build_id`: **<your-initials>-01**
    *   `cleanup_orphans`: **true**

## 3. Merge Criteria

You may merge your PR when:
1.  Ephemeral environment created successfully (Green CI).
2.  Core addons (ArgoCD) are healthy.
3.  Teardown completed successfully.
