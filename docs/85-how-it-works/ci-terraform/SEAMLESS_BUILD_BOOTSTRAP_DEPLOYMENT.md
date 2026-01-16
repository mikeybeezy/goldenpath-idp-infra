---
id: SEAMLESS_BUILD_BOOTSTRAP_DEPLOYMENT
title: 'How It Works: Seamless Build and Bootstrap Deployment'
type: documentation
relates_to:
  - CI_TERRAFORM_WORKFLOWS
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0148-seamless-build-deployment-with-immutability
---

This guide explains the detailed mechanics of the seamless two-phase deployment system with build_id immutability enforcement.

## Overview

The seamless deployment system provides a single-command user experience while maintaining clear separation between infrastructure (Terraform) and platform (Kubernetes/ArgoCD) concerns.

**User runs**:
```bash
make deploy ENV=dev BUILD_ID=13-01-26-03
```

**System executes**:
1. Validates build_id format and uniqueness
2. Phase 1: Provisions AWS infrastructure via Terraform
3. Phase 2: Bootstraps Kubernetes platform via shell scripts
4. Phase 3: Verifies deployment health
5. Records build metadata to governance-registry

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    make deploy                              │
│              (Single User Command)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Makefile Orchestration                         │
│  - Validates BUILD_ID format (DD-MM-YY-NN)                 │
│  - Fetches governance-registry branch                       │
│  - Logs all output to timestamped files                     │
└────────┬────────────────────┬───────────────────┬───────────┘
         │                    │                   │
         ▼                    ▼                   ▼
┌────────────────┐   ┌────────────────┐   ┌─────────────┐
│   Phase 1      │   │   Phase 2      │   │  Phase 3    │
│ Infrastructure │──→│   Bootstrap    │──→│ Verification│
│   (Terraform)  │   │  (Shell+Helm)  │   │  (kubectl)  │
└────────────────┘   └────────────────┘   └─────────────┘
         │                    │                   │
         └────────────────────┴───────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────────┐
         │     governance-registry branch          │
         │   Record build timing + inventory       │
         └─────────────────────────────────────────┘
```

## Phase 1: Infrastructure (Terraform)

### What Happens

```bash
# Internal command (you don't run this directly)
make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-03
```

### Execution Flow

```
1. Makefile Stage
   ├── Validates BUILD_ID format
   ├── Creates log directory: logs/build-timings/
   └── Sets terraform variables

2. Terraform Init (if needed)
   └── Initialize backend and providers

3. Build ID Validation (terraform plan phase)
   ├── Layer 1: Format Validation (variable validation)
   ├── Layer 2: Registry Check (data.external)
   │   └── Executes: git show origin/governance-registry:...build_timings.csv
   └── Layer 3: Lifecycle Precondition (null_resource)
       └── Fails plan if duplicate found

4. Terraform Apply
   ├── Create VPC + Subnets
   ├── Create Security Groups
   ├── Create EKS Cluster
   ├── Create IAM Roles (cluster, nodes, IRSA)
   ├── Create Node Groups
   ├── Create Service Accounts (kubernetes_service_account_v1)
   │   ├── aws-load-balancer-controller (kube-system)
   │   ├── cluster-autoscaler (kube-system)
   │   └── external-secrets (external-secrets-system)
   └── Wait for cluster Ready

5. Output Variables
   ├── cluster_endpoint
   ├── cluster_ca_certificate
   ├── oidc_provider_arn
   └── service_account_role_arns
```

### Key Terraform Resources (envs/dev/main.tf)

**Build ID Validation**:
```hcl
# Lines 20-50: Build ID immutability enforcement
data "external" "build_id_check" {
  count   = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0
  program = ["bash", "-c", <<-EOT
    set -e
    BUILD_ID="${var.build_id}"
    ENV="${var.environment}"
    REGISTRY_BRANCH="${var.governance_registry_branch}"
    CSV_PATH="environments/development/latest/build_timings.csv"

    # Fetch CSV from governance-registry branch
    CSV_CONTENT=$(git show "origin/$REGISTRY_BRANCH:$CSV_PATH" 2>/dev/null || echo "")

    if [ -z "$CSV_CONTENT" ]; then
      echo '{"exists":"false","error":"Registry CSV not found or git fetch needed"}'
      exit 0
    fi

    # Check if build_id exists for this environment (skip header)
    if echo "$CSV_CONTENT" | grep -q ",$ENV,$BUILD_ID," 2>/dev/null; then
      echo '{"exists":"true","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    else
      echo '{"exists":"false","build_id":"'"$BUILD_ID"'","environment":"'"$ENV"'"}'
    fi
  EOT
  ]
}

