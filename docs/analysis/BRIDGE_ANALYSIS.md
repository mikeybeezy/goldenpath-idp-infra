---
id: BRIDGE_ANALYSIS
title: 'Bridge Analysis: Infrastructure to Bootstrap'
type: documentation
---

# Bridge Analysis: Infrastructure to Bootstrap

**Date**: 2026-01-13
**Status**: CRITICAL BUGS FOUND
**Analyst**: Claude Code

## Executive Summary

The bridge between Phase 1 (infrastructure) and Phase 2 (bootstrap) has **critical inconsistencies** that will cause deployment failures. The implementation assumes service accounts are created in Phase 1, but the current configuration prevents this.

---

## How The Bridge Should Work

### Phase 1: Infrastructure (Terraform Apply)
**Command**: `make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-03`

**Terraform Variables Set**:
```bash
-var="build_id=$(BUILD_ID)"
-var="enable_k8s_resources=false"  # ⚠️ THIS IS THE PROBLEM
```

**Expected Outcomes**:
1. VPC, Subnets, NAT Gateway, Route Tables
2. EKS Cluster
3. EKS Node Group
4. IAM Roles (cluster, nodes, IRSA roles for LB Controller, Autoscaler, ESO)
5. **Service Accounts** (aws-load-balancer-controller, cluster-autoscaler, external-secrets)

### Phase 2: Bootstrap (Shell Script)
**Command**: `make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-03`

**Environment Variables Set**:
```bash
ENABLE_TF_K8S_RESOURCES=true  # Tells script that service accounts should already exist
TF_DIR=$(ENV_DIR)
```

**Bootstrap Script Stage 3B Validation** (lines 273-283):
```bash
stage_banner "STAGE 3B: SERVICE ACCOUNTS (IRSA)"
echo "Skipping Terraform IRSA apply in v3; validating existing service accounts only."

if ! kubectl -n kube-system get serviceaccount aws-load-balancer-controller >/dev/null 2>&1; then
  echo "ServiceAccount kube-system/aws-load-balancer-controller not found." >&2
  exit 1
fi

if ! kubectl -n kube-system get serviceaccount cluster-autoscaler >/dev/null 2>&1; then
  echo "ServiceAccount kube-system/cluster-autoscaler not found." >&2
  exit 1
fi
```

**Expected Behavior**: Script validates that service accounts created in Phase 1 exist, then proceeds to install Helm charts that reference them.

---

## Critical Bug #1: Service Accounts Won't Be Created in Phase 1

### Root Cause

**File**: `envs/dev/main.tf` (lines 345-379)

```hcl
resource "kubernetes_service_account_v1" "aws_load_balancer_controller" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_lb_controller_role ? 1 : 0
  #                                  ^^^^^^^^^^^^^^^^^^^^^^
  #                                  THIS WILL BE FALSE IN PHASE 1

  metadata {
    name      = var.iam_config.lb_controller_service_account_name
    namespace = var.iam_config.lb_controller_service_account_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = module.iam[0].lb_controller_role_arn
    }
  }
}

resource "kubernetes_service_account_v1" "cluster_autoscaler" {
  count = var.eks_config.enabled && var.enable_k8s_resources && var.iam_config.enabled && var.iam_config.enable_autoscaler_role ? 1 : 0
  #                                  ^^^^^^^^^^^^^^^^^^^^^^
  #                                  THIS WILL BE FALSE IN PHASE 1
}
```

### The Problem

**Phase 1 sets**: `-var="enable_k8s_resources=false"`
**Condition requires**: `var.enable_k8s_resources == true`
**Result**: `count = 0` → Service accounts NOT created

**Phase 2 expects**: Service accounts to already exist
**Actual state**: Service accounts don't exist
**Result**: Bootstrap fails at Stage 3B with error:
```
ServiceAccount kube-system/aws-load-balancer-controller not found.
Create it before installing the AWS Load Balancer Controller.
```

---

## Critical Bug #2: Conflicting Documentation

### ADR-0148 States (lines 60-72):

```
#### Phase 1: Infrastructure (Terraform)

**Scope**: AWS resources only
- VPC, Subnets, Security Groups
- EKS Cluster
- IAM Roles (cluster, nodes, IRSA)
- Service Accounts (with IRSA annotations)  # ⚠️ CLAIMS SERVICE ACCOUNTS INCLUDED

**Command**: `make _phase1-infrastructure`

**Key characteristic**: No Helm releases, no ArgoCD Applications
```

