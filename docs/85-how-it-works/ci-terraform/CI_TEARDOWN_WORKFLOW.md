---
id: CI_TEARDOWN_WORKFLOW
title: 'How It Works: CI Teardown Workflow'
type: documentation
relates_to:
  - CI_TERRAFORM_WORKFLOWS
  - SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT
  - RB-0015-teardown-and-cleanup
---

This guide explains the CI teardown workflow for destroying ephemeral EKS clusters and cleaning up associated resources.

## Overview

Teardown is the **reverse of bootstrap** - it must clean up resources in the correct order to avoid orphaned AWS resources (ENIs, Load Balancers, Security Groups).

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    LIFECYCLE PHASES                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BUILD                          TEARDOWN (Reverse Order)            │
│  ─────                          ────────────────────────            │
│  1. Terraform Apply             3. Terraform Destroy                │
│  2. Bootstrap (Helm)            2. Bootstrap Cleanup                │
│  3. Apps (ArgoCD)               1. Apps & LB Cleanup                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Workflow: `ci-teardown.yml`

### Trigger

Manual workflow dispatch only - teardown requires explicit confirmation.

```yaml
on:
  workflow_dispatch:
    inputs:
      env: dev/test/staging/prod
      build_id: DD-MM-YY-NN
      lifecycle: ephemeral/persistent
      cleanup_mode: delete/dry_run/none
```

### Phased Execution

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    TEARDOWN PHASES                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: App & Ingress Cleanup                                     │
│  ├─ Delete ArgoCD application (e.g., dev-kong)                      │
│  ├─ Wait for LoadBalancer services to terminate                     │
│  ├─ Force delete stuck LB finalizers (if enabled)                   │
│  └─ Wait for ENI cleanup (up to 15 minutes)                         │
│                                                                      │
│  Phase 2: Pre-Destroy Cleanup                                       │
│  ├─ Relax PDB (Pod Disruption Budgets)                              │
│  ├─ Drain node groups                                               │
│  ├─ Remove kubernetes_service_account from TF state                 │
│  └─ Clean up orphaned K8s resources                                 │
│                                                                      │
│  Phase 3: Terraform Destroy                                         │
│  ├─ terraform destroy -auto-approve                                 │
│  └─ Orphan sweep (ENIs, Security Groups, EBS)                       │
│                                                                      │
│  Phase 4: Auto-Resume (if failure)                                  │
│  └─ Retry teardown with state refresh                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `build_id` | Required | Build ID to tear down (DD-MM-YY-NN) |
| `lifecycle` | ephemeral | Cluster lifecycle type |
| `cleanup_mode` | delete | Orphan cleanup: `delete`, `dry_run`, `none` |
| `delete_argo_app` | true | Delete ArgoCD app before LB cleanup |
| `argo_app_name` | dev-kong | ArgoCD application to delete |
| `lb_cleanup_max_wait` | 900 | Max seconds to wait for LB deletion |
| `force_delete_lbs` | true | Force delete remaining LBs |
| `force_delete_lb_finalizers` | true | Remove stuck finalizers |
| `drain_timeout` | 300s | Node drain timeout |
| `relax_pdb` | true | Relax PDB during teardown |

## Why Order Matters

### The Problem: Orphaned Resources

Kong (via AWS Load Balancer Controller) creates:

- **Application Load Balancers** (ALBs)
- **Target Groups**
- **Elastic Network Interfaces** (ENIs)
- **Security Group rules**

If you run `terraform destroy` before cleaning these up:

```text
terraform destroy
    │
    ├─► Tries to delete VPC
    │       │
    │       └─► FAILS: "ENI eni-xxx is in use"
    │
    └─► Tries to delete Security Groups
            │
            └─► FAILS: "Security group sg-xxx has dependencies"
```

### The Solution: Reverse Order

```text
1. Delete ArgoCD apps (triggers LB controller cleanup)
       │
       └─► LB Controller deletes ALBs, Target Groups
               │
               └─► AWS releases ENIs (async, ~2-5 min)

2. Wait for ENI cleanup
       │
       └─► Poll until no cluster-tagged ENIs remain

3. Terraform destroy
       │
       └─► VPC, subnets, security groups delete cleanly
```

## Makefile Targets

The workflow calls these Makefile targets:

```bash
# Full timed teardown
make timed-teardown ENV=dev BUILD_ID=15-01-26-01

# Resume after failure
make teardown-resume ENV=dev BUILD_ID=15-01-26-01

# Pre-destroy cleanup only
make pre-destroy-cleanup ENV=dev BUILD_ID=15-01-26-01

# Orphan cleanup only
make cleanup-orphans ENV=dev BUILD_ID=15-01-26-01
```

## Teardown Logging

Successful teardowns generate logs in `docs/build-run-logs/`:

```text
docs/build-run-logs/
├── TD-15-01-26-01-20260115T123456Z.md   # Teardown log
└── BR-15-01-26-01-20260115T012345Z.md   # Build log (for reference)
```

## Troubleshooting

### Error: ENIs still attached

```text
Error: deleting EC2 Subnet: DependencyViolation: The subnet has dependencies
```

**Cause**: ENIs from deleted Load Balancers haven't been released yet.

**Solution**:

1. Wait longer (`lb_cleanup_max_wait`)
2. Run orphan cleanup manually:
   ```bash
   make cleanup-orphans CLEANUP_MODE=delete
   ```

### Error: Finalizer stuck on Service

```text
Service "kong-proxy" has finalizer preventing deletion
```

**Cause**: AWS LB Controller finalizer stuck.

**Solution**: Enable `force_delete_lb_finalizers: true` or manually:

```bash
kubectl patch svc kong-proxy -n kong-system -p '{"metadata":{"finalizers":null}}'
```

### Error: PDB preventing node drain

```text
Cannot evict pod: would violate PodDisruptionBudget
```

**Cause**: PDB blocking eviction during drain.

**Solution**: Enable `relax_pdb: true` or manually:

```bash
kubectl delete pdb --all -A
```

## References

- [CI Terraform Workflows](CI_TERRAFORM_WORKFLOWS.md) - Build and apply
- [Seamless Build Bootstrap Deployment](SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT.md) - Bootstrap phase
- [Teardown Runbook](../../70-operations/runbooks/RB-0015-teardown-and-cleanup.md) - Operational procedures