resource "null_resource" "enforce_build_id_immutability" {
  count = var.cluster_lifecycle == "ephemeral" && var.build_id != "" ? 1 : 0

  lifecycle {
    precondition {
      condition     = !var.allow_build_id_reuse ? try(data.external.build_id_check[0].result.exists, "false") == "false" : true
      error_message = <<-EOT
        Build ID ${var.build_id} already exists for environment ${var.environment}.

        This build_id was previously used. To prevent state corruption and resource conflicts,
        you must use a unique build_id for each ephemeral cluster deployment.

        Options:
        1. Use a new build_id (recommended): Increment the sequence number
           Example: If current is 13-01-26-01, use 13-01-26-02

        2. Override protection (NOT recommended, only for testing/recovery):
           terraform apply -var="build_id=${var.build_id}" -var="allow_build_id_reuse=true"

           WARNING: Reusing build_ids can cause:
           - Terraform state corruption
           - Resource naming conflicts
           - Lost audit trail

        Check governance registry for existing builds:
        git show origin/governance-registry:environments/development/latest/build_timings.csv
      EOT
    }
  }
}
```

**Service Accounts** (Created before kubernetes_addons module):
```hcl
# Lines 267-319: Service accounts with IRSA annotations
resource "kubernetes_service_account_v1" "aws_load_balancer_controller" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_lb_controller_role ? 1 : 0

  metadata {
    name      = var.iam_config.lb_controller_service_account_name
    namespace = var.iam_config.lb_controller_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].lb_controller_role_arn
    }
  }

  depends_on = [
    module.eks,
    module.iam,
    aws_eks_access_policy_association.terraform_admin
  ]
}
```

**kubernetes_addons Module** (Depends on service accounts):
```hcl
# Lines 333-352: Helm releases for ArgoCD + controllers
module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  path_to_app_manifests = "${path.module}/../../gitops/argocd/apps/dev"
  argocd_values         = file("${path.module}/../../gitops/helm/argocd/values/dev.yaml")

  vpc_id       = module.vpc.vpc_id
  cluster_name = local.cluster_name_effective
  aws_region   = var.aws_region

  depends_on = [
    module.eks,
    kubernetes_service_account_v1.aws_load_balancer_controller,
    aws_eks_access_policy_association.terraform_admin
  ]
}
```

### Error Scenarios

#### Error 1: Duplicate Build ID

```
╷
│ Error: Resource precondition failed
│
│ on main.tf line 45, in resource "null_resource" "enforce_build_id_immutability":
│
│ Build ID 13-01-26-03 already exists for environment dev.
│
│ This build_id was previously used. To prevent state corruption...
│
│ Options:
│ 1. Use a new build_id (recommended): 13-01-26-04
│ 2. Override: -var="allow_build_id_reuse=true" (NOT recommended)
╵
```

**Solution**: Use next sequence number (13-01-26-04)

#### Error 2: Invalid Format

```
╷
│ Error: Invalid value for variable
│
│ on variables.tf line 42:
│
│ build_id must match format: DD-MM-YY-NN (e.g., 13-01-26-01)
╵
```

**Solution**: Fix format to DD-MM-YY-NN

#### Error 3: Registry Not Found

```
Warning: Registry CSV not found or git fetch needed
Will proceed but build_id validation is skipped
```

**Solution**: Fetch governance-registry branch:
```bash
git fetch origin governance-registry
```

## Phase 2: Platform Bootstrap (Shell Script)

### What Happens

```bash
# Internal command (you don't run this directly)
make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-03
```

### Execution Flow

```
bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
│
├── STAGE 1: Cluster Context
│   └── aws eks update-kubeconfig
│
├── STAGE 2: Tool Checks
│   └── Verify kubectl, helm, aws CLI
│
├── STAGE 3: EKS Preflight
│   └── Verify cluster accessibility
│
├── STAGE 3B: Service Accounts
│   └── Verify IRSA service accounts exist
│
├── STAGE 4: Capacity Check
│   └── Ensure minimum Ready nodes
│
├── STAGE 5: Metrics Server
│   └── Deploy metrics-server (for HPA)
│
├── STAGE 6: Argo CD
│   └── Deploy ArgoCD via Helm
│       └── Uses kubernetes_addons module (terraform)
│
├── STAGE 7: Core Add-ons
│   └── Deploy AWS Load Balancer Controller
│       └── Uses kubernetes_addons module (terraform)
│
├── STAGE 8: Autoscaler App
│   └── kubectl apply -f cluster-autoscaler.yaml
│
├── STAGE 9: Autoscaler Ready
│   └── Wait for autoscaler deployment
│
├── STAGE 10: Platform Apps
│   └── kubectl apply -f gitops/argocd/apps/dev/*.yaml
│       (excludes cluster-autoscaler, kong)
│
├── STAGE 11: Kong
│   └── kubectl apply -f kong.yaml
│   └── Validate Kong ingress
│
├── STAGE 12: Audit
│   └── Run smoke tests and audit checks
│
├── STAGE 13: Optional Scale Down
│   └── If SCALE_DOWN_AFTER_BOOTSTRAP=true
│       └── terraform apply -var="bootstrap_mode=false"
│
└── STAGE 14-15: Verification
    ├── kubectl get nodes
    ├── kubectl top nodes
    ├── kubectl -n argocd get applications
    └── kubectl -n kong-system get svc
```

### Key Characteristics

**Resilient**: Each stage can be retried independently
**Verbose**: Clear logging with stage banners
**Conditional**: Stages can be skipped via env vars
**Verifiable**: Built-in health checks at each stage

### Environment Variables

```bash
# Passed to bootstrap script
SKIP_ARGO_SYNC_WAIT=true           # Skip waiting for ArgoCD sync
SKIP_CERT_MANAGER_VALIDATION=true  # Skip cert-manager validation
NODE_INSTANCE_TYPE=t3.small        # Node instance type for preflight
ENV_NAME=dev                       # Environment name
COMPACT_OUTPUT=false               # Reduce log verbosity
SCALE_DOWN_AFTER_BOOTSTRAP=false   # Scale down nodes after bootstrap
ENABLE_TF_K8S_RESOURCES=true       # Enable Terraform k8s resources
TF_DIR=envs/dev                    # Terraform directory
```

### Terraform Integration in Bootstrap

The bootstrap script calls terraform for the kubernetes_addons module:

```bash
# Inside bootstrap-v3.sh, STAGE 6 & 7
# This applies ONLY the kubernetes_addons module

terraform -chdir="${TF_DIR}" apply \
  -var="enable_k8s_resources=true" \
  -auto-approve

# This deploys:
# - helm_release.argocd
# - helm_release.aws_load_balancer_controller
# - helm_release.bootstrap_apps (ArgoCD Applications)
```

## Phase 3: Verification

### What Happens

```bash
# Internal command
make _phase3-verify ENV=dev
```

### Checks Performed

```bash
# 1. Nodes are Ready
kubectl get nodes

# 2. Metrics server working
kubectl top nodes

# 3. ArgoCD Applications deployed
kubectl -n argocd get applications

# 4. Kong ingress has external IP
kubectl -n kong-system get svc
```

### Success Criteria

- ✅ All nodes show STATUS=Ready
- ✅ Metrics data available (not "error")
- ✅ All ArgoCD apps show SYNC=Synced, HEALTH=Healthy
- ✅ Kong service has EXTERNAL-IP assigned

## Recording to Governance Registry

### When Recording Happens

```
After Phase 1 completes:
  scripts/record-build-timing.sh dev 13-01-26-03 terraform-apply

After Phase 2 completes:
  scripts/record-build-timing.sh dev 13-01-26-03 bootstrap

After teardown completes:
  scripts/record-build-timing.sh dev 13-01-26-03 teardown
```

### Recording Script Logic

```bash
#!/usr/bin/env bash
# scripts/record-build-timing.sh

ENV="$1"           # dev
BUILD_ID="$2"      # 13-01-26-03
PHASE="$3"         # terraform-apply | bootstrap | teardown

# 1. Find latest log for this phase+build_id
LOG_DIR="logs/build-timings"
LATEST_LOG=$(ls -t "$LOG_DIR/$PHASE-$ENV-"*"$BUILD_ID"*.log | head -1)

# 2. Extract timing data
START_TIME=$(head -1 "$LATEST_LOG" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DURATION=$(($(date -d "$END_TIME" +%s) - $(date -d "$START_TIME" +%s)))
EXIT_CODE=$(tail -1 "$LATEST_LOG" | grep -oP 'exit \K\d+' || echo 0)

# 3. Extract inventory from terraform output (if terraform-apply phase)
if [[ "$PHASE" == "terraform-apply" ]]; then
  RESOURCES_ADDED=$(grep -oP 'Plan: \K\d+(?= to add)' "$LATEST_LOG" || echo 0)
  RESOURCES_CHANGED=$(grep -oP ', \K\d+(?= to change)' "$LATEST_LOG" || echo 0)
  RESOURCES_DESTROYED=$(grep -oP ', \K\d+(?= to destroy)' "$LATEST_LOG" || echo 0)
else
  RESOURCES_ADDED=0
  RESOURCES_CHANGED=0
  RESOURCES_DESTROYED=0
fi

# 4. Append to governance-registry CSV
git fetch origin governance-registry
git checkout governance-registry

echo "$START_TIME,$END_TIME,$PHASE,$ENV,$BUILD_ID,$DURATION,$EXIT_CODE,\"\",$RESOURCES_ADDED,$RESOURCES_CHANGED,$RESOURCES_DESTROYED,$LATEST_LOG" >> \
  environments/development/latest/build_timings.csv

# 5. Commit and push
git add environments/development/latest/build_timings.csv
git commit -m "chore(registry): record $PHASE for $ENV build $BUILD_ID"
git push origin governance-registry

# 6. Return to original branch
git checkout -
```

### CSV Format

```csv
start_time_utc,end_time_utc,phase,env,build_id,duration_seconds,exit_code,flags,resources_added,resources_changed,resources_destroyed,log_path
2026-01-13T18:00:00Z,2026-01-13T18:15:00Z,terraform-apply,dev,13-01-26-03,900,0,"",47,12,0,logs/build-timings/terraform-apply-dev-goldenpath-dev-eks-13-01-26-03-20260113T180000Z.log
2026-01-13T18:16:00Z,2026-01-13T18:40:00Z,bootstrap,dev,13-01-26-03,1440,0,"",0,0,0,logs/build-timings/bootstrap-dev-goldenpath-dev-eks-13-01-26-03-20260113T181600Z.log
```

## Error Handling & Recovery

### Phase 1 Fails

**Scenario**: Terraform apply fails (e.g., AWS quota exceeded)

**Recovery**:
```bash
# Fix the issue (e.g., request quota increase)
# Then retry just Phase 1
make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-03
```

### Phase 2 Fails

**Scenario**: Bootstrap script fails at STAGE 8 (cluster-autoscaler)

**Recovery**:
```bash
# Terraform infrastructure already exists
# Retry just the bootstrap
make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-03

# Or retry from specific stage
bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh goldenpath-dev-eks-13-01-26-03 eu-west-2
```

### Service Account Missing

**Scenario**: Service account not found during bootstrap

**Cause**: Terraform didn't create service accounts (enable_k8s_resources=false?)

**Recovery**:
```bash
# Apply Terraform with K8s resources enabled
cd envs/dev
terraform apply -var="enable_k8s_resources=true" -var="build_id=13-01-26-03"
```

## Performance Characteristics

### Typical Timings

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| Phase 1: Infrastructure | 15-20 min | VPC, EKS cluster, node groups |
| Phase 2: Bootstrap | 20-25 min | ArgoCD, controllers, apps sync |
| Phase 3: Verification | 1-2 min | kubectl health checks |
| **Total** | **36-47 min** | Full platform deployment |

### Optimization Tips

1. **Use bootstrap_mode**: Set larger nodes during bootstrap, scale down after
2. **Skip sync waits**: Set `SKIP_ARGO_SYNC_WAIT=true` for faster bootstrap
3. **Parallel applies**: Use terraform `-parallelism=20` for faster Phase 1
4. **Pre-warm AMIs**: Use custom EKS-optimized AMIs with tools pre-installed

## Troubleshooting Guide

### Build ID Validation Failed

**Symptom**:
```
Error: Build ID 13-01-26-03 already exists
```

**Check**:
```bash
git show origin/governance-registry:environments/development/latest/build_timings.csv | grep "13-01-26-03"
```

**Solution**: Use next sequence number (13-01-26-04)

### Registry Branch Not Found

**Symptom**:
```
Warning: Registry CSV not found
```

**Check**:
```bash
git branch -r | grep governance-registry
```

**Solution**:
```bash
git fetch origin governance-registry
```

### Service Account Already Exists

**Symptom**:
```
Error: serviceaccount "aws-load-balancer-controller" already exists
```

**Cause**: Previous incomplete deployment

**Solution**:
```bash
kubectl delete serviceaccount aws-load-balancer-controller -n kube-system
make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-04
```

### ArgoCD Applications Not Deploying

**Symptom**: kubectl get applications shows empty

**Check**:
```bash
helm list -n argocd
# Should show: bootstrap-apps
```

**Solution**:
```bash
# If bootstrap-apps missing, re-run Phase 2
make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-03
```

## References

- Makefile: [Makefile](../../Makefile) (deploy target)
- Bootstrap script: [bootstrap-v3.sh](../../bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh)
- Terraform config: [envs/dev/main.tf](../../envs/dev/main.tf)
- ADR: [ADR-0148](../adrs/ADR-0148-seamless-build-deployment-with-immutability.md)
- Changelog: [CL-0121](../changelog/entries/CL-0121-seamless-build-deployment.md)