But the Makefile sets `enable_k8s_resources=false`, which prevents service accounts from being created!

### Changelog CL-0121 States (lines 22-25):

```
Behind the scenes orchestrates:
1. Phase 1: Terraform infrastructure (VPC, EKS, IAM, Service Accounts)
2. Phase 2: Platform bootstrap (ArgoCD, controllers, applications)
```

Again claims service accounts are in Phase 1, but implementation contradicts this.

---

## Critical Bug #3: Bootstrap Script v3 Change

### bootstrap-v2.sh Behavior (lines 275-294):

```bash
stage_banner "STAGE 3B: SERVICE ACCOUNTS (IRSA)"
if [[ "${enable_tf_k8s_resources}" == "true" ]]; then
  if [[ -z "${TF_DIR:-}" ]]; then
    echo "ENABLE_TF_K8S_RESOURCES is true but TF_DIR is not set; skipping Terraform Kubernetes resources." >&2
  else
    check_build_id_match
    echo "About to run a targeted Terraform apply for IRSA service accounts."
    run_cmd terraform -chdir="${TF_DIR}" apply -auto-approve \
      -var-file="${tfvars_path}" \
      -var="enable_k8s_resources=true" \
      -target="kubernetes_service_account_v1.aws_load_balancer_controller[0]" \
      -target="kubernetes_service_account_v1.cluster_autoscaler[0]"
  fi
fi
```

**v2 behavior**: If `ENABLE_TF_K8S_RESOURCES=true`, the bootstrap script CREATES the service accounts via targeted terraform apply.

### bootstrap-v3.sh Behavior (lines 273-283):

```bash
stage_banner "STAGE 3B: SERVICE ACCOUNTS (IRSA)"
echo "Skipping Terraform IRSA apply in v3; validating existing service accounts only."
if ! kubectl -n kube-system get serviceaccount aws-load-balancer-controller >/dev/null 2>&1; then
  echo "ServiceAccount kube-system/aws-load-balancer-controller not found." >&2
  exit 1
fi
```

**v3 behavior**: Assumes service accounts already exist, only validates. Does NOT create them.

### The Disconnect

- **Makefile Phase 2** sets `ENABLE_TF_K8S_RESOURCES=true`
- **Makefile Phase 2** uses `BOOTSTRAP_VERSION=v3` (default)
- **bootstrap-v3.sh** does NOT create service accounts when `ENABLE_TF_K8S_RESOURCES=true`
- **bootstrap-v3.sh** only VALIDATES that service accounts exist

This is a breaking change from v2 → v3 that was not accounted for in the seamless deployment design.

---

## Root Cause Analysis

### Timeline of Changes

1. **Development Branch (Original)**:
   - Manual two-phase: `terraform apply` → `bash bootstrap-v3.sh`
   - Users would run: `terraform apply` (which includes `-var="enable_k8s_resources=true"` by default)
   - This created service accounts during terraform apply
   - Then users would manually run bootstrap script

2. **eks-single-build-refactor Branch (Rejected)**:
   - Tried to consolidate everything into single terraform apply
   - Introduced circular dependencies
   - Not merged

3. **feature/seamless-build-deployment Branch (Current)**:
   - Attempted to maintain two-phase pattern
   - Added seamless `make deploy` orchestration
   - **MISTAKE**: Set `enable_k8s_resources=false` in Phase 1 to avoid kubernetes_addons circular dependency
   - **MISTAKE**: Didn't realize bootstrap-v3 expects service accounts to pre-exist
   - **MISTAKE**: Documentation claims service accounts created in Phase 1, but code doesn't do this

### Why This Wasn't Caught

1. **Never tested end-to-end** - Implementation completed but not run
2. **Assumed v3 behavior matched v2** - Didn't read bootstrap-v3.sh Stage 3B carefully
3. **Documentation written before code review** - ADR/Changelog described intended behavior, not actual behavior

---

## Impact Assessment

### Severity: CRITICAL

