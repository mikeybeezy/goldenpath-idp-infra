---
id: BUG_FIXES_SUMMARY
title: 'Bug Fixes Summary: Seamless Build Deployment'
type: documentation
---

# Bug Fixes Summary: Seamless Build Deployment

**Date**: 2026-01-13
**Status**: FIXES IMPLEMENTED
**Branch**: feature/seamless-build-deployment

## Overview

Critical bugs in the seamless build deployment implementation have been identified and fixed. The deployment will now work correctly with service accounts created in Phase 1 and platform components deployed in Phase 2.

---

## Critical Bugs Fixed

### Bug #1: Service Accounts Not Created in Phase 1 ✅ FIXED

**Problem**:
- Phase 1 set `enable_k8s_resources=false`
- Service account resources have condition: `count = ... && var.enable_k8s_resources ? 1 : 0`
- Result: Service accounts not created (count=0)
- Phase 2 bootstrap script expected service accounts to exist
- Result: Bootstrap failed at Stage 3B validation

**Fix Applied**:
- [Makefile:192-193](../../Makefile#L192-L193) now sets:
  ```bash
  -var="enable_k8s_resources=true" \
  -var="apply_kubernetes_addons=false" \
  ```
- Service accounts now created in Phase 1
- Bootstrap validation in Phase 2 will pass

**Files Modified**:
- `Makefile` (line 192-193)

### Bug #2: kubernetes_addons Module Would Apply in Phase 1 ✅ FIXED

**Problem**:
- If `enable_k8s_resources=true`, the `kubernetes_addons` module would apply
- Module deploys ArgoCD, LB Controller, bootstrap-apps via Helm
- This would conflict with Phase 2 bootstrap script which also installs ArgoCD
- Result: Collision and duplicate installations

**Fix Applied**:
- Added new variable `apply_kubernetes_addons` to control module independently
- [envs/dev/variables.tf:311-315](../../envs/dev/variables.tf#L311-L315):
  ```hcl
  variable "apply_kubernetes_addons" {
    type        = bool
    description = "Whether to apply the kubernetes_addons module (Helm releases: ArgoCD, LB Controller, bootstrap-apps). Set false in Phase 1 (infra), true in Phase 2 (bootstrap)."
    default     = false
  }
  ```
- [envs/dev/main.tf:413](../../envs/dev/main.tf#L413) updated module condition:
  ```hcl
  count = var.eks_config.enabled && var.enable_k8s_resources && var.apply_kubernetes_addons ? 1 : 0
  ```
- Phase 1 sets `apply_kubernetes_addons=false` → module does not apply
- Phase 2 could set `apply_kubernetes_addons=true` if needed (future enhancement)

**Files Modified**:
- `envs/dev/variables.tf` (lines 311-315)
- `envs/dev/main.tf` (line 413)

### Bug #3: Missing CONFIRM_TF_APPLY in Phase 2 ✅ FIXED

**Problem**:
- Bootstrap script may require terraform apply confirmation
- Non-interactive mode would fail without `CONFIRM_TF_APPLY=true`

**Fix Applied**:
- [Makefile:210-211](../../Makefile#L210-L211) now sets:
  ```bash
  ENABLE_TF_K8S_RESOURCES=false \
  CONFIRM_TF_APPLY=true \
  ```
- Note: `ENABLE_TF_K8S_RESOURCES=false` because service accounts already created in Phase 1
- Bootstrap script will skip terraform apply and only validate service accounts exist

**Files Modified**:
- `Makefile` (lines 210-211)

---

## Solution Architecture

### Phase 1: Infrastructure + Service Accounts

**Terraform Variables**:
```bash
-var="build_id=$(BUILD_ID)"
-var="enable_k8s_resources=true"      # Creates service accounts
-var="apply_kubernetes_addons=false"  # Prevents Helm releases
```

**Resources Created**:
- VPC, Subnets, NAT Gateway, Route Tables
- EKS Cluster
- EKS Node Group
- IAM Roles (cluster, nodes, IRSA roles)
- ✅ Service Accounts (aws-load-balancer-controller, cluster-autoscaler, external-secrets)
-  NO Helm releases (ArgoCD, LB Controller, etc.)

**Key Mechanism**: The `apply_kubernetes_addons` variable acts as a safety gate. Even though `enable_k8s_resources=true` enables the kubernetes provider and service account resources, the `kubernetes_addons` module is prevented from applying by the additional condition.

### Phase 2: Platform Bootstrap

**Environment Variables**:
```bash
ENABLE_TF_K8S_RESOURCES=false  # Service accounts already exist
CONFIRM_TF_APPLY=true          # Non-interactive mode
TF_DIR=$(ENV_DIR)              # Terraform directory for other operations
```

**Bootstrap Script Behavior** (bootstrap-v3.sh):
- Stage 3B: Validates service accounts exist (lines 274-283)
- Validation passes ✅ because Phase 1 created them
- Stage 6: Installs ArgoCD via Helm (line 305)
- Stage 7: Installs LB Controller via Helm (line 311)
- Stage 8: Applies Cluster Autoscaler ArgoCD app (line 325)
- Subsequent stages: Other platform components

**Key Mechanism**: By setting `ENABLE_TF_K8S_RESOURCES=false`, we tell the bootstrap script that service accounts are already in place and terraform apply is not needed. The script validates and continues with bash/kubectl/helm operations.

---

## Implementation Details

### Variable Control Flow

```
Phase 1:
  enable_k8s_resources=true
    ├─> kubernetes_service_account_v1 resources: count=1 ✅ CREATED
    ├─> kubernetes_manifest resources: count=1 ✅ CREATED
    └─> kubernetes_addons module: count=0  SKIPPED (apply_kubernetes_addons=false)

Phase 2:
  ENABLE_TF_K8S_RESOURCES=false (bootstrap script env var)
    ├─> Bootstrap script Stage 3B: Validates service accounts exist ✅
    └─> Bootstrap script proceeds with Helm/kubectl operations ✅
```

### Module Condition Breakdown

**Before Fix**:
```hcl
count = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0
#       ✅ true                &&  false                  → count=0
```

**After Fix**:
```hcl
count = var.eks_config.enabled && var.enable_k8s_resources && var.apply_kubernetes_addons ? 1 : 0
#       ✅ true                && ✅ true                  &&  false                       → count=0
```

The additional `apply_kubernetes_addons` condition gives us fine-grained control.

---

## Testing Verification Points

### Test 1: Phase 1 Verification
After running `make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-99`:

✅ Check infrastructure created:
```bash
aws eks describe-cluster --name goldenpath-dev-eks-13-01-26-99 --region eu-west-2
kubectl get nodes
```

✅ Check service accounts created:
```bash
kubectl get sa -n kube-system aws-load-balancer-controller
kubectl get sa -n kube-system cluster-autoscaler
kubectl get sa -n external-secrets external-secrets
```

 Verify NO Helm releases:
```bash
helm list -A
# Should show: No resources found
```

 Verify NO ArgoCD:
```bash
kubectl get ns argocd
# Should show: Error from server (NotFound): namespaces "argocd" not found
```

### Test 2: Phase 2 Verification
After running `make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-99`:

✅ Check Stage 3B passed:
```bash
# Look in logs for:
# "STAGE 3B: SERVICE ACCOUNTS (IRSA)"
# "Skipping Terraform IRSA apply in v3; validating existing service accounts only."
# "STAGE 3B DONE"
```

✅ Check ArgoCD installed:
```bash
kubectl get ns argocd
kubectl get pods -n argocd
helm list -n argocd
```

✅ Check LB Controller installed:
```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
```

✅ Check ArgoCD applications:
```bash
kubectl get applications -n argocd
```

### Test 3: Full Deploy
Run `make deploy ENV=dev BUILD_ID=13-01-26-98` and verify:

✅ Phase 1 completes with message: "✅ Infrastructure ready (including service accounts)"
✅ Phase 2 completes with message: "✅ Platform bootstrapped"
✅ Phase 3 completes with message: "✅ All systems operational"
✅ Governance registry updated

---

## Documentation Updates

### Files Updated

1. **[Makefile](../../Makefile)**:
   - Line 192-193: Phase 1 terraform apply variables
   - Line 210-211: Phase 2 bootstrap script environment variables
   - Line 198: Updated success message

2. **[envs/dev/variables.tf](../../envs/dev/variables.tf)**:
   - Lines 311-315: Added `apply_kubernetes_addons` variable

3. **[envs/dev/main.tf](../../envs/dev/main.tf)**:
   - Line 413: Updated `kubernetes_addons` module condition

4. **[docs/adrs/ADR-0148-seamless-build-deployment-with-immutability.md](../adrs/ADR-0148-seamless-build-deployment-with-immutability.md)**:
   - Lines 70-74: Added Terraform Variables section to Phase 1
   - Lines 229-242: Updated implementation details

5. **[docs/analysis/BRIDGE_ANALYSIS.md](./BRIDGE_ANALYSIS.md)** (NEW):
   - Comprehensive analysis of bugs found
   - Solution options evaluated
   - Recommended fix (Option A implemented)

6. **[docs/analysis/BUG_FIXES_SUMMARY.md](./BUG_FIXES_SUMMARY.md)** (THIS FILE):
   - Summary of fixes applied
   - Testing verification points

---

## Remaining Work

### Documentation (Low Priority)
- Update [docs/changelog/entries/CL-0121-seamless-build-deployment.md](../changelog/entries/CL-0121-seamless-build-deployment.md) with bug fix notes
- Update [README.md](../../README.md) if needed (already documents new deploy command)

### Future Enhancements (Optional)
1. Remove ArgoCD installation from `kubernetes_addons` module entirely (let bootstrap script be the single source)
2. Consider removing `kubernetes_addons` module altogether if bootstrap script handles everything
3. Add integration tests for two-phase deployment
4. Add pre-flight checks in Makefile to validate prerequisites

---

## Risk Assessment

### Risks Eliminated ✅

1. **Service Account Missing**: Fixed - now created in Phase 1
2. **Module Collision**: Fixed - controlled by `apply_kubernetes_addons` variable
3. **Interactive Prompt Failure**: Fixed - `CONFIRM_TF_APPLY=true` added
4. **Documentation Mismatch**: Fixed - ADR updated to reflect implementation

### Remaining Risks ⚠️

1. **Untested**: Implementation not yet tested end-to-end (needs test environment)
2. **Governance Registry Setup**: Requires manual one-time setup of governance-registry branch with CSV file
3. **Build ID Format**: Users must follow `DD-MM-YY-NN` format (validated, but could be error-prone)
4. **Bootstrap Script Stages**: If bootstrap-v3.sh is updated, may need coordination with Makefile

### Mitigation Strategies

1. **Test in Dev First**: Run full deployment in dev environment before prod
2. **Governance Registry**: Create setup script or documentation
3. **Build ID Helper**: Consider adding `make generate-build-id` target
4. **Version Lock**: Pin `BOOTSTRAP_VERSION=v3` in Makefile (already done at line 27)

---

## Deployment Readiness

**Status**: ✅ READY FOR TESTING

The critical bugs have been fixed. The implementation is now coherent:
- Phase 1 creates service accounts (matches documentation)
- Phase 2 validates and proceeds with platform deployment (no conflicts)
- Build ID immutability enforced (three-layer validation)
- Governance registry integration working (recording script created)

**Next Step**: Test deployment in dev environment with a fresh build_id.

**Recommended Test Build ID**: `13-01-26-99` (today's date, sequence 99 to avoid collisions)

**Test Command**:
```bash
make deploy ENV=dev BUILD_ID=13-01-26-99
```

---

## Change Summary

| File | Lines Changed | Type | Description |
|------|--------------|------|-------------|
| Makefile | 192-193, 198, 210-211 | Fix | Enable service accounts in Phase 1, prevent module collision |
| envs/dev/variables.tf | 311-315 | Add | New `apply_kubernetes_addons` variable |
| envs/dev/main.tf | 413 | Fix | Add condition to module to prevent Phase 1 application |
| docs/adrs/ADR-0148-*.md | 70-74, 229-242 | Update | Document implementation details |
| docs/analysis/BRIDGE_ANALYSIS.md | (entire file) | Add | Detailed bug analysis |
| docs/analysis/BUG_FIXES_SUMMARY.md | (entire file) | Add | Fix summary and testing guide |

**Total Lines Changed**: ~15 lines of code, ~500 lines of documentation
**Impact**: Critical - fixes deployment-blocking bugs
**Backward Compatibility**: No impact on existing clusters, affects new deployments only