**Deployment will fail 100% of the time** with error:
```
STAGE 3B: SERVICE ACCOUNTS (IRSA)
Skipping Terraform IRSA apply in v3; validating existing service accounts only.
ServiceAccount kube-system/aws-load-balancer-controller not found.
Create it before installing the AWS Load Balancer Controller.
```

### Affected Commands

- `make deploy ENV=dev BUILD_ID=13-01-26-03` - **WILL FAIL**
- `make _phase1-infrastructure` + `make _phase2-bootstrap` - **WILL FAIL**

### When It Fails

- Phase 1 completes successfully (infra created, service accounts NOT created)
- Phase 2 starts bootstrap-v3.sh
- Stage 3B validation fails immediately
- Entire deployment aborts

---

## Solution Options

### Option A: Create Service Accounts in Phase 1 (Recommended)

**Change Phase 1 to set `enable_k8s_resources=true`**

#### Pros:
- Matches documentation (ADR, Changelog)
- Service accounts created with infrastructure
- Bootstrap script validation passes
- Aligns with original development branch pattern

#### Cons:
- Must ensure kubernetes_addons module doesn't apply in Phase 1
- Need to verify no circular dependencies

#### Implementation:

**File**: `Makefile` (line 192)

```diff
_phase1-infrastructure:
	$(call require_build_id)
	@echo " Phase 1: Building infrastructure..."
	@mkdir -p logs/build-timings
	@bash -c 'set -e; \
	log="logs/build-timings/terraform-apply-$(ENV)-$(CLUSTER)-$(BUILD_ID)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Infrastructure apply output streaming; full log at $$log"; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply \
		-var="build_id=$(BUILD_ID)" \
-		-var="enable_k8s_resources=false" \
+		-var="enable_k8s_resources=true" \
		-auto-approve 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'
	@bash scripts/record-build-timing.sh $(ENV) $(BUILD_ID) terraform-apply
	@echo "✅ Infrastructure ready"
```

**Verification Required**:
1. Ensure `kubernetes_addons` module is controlled separately
2. Check if module has `count` condition that prevents Phase 1 application
3. Test that service accounts create without triggering module

**File to Check**: `envs/dev/main.tf` (around line 405-430)

```hcl
module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0
  #                                  ^^^^^^^^^^^^^^^^^^^^^^
  # Need to add additional condition to prevent Phase 1 application
```

**Potential Fix**:
```hcl
module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled && var.enable_k8s_resources && var.apply_kubernetes_addons ? 1 : 0
  #                                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  # New variable to control when module applies
```

Add to `variables.tf`:
```hcl
variable "apply_kubernetes_addons" {
  type        = bool
  description = "Whether to apply the kubernetes_addons module (ArgoCD, LB Controller Helm charts). Set to false in Phase 1, true in Phase 2."
  default     = false
}
```

Update `_phase1-infrastructure`:
```bash
-var="enable_k8s_resources=true" \
-var="apply_kubernetes_addons=false" \
```

Update `_phase2-bootstrap`:
```bash
# In bootstrap script, run targeted terraform apply with:
terraform -chdir="${TF_DIR}" apply -auto-approve \
  -var-file="${tfvars_path}" \
  -var="enable_k8s_resources=true" \
  -var="apply_kubernetes_addons=true"
```

---

### Option B: Modify bootstrap-v3 to Create Service Accounts

**Revert bootstrap-v3 Stage 3B to v2 behavior**

#### Pros:
- No changes to Makefile Phase 1
- Keeps `enable_k8s_resources=false` in Phase 1 as intended
- Bootstrap script creates service accounts dynamically

#### Cons:
- Bootstrap script runs terraform apply (mixing concerns)
- Requires TF_DIR to be set (already done)
- Service accounts created in Phase 2 instead of Phase 1 (contradicts docs)

#### Implementation:

**File**: `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh` (lines 273-283)

```diff
stage_banner "STAGE 3B: SERVICE ACCOUNTS (IRSA)"
-echo "Skipping Terraform IRSA apply in v3; validating existing service accounts only."
-if ! kubectl -n kube-system get serviceaccount aws-load-balancer-controller >/dev/null 2>&1; then
-  echo "ServiceAccount kube-system/aws-load-balancer-controller not found." >&2
-  exit 1
-fi
-if ! kubectl -n kube-system get serviceaccount cluster-autoscaler >/dev/null 2>&1; then
-  echo "ServiceAccount kube-system/cluster-autoscaler not found." >&2
-  exit 1
-fi
+if [[ "${enable_tf_k8s_resources}" == "true" ]]; then
+  if [[ -z "${TF_DIR:-}" ]]; then
+    echo "ENABLE_TF_K8S_RESOURCES is true but TF_DIR is not set; skipping service account creation." >&2
+    exit 1
+  else
+    check_build_id_match
+    echo "Creating service accounts via targeted Terraform apply..."
+    irsa_plan_guard
+    run_cmd terraform -chdir="${TF_DIR}" apply -auto-approve \
+      -var-file="${tfvars_path}" \
+      -var="enable_k8s_resources=true" \
+      -target="kubernetes_service_account_v1.aws_load_balancer_controller[0]" \
+      -target="kubernetes_service_account_v1.cluster_autoscaler[0]"
+  fi
+else
+  echo "Validating service accounts exist (ENABLE_TF_K8S_RESOURCES=false mode)..."
+  if ! kubectl -n kube-system get serviceaccount aws-load-balancer-controller >/dev/null 2>&1; then
+    echo "ServiceAccount kube-system/aws-load-balancer-controller not found." >&2
+    exit 1
+  fi
+  if ! kubectl -n kube-system get serviceaccount cluster-autoscaler >/dev/null 2>&1; then
+    echo "ServiceAccount kube-system/cluster-autoscaler not found." >&2
+    exit 1
+  fi
+fi
```

**Requires updating documentation** to reflect that service accounts created in Phase 2.

---

### Option C: Use Targeted Apply in Phase 1

**Add targeted terraform apply for service accounts only in Phase 1**

#### Pros:
- Service accounts created in Phase 1 (matches docs)
- Keeps `enable_k8s_resources=false` for safety
- Explicit control over what applies when

#### Cons:
- More complex Makefile logic
- Two terraform applies in Phase 1 (infrastructure + service accounts)

#### Implementation:

**File**: `Makefile` (_phase1-infrastructure target)

```bash
_phase1-infrastructure:
	$(call require_build_id)
	@echo " Phase 1: Building infrastructure..."
	@mkdir -p logs/build-timings

	# Step 1: Infrastructure (enable_k8s_resources=false)
	@bash -c 'set -e; \
	log="logs/build-timings/terraform-apply-infra-$(ENV)-$(CLUSTER)-$(BUILD_ID)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Infrastructure apply (AWS resources only)..."; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply \
		-var="build_id=$(BUILD_ID)" \
		-var="enable_k8s_resources=false" \
		-auto-approve 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

	# Step 2: Service Accounts (enable_k8s_resources=true, targeted)
	@bash -c 'set -e; \
	log="logs/build-timings/terraform-apply-sa-$(ENV)-$(CLUSTER)-$(BUILD_ID)-$$(date -u +%Y%m%dT%H%M%SZ).log"; \
	echo "Service accounts apply (targeted)..."; \
	$(TF_BIN) -chdir=$(ENV_DIR) apply \
		-var="build_id=$(BUILD_ID)" \
		-var="enable_k8s_resources=true" \
		-target="kubernetes_service_account_v1.aws_load_balancer_controller[0]" \
		-target="kubernetes_service_account_v1.cluster_autoscaler[0]" \
		-target="kubernetes_service_account_v1.external_secrets[0]" \
		-auto-approve 2>&1 | tee "$$log"; \
	exit $${PIPESTATUS[0]}; \
	'

	@bash scripts/record-build-timing.sh $(ENV) $(BUILD_ID) terraform-apply
	@echo "✅ Infrastructure ready (including service accounts)"
```

---

## Secondary Issues Found

### Issue #1: Module Dependency Conflict

**File**: `envs/dev/main.tf` (lines 405-430)

```hcl
module "kubernetes_addons" {
  source = "../../modules/kubernetes_addons"
  count  = var.eks_config.enabled && var.enable_k8s_resources ? 1 : 0

  # Module deploys:
  # - ArgoCD (Helm)
  # - AWS Load Balancer Controller (Helm)
  # - bootstrap-apps (Helm chart that applies ArgoCD Applications)

  depends_on = [
    module.eks,
    kubernetes_service_account_v1.aws_load_balancer_controller,
    aws_eks_access_policy_association.terraform_admin
  ]
}
```

**Problem**: If `enable_k8s_resources=true` in Phase 1, this module will try to apply, which includes:
- Installing ArgoCD via Helm
- Installing LB Controller via Helm
- Applying ArgoCD Applications via bootstrap-apps Helm chart

This overlaps with what the bootstrap script does in Phase 2!

**Conflict**:
- `kubernetes_addons` module (line 10) installs ArgoCD via Helm
- `bootstrap-v3.sh` Stage 6 (line 305) installs ArgoCD via bash script

Both will try to install ArgoCD, causing collision.

### Issue #2: Bootstrap Script Stage 6 Redundancy

**File**: `bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh` (lines 303-306)

```bash
stage_banner "STAGE 6: ARGO CD"
echo "INSTALLING Argo CD..."
run_cmd bash "${repo_root}/bootstrap/10_gitops-controller/10_argocd_helm.sh" "${cluster_name}" "${region}" "${repo_root}/gitops/helm/argocd/values/dev.yaml"
stage_done "STAGE 6"
```

**Also**: `kubernetes_addons` module (modules/kubernetes_addons/main.tf lines 10-31) installs ArgoCD.

**Problem**: Two different installation methods for same component.

### Issue #3: Missing CONFIRM_TF_APPLY in Phase 2

**File**: `Makefile` (_phase2-bootstrap target, line 209)

```bash
ENABLE_TF_K8S_RESOURCES=true \
TF_DIR=$(ENV_DIR) \
bash $(BOOTSTRAP_SCRIPT) $(CLUSTER) $(REGION) $(KONG_NAMESPACE)
```

**Missing**: `CONFIRM_TF_APPLY=true`

**Impact**: If bootstrap-v3 is modified to apply service accounts (Option B), it will prompt for confirmation in non-interactive mode and fail.

**Fix**: Add `CONFIRM_TF_APPLY=true \` to the environment variables.

---

## Recommendation

**Implement Option A with Additional Safety**:

1. **Add `apply_kubernetes_addons` variable** to control module application independently
2. **Set `enable_k8s_resources=true`** in Phase 1 (creates service accounts)
3. **Set `apply_kubernetes_addons=false`** in Phase 1 (prevents Helm releases)
4. **Keep bootstrap-v3 validation-only** for service accounts
5. **Remove ArgoCD installation from kubernetes_addons module** (let bootstrap script handle it)
6. **Update documentation** to reflect accurate behavior

### Why This Is Best

1. **Service accounts in Phase 1** (infrastructure layer) ✅
2. **Platform components in Phase 2** (bootstrap layer) ✅
3. **No terraform in bootstrap script** (clean separation) ✅
4. **No ArgoCD duplication** (single installation path) ✅
5. **Matches documentation intent** ✅
6. **Clear phase boundaries** ✅

---

## Testing Plan

Before deployment, test each phase independently:

### Test 1: Phase 1 Alone
```bash
make _phase1-infrastructure ENV=dev BUILD_ID=13-01-26-99
```

**Expected**:
- VPC, EKS, IAM created
- Service accounts created
- `kubectl get sa -n kube-system` shows aws-load-balancer-controller, cluster-autoscaler
- NO Helm releases present
- NO ArgoCD installed

### Test 2: Phase 2 After Phase 1
```bash
make _phase2-bootstrap ENV=dev BUILD_ID=13-01-26-99
```

**Expected**:
- Stage 3B validation passes (service accounts found)
- ArgoCD installed
- LB Controller installed
- Cluster Autoscaler ArgoCD app applied
- All workloads healthy

### Test 3: Full Deploy
```bash
make deploy ENV=dev BUILD_ID=13-01-26-98
```

**Expected**:
- Both phases complete successfully
- Phase 3 verification passes
- Governance registry updated with build timing

---

## Conclusion

The current implementation has a **critical bug** that prevents any deployment from succeeding. Service accounts are expected in Phase 2 but never created in Phase 1. Three viable solutions exist, with Option A (create service accounts in Phase 1 with additional safety) being the recommended approach. Additional issues around module duplication and Helm chart conflicts must also be addressed.

**Status**: Implementation is NOT production-ready. Requires fixes before testing.
