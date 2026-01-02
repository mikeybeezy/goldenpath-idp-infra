#!/usr/bin/env bash
set -euo pipefail

# Full bootstrap runner for a new EKS cluster.
# This orchestrates the repo bootstrap scripts in a safe, deterministic order.
# Usage:
#   bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh [<cluster-name> <region> [kong-namespace]]
#   If cluster/region are omitted, the script will try TF_DIR/terraform.tfvars.
#
# Optional cleanup mode:
#   CLEANUP_ON_FAILURE=true BUILD_ID=<id> DRY_RUN=false bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>
#
# Optional scale-down after bootstrap (Terraform required):
#   SCALE_DOWN_AFTER_BOOTSTRAP=true TF_DIR=goldenpath-idp-infra/envs/dev bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>
#
# Optional Terraform Kubernetes resources phase (Terraform required):
#   ENABLE_TF_K8S_RESOURCES=true TF_DIR=goldenpath-idp-infra/envs/dev bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh <cluster> <region>

cluster_name="${1:-}"
region="${2:-}"
kong_namespace="${3:-kong-system}"

script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "${script_root}" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${repo_root}" ]]; then
  repo_root="$(cd "${script_root}/../.." && pwd)"
fi

require_cmd() {
  if ! command -v "$1" >/dev/null; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

read_tfvars_var() {
  local tfvars_path="$1"
  local key="$2"
  if [[ -f "${tfvars_path}" ]]; then
    awk -F'=' -v k="${key}" '{
      key=$1; gsub(/[[:space:]]/,"",key);
      if (key == k) { val=$2; gsub(/"/,"",val); gsub(/[[:space:]]/,"",val); print val; exit }
    }' "${tfvars_path}"
  fi
}

tfvars_path=""
if [[ -n "${TFVARS_PATH:-}" ]]; then
  tfvars_path="${TFVARS_PATH}"
elif [[ -n "${TF_DIR:-}" ]]; then
  tfvars_path="${TF_DIR}/terraform.tfvars"
fi
if [[ -n "${tfvars_path}" && "${tfvars_path}" != /* ]]; then
  tfvars_path="${repo_root}/${tfvars_path}"
fi
if [[ -n "${tfvars_path}" && ! -f "${tfvars_path}" ]]; then
  echo "Expected terraform.tfvars at ${tfvars_path} but it was not found." >&2
  echo "Set TFVARS_PATH/TF_DIR correctly or provide the tfvars file before bootstrap." >&2
  exit 1
fi

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  if [[ -n "${TF_DIR:-}" ]]; then
    cluster_name="${cluster_name:-$(read_tfvars_var "${tfvars_path}" "cluster_name")}"
    region="${region:-$(read_tfvars_var "${tfvars_path}" "aws_region")}"
    region="${region:-$(read_tfvars_var "${tfvars_path}" "region")}"
  fi
fi

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster-name> <region> [kong-namespace]" >&2
  echo "Missing cluster_name/region and unable to read them from TF_DIR/terraform.tfvars." >&2
  exit 1
fi

# Determine storage add-on expectation (default: true).
storage_addons_enabled="${ENABLE_STORAGE_ADDONS:-}"
if [[ -z "${storage_addons_enabled}" && -n "${tfvars_path}" ]]; then
  storage_addons_enabled="$(read_tfvars_var "${tfvars_path}" "enable_storage_addons")"
fi
if [[ -z "${storage_addons_enabled}" ]]; then
  storage_addons_enabled="true"
fi

# Preflight checks for required CLIs.
require_cmd aws
require_cmd kubectl
require_cmd helm

stage_banner() {
  local title="$1"
  echo ""
  echo "##### ${title} #####"
  echo ""
}

stage_done() {
  local title="$1"
  echo ""
  echo "----- ${title} DONE -----"
}

run_cmd() {
  if [[ "${COMPACT_OUTPUT:-false}" == "true" ]]; then
    "$@" >/dev/null
  else
    "$@"
  fi
}

confirm_tf_apply() {
  local label="$1"
  if [[ "${CONFIRM_TF_APPLY:-false}" == "true" ]]; then
    return 0
  fi
  if [[ -t 0 ]]; then
    echo ""
    echo "Confirmation required: ${label}"
    echo "Type APPLY to proceed or anything else to cancel."
    read -r reply
    if [[ "${reply}" != "APPLY" ]]; then
      echo "Terraform apply cancelled." >&2
      exit 1
    fi
  else
    echo "Non-interactive shell; set CONFIRM_TF_APPLY=true to proceed." >&2
    exit 1
  fi
}

enable_tf_k8s_resources="${ENABLE_TF_K8S_RESOURCES:-true}"
scale_down_after_bootstrap="${SCALE_DOWN_AFTER_BOOTSTRAP:-false}"
min_ready_nodes="${MIN_READY_NODES:-3}"
if ! [[ "${min_ready_nodes}" =~ ^[0-9]+$ ]]; then
  echo "MIN_READY_NODES must be a number; got '${min_ready_nodes}'." >&2
  exit 1
fi

echo "Bootstrap starting for cluster ${cluster_name} in ${region}"

# Ensure kubeconfig is set for the target cluster.
stage_banner "STAGE 1: CLUSTER CONTEXT"
echo "Updating kubeconfig for ${cluster_name} (${region})..."
run_cmd aws eks update-kubeconfig --name "${cluster_name}" --region "${region}"
stage_done "STAGE 1"

# Verify tools and basic access.
stage_banner "STAGE 2: TOOL CHECKS"
echo "Checking required tools..."
run_cmd bash "${repo_root}/bootstrap/00_prereqs/00_check_tools.sh"
stage_done "STAGE 2"

# Preflight for node group creation (mandatory).
stage_banner "STAGE 3: EKS PREFLIGHT"
echo "Running EKS preflight..."
vpc_id="$(aws eks describe-cluster --name "${cluster_name}" --region "${region}" --query 'cluster.resourcesVpcConfig.vpcId' --output text)"
node_role_arn="$(aws iam get-role --role-name "${cluster_name}-node-role" --query 'Role.Arn' --output text)"
private_subnets="$(aws eks describe-cluster --name "${cluster_name}" --region "${region}" --query 'cluster.resourcesVpcConfig.subnetIds' --output text | tr '\t' ',')"
instance_type="${NODE_INSTANCE_TYPE:-}"
if [[ -z "${instance_type}" ]]; then
  echo "NODE_INSTANCE_TYPE is required for preflight (example: NODE_INSTANCE_TYPE=t2.small)." >&2
  exit 1
fi
run_cmd bash "${repo_root}/bootstrap/00_prereqs/10_eks_preflight.sh" "${cluster_name}" "${region}" "${vpc_id}" "${private_subnets}" "${node_role_arn}" "${instance_type}"
stage_done "STAGE 3"

# Ensure build_id is consistent between Makefile and Terraform inputs.
read_tfvars_build_id() {
  local tfvars_path="$1"
  if [[ -f "${tfvars_path}" ]]; then
    awk -F'=' '/^[[:space:]]*build_id[[:space:]]*=/{
      gsub(/"/,"",$2); gsub(/[[:space:]]/,"",$2); print $2; exit
    }' "${tfvars_path}"
  fi
}

effective_build_id() {
  if [[ -n "${TF_VAR_build_id:-}" ]]; then
    echo "${TF_VAR_build_id}"
    return
  fi
  if [[ -n "${tfvars_path}" ]]; then
    read_tfvars_build_id "${tfvars_path}"
    return
  fi
}

check_build_id_match() {
  local tf_build_id
  local make_build_id="${BUILD_ID:-}"
  tf_build_id="$(effective_build_id)"
  if [[ -n "${make_build_id}" && -z "${tf_build_id}" ]]; then
    echo "BUILD_ID mismatch detected." >&2
    echo "Make/ENV BUILD_ID: ${make_build_id}" >&2
    echo "Terraform build_id: <empty>" >&2
    echo "Set TF_VAR_build_id or terraform.tfvars to match BUILD_ID before running bootstrap." >&2
    exit 1
  fi
  if [[ -z "${make_build_id}" && -n "${tf_build_id}" ]]; then
    echo "BUILD_ID mismatch detected." >&2
    echo "Make/ENV BUILD_ID: <empty>" >&2
    echo "Terraform build_id: ${tf_build_id}" >&2
    echo "Set BUILD_ID to match TF_VAR_build_id/terraform.tfvars before running bootstrap." >&2
    exit 1
  fi
  if [[ -n "${make_build_id}" && -n "${tf_build_id}" && "${make_build_id}" != "${tf_build_id}" ]]; then
    echo "BUILD_ID mismatch detected." >&2
    echo "Make/ENV BUILD_ID: ${make_build_id}" >&2
    echo "Terraform build_id: ${tf_build_id}" >&2
    echo "Set TF_VAR_build_id or terraform.tfvars to match BUILD_ID before running bootstrap." >&2
    exit 1
  fi
}

irsa_plan_guard() {
  local plan_output
  local summary_line
  local add_count
  local change_count
  local destroy_count
  local tfvars_args=()

  if [[ -n "${tfvars_path}" ]]; then
    tfvars_args=(-var-file="${tfvars_path}")
  fi

  echo "Validating IRSA plan scope (service accounts only)..."
  plan_output="$(terraform -chdir="${TF_DIR}" plan -no-color \
    -var="enable_k8s_resources=false" \
    "${tfvars_args[@]}" \
    -target="kubernetes_service_account_v1.aws_load_balancer_controller[0]" \
    -target="kubernetes_service_account_v1.cluster_autoscaler[0]")"
  echo "${plan_output}"

  summary_line="$(echo "${plan_output}" | grep -m1 -E '^Plan:')"
  if [[ -z "${summary_line}" ]]; then
    echo "IRSA plan guard failed: plan summary not found." >&2
    exit 1
  fi

  if [[ "${summary_line}" =~ Plan:\ ([0-9]+)\ to\ add,\ ([0-9]+)\ to\ change,\ ([0-9]+)\ to\ destroy\. ]]; then
    add_count="${BASH_REMATCH[1]}"
    change_count="${BASH_REMATCH[2]}"
    destroy_count="${BASH_REMATCH[3]}"
  else
    echo "IRSA plan guard failed: unable to parse plan summary." >&2
    exit 1
  fi

  if [[ "${change_count}" -ne 0 || "${destroy_count}" -ne 0 || "${add_count}" -gt 2 ]]; then
    echo "IRSA plan guard failed: expected <= 2 adds and 0 change/destroy." >&2
    echo "Observed: ${summary_line}" >&2
    exit 1
  fi
}

stage_banner "MODE SUMMARY"
irsa_apply="no"
irsa_reason="ENABLE_TF_K8S_RESOURCES=false"
if [[ "${enable_tf_k8s_resources}" == "true" ]]; then
  if [[ -z "${TF_DIR:-}" ]]; then
    irsa_reason="TF_DIR not set (IRSA apply skipped)"
  else
    irsa_apply="yes"
    irsa_reason="targeted Terraform apply for IRSA service accounts"
  fi
fi
tf_build_id="$(effective_build_id)"
echo "IRSA apply: ${irsa_apply} (${irsa_reason})"
echo "Scale down after bootstrap: ${scale_down_after_bootstrap}"
echo "Minimum Ready nodes required: ${min_ready_nodes}"
echo "BUILD_ID (env): ${BUILD_ID:-<empty>}"
echo "build_id (Terraform): ${tf_build_id:-<empty>}"
if [[ "${CONFIRM_TF_APPLY:-false}" != "true" ]]; then
  echo "Terraform apply confirmation: required (set CONFIRM_TF_APPLY=true to skip)"
else
  echo "Terraform apply confirmation: skipped (CONFIRM_TF_APPLY=true)"
fi
stage_done "MODE SUMMARY"

# Ensure Terraform-managed Kubernetes resources only apply after kubeconfig is ready.
# Service accounts must exist before installing AWS LB Controller or Cluster Autoscaler.
stage_banner "STAGE 3B: SERVICE ACCOUNTS (IRSA)"
if [[ "${enable_tf_k8s_resources}" == "true" ]]; then
  if [[ -z "${TF_DIR:-}" ]]; then
    echo "ENABLE_TF_K8S_RESOURCES is true but TF_DIR is not set; skipping Terraform Kubernetes resources." >&2
  else
    if [[ -z "${tfvars_path}" ]]; then
      echo "TFVARS_PATH is required for IRSA apply (full config needed)." >&2
      exit 1
    fi
    check_build_id_match
    echo "About to run a targeted Terraform apply for IRSA service accounts."
    echo "This will update state in ${TF_DIR} and may create/update these resources:"
    echo "  - kubernetes_service_account_v1.aws_load_balancer_controller[0]"
    echo "  - kubernetes_service_account_v1.cluster_autoscaler[0]"
    irsa_plan_guard
    confirm_tf_apply "IRSA service account apply"
    echo "Applying Terraform Kubernetes service accounts in ${TF_DIR} (enable_k8s_resources=true)..."
    run_cmd terraform -chdir="${TF_DIR}" apply -auto-approve \
      -var-file="${tfvars_path}" \
      -var="enable_k8s_resources=true" \
      -target="kubernetes_service_account_v1.aws_load_balancer_controller[0]" \
      -target="kubernetes_service_account_v1.cluster_autoscaler[0]"
  fi
else
  echo "Skipping Terraform Kubernetes resources (ENABLE_TF_K8S_RESOURCES=${enable_tf_k8s_resources})."
  if ! kubectl -n kube-system get serviceaccount aws-load-balancer-controller >/dev/null 2>&1; then
    echo "ServiceAccount kube-system/aws-load-balancer-controller not found. Create it before installing the AWS Load Balancer Controller." >&2
    exit 1
  fi
  if ! kubectl -n kube-system get serviceaccount cluster-autoscaler >/dev/null 2>&1; then
    echo "ServiceAccount kube-system/cluster-autoscaler not found. Create it before installing Cluster Autoscaler." >&2
    exit 1
  fi
fi
stage_done "STAGE 3B"

# Preflight: ensure enough Ready nodes for a full bootstrap.
stage_banner "STAGE 4: CAPACITY CHECK"
echo "Checking Ready node count..."
ready_nodes="$(kubectl get nodes --no-headers 2>/dev/null | awk '$2 == "Ready" {count++} END {print count+0}')"
if [[ "${ready_nodes}" -lt "${min_ready_nodes}" ]]; then
  echo "Insufficient node capacity (${ready_nodes} Ready). Require ${min_ready_nodes}." >&2
  echo "Scale nodes before running full bootstrap." >&2
  exit 1
fi
stage_done "STAGE 4"

# Install Metrics Server early so autoscaler and scheduling checks work.
stage_banner "STAGE 5: METRICS SERVER"
echo "Installing Metrics Server..."
run_cmd bash "${repo_root}/bootstrap/50_smoke-tests/10_kubeconfig.sh" "${cluster_name}" "${region}"
stage_done "STAGE 5"

# Install Argo CD and (optionally) show admin access helper instructions.
stage_banner "STAGE 6: ARGO CD"
echo "INSTALLING Argo CD..."
run_cmd bash "${repo_root}/bootstrap/10_gitops-controller/10_argocd_helm.sh" "${cluster_name}" "${region}" "${repo_root}/gitops/helm/argocd/values/dev.yaml"
stage_done "STAGE 6"

# Validate core add-ons that are expected to exist.
stage_banner "STAGE 7: CORE ADD-ONS"
echo "INSTALLING AWS Load Balancer Controller..."
run_cmd bash "${repo_root}/bootstrap/30_core-addons/10_aws_lb_controller.sh" "${cluster_name}" "${region}" "${vpc_id}"
if [[ "${SKIP_CERT_MANAGER_VALIDATION:-true}" == "true" ]]; then
  echo "Skipping cert-manager validation; Argo apps may not be synced yet."
else
  echo "VALIDATING cert-manager..."
  run_cmd bash "${repo_root}/bootstrap/30_core-addons/20_cert_manager.sh" "${cluster_name}" "${region}"
fi
stage_done "STAGE 7"

# Validate storage add-ons when required.
stage_banner "STAGE 7B: STORAGE ADD-ONS"
if [[ "${storage_addons_enabled}" == "true" ]]; then
  for addon in aws-ebs-csi-driver aws-efs-csi-driver snapshot-controller; do
    status="$(aws eks describe-addon \
      --cluster-name "${cluster_name}" \
      --region "${region}" \
      --addon-name "${addon}" \
      --query 'addon.status' \
      --output text 2>/dev/null || true)"
    if [[ "${status}" != "ACTIVE" ]]; then
      echo "Storage add-on ${addon} is not Active (status=${status})." >&2
      echo "Enable storage add-ons or set ENABLE_STORAGE_ADDONS=false to skip this check." >&2
      exit 1
    fi
    echo "Storage add-on ${addon} is Active."
  done
else
  echo "Storage add-ons disabled; skipping validation."
fi
stage_done "STAGE 7B"

# Apply Cluster Autoscaler first so capacity is stable before Kong.
stage_banner "STAGE 8: AUTOSCALER APP"
env_name="${ENV_NAME:-dev}"
autoscaler_app="${env_name}-cluster-autoscaler"
echo "INSTALLING Cluster Autoscaler app for ${env_name}..."
run_cmd kubectl apply -f "${repo_root}/gitops/argocd/apps/${env_name}/cluster-autoscaler.yaml"
autoscaler_cluster_name="${cluster_name}"
autoscaler_patch="$(printf '[{"op":"add","path":"/spec/sources/0/helm/parameters","value":[{"name":"autoDiscovery.clusterName","value":"%s"}]}]' "${autoscaler_cluster_name}")"
run_cmd kubectl -n argocd patch application "${autoscaler_app}" --type=json -p "${autoscaler_patch}"
stage_done "STAGE 8"

# Optionally wait for the Cluster Autoscaler Argo app to sync before installing Kong.
if [[ "${SKIP_ARGO_SYNC_WAIT:-true}" == "true" ]]; then
  echo "Skipping Argo CD sync wait (SKIP_ARGO_SYNC_WAIT=true)."
else
  if kubectl -n argocd get application "${autoscaler_app}" >/dev/null 2>&1; then
    echo "Waiting for Argo CD app ${autoscaler_app} to sync..."
    run_cmd kubectl -n argocd wait --for=condition=Synced "application/${autoscaler_app}" --timeout=300s
    run_cmd kubectl -n argocd wait --for=condition=Healthy "application/${autoscaler_app}" --timeout=300s
  else
    echo "Cluster Autoscaler app ${autoscaler_app} not found in Argo CD. Ensure the app manifests are applied." >&2
    exit 1
  fi
fi

# Ensure Cluster Autoscaler is running before installing Kong.
stage_banner "STAGE 9: AUTOSCALER READY"
echo "Checking Cluster Autoscaler rollout..."
run_cmd kubectl -n kube-system rollout status deployment/cluster-autoscaler --timeout=180s || \
  echo "Warning: cluster-autoscaler deployment not ready yet."
stage_done "STAGE 9"

# Apply remaining platform apps (excluding Kong and Autoscaler).
stage_banner "STAGE 10: PLATFORM APPS"
echo "INSTALLING remaining Argo apps for ${env_name}..."
EXCLUDE_APPS="cluster-autoscaler,kong" run_cmd bash "${repo_root}/bootstrap/40_platform-tooling/10_argocd_apps.sh" "${env_name}"
stage_done "STAGE 10"

# Validate Kong ingress after autoscaler and core apps are in place.
stage_banner "STAGE 11: KONG"
echo "INSTALLING Kong app for ${env_name}..."
run_cmd kubectl apply -f "${repo_root}/gitops/argocd/apps/${env_name}/kong.yaml"
echo "VALIDATING Kong ingress..."
run_cmd bash "${repo_root}/bootstrap/40_platform-tooling/20_kong_ingress.sh" "${cluster_name}" "${region}" "${kong_namespace}"
stage_done "STAGE 11"

# Post-bootstrap audit output.
stage_banner "STAGE 12: AUDIT"
echo "Running audit checks..."
run_cmd bash "${repo_root}/bootstrap/50_smoke-tests/20_audit.sh" "${cluster_name}" "${region}"
stage_done "STAGE 12"

# Optional: scale down after bootstrap by re-applying Terraform with bootstrap_mode=false.
stage_banner "STAGE 13: OPTIONAL SCALE DOWN"
if [[ "${scale_down_after_bootstrap}" == "true" ]]; then
  if [[ -z "${TF_DIR:-}" ]]; then
    echo "SCALE_DOWN_AFTER_BOOTSTRAP is true but TF_DIR is not set." >&2
    exit 1
  fi
  echo "About to run Terraform apply to set bootstrap_mode=false in ${TF_DIR}."
  echo "This may reduce node capacity and related resources."
  confirm_tf_apply "Scale down apply"
  echo "Scaling down via Terraform (bootstrap_mode=false) in ${TF_DIR}"
  tf_auto_approve_flag=""
  if [[ "${TF_AUTO_APPROVE:-false}" == "true" ]]; then
    tf_auto_approve_flag="-auto-approve"
  fi
  run_cmd terraform -chdir="${TF_DIR}" apply ${tf_auto_approve_flag} -var="bootstrap_mode=false"
  stage_done "STAGE 13"
else
  echo "Skipping scale down (SCALE_DOWN_AFTER_BOOTSTRAP=false)."
  stage_done "STAGE 13"
fi

stage_banner "STAGE 14: BOOTSTRAP COMPLETE"
cat <<NOTE
Bootstrap complete.
Sanity checks:
  kubectl get nodes
  kubectl top nodes
  kubectl -n argocd get applications
  kubectl -n ${kong_namespace} get svc
NOTE

cat <<EXPLAIN
What these checks mean:
  - kubectl get nodes: all nodes should be Ready (cluster can schedule).
  - kubectl top nodes: metrics-server is working and reporting usage.
  - argocd applications: apps show Synced/Healthy (GitOps reconciled).
  - kong-system services: Kong has a LoadBalancer hostname/EXTERNAL-IP.

If any check fails, the platform is not fully ready yet.
EXPLAIN

echo "kubectl get nodes"
kubectl get nodes
echo ""
echo "kubectl top nodes"
kubectl top nodes
echo ""
echo "kubectl -n argocd get applications"
kubectl -n argocd get applications
echo ""
echo "kubectl -n ${kong_namespace} get svc"
kubectl -n "${kong_namespace}" get svc

# Checklist to confirm the platform is usable.
stage_done "STAGE 14"

stage_banner "STAGE 15: SANITY CHECKS"
cat "${repo_root}/bootstrap/50_smoke-tests/30_dev_baseline_checklist.md"
stage_done "STAGE 15"

# Surface Argo CD app status at the end for manual review.
kubectl -n argocd get applications \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status,MESSAGE:.status.health.message

# Remind users to validate app behavior independently.
echo ""
echo ""
echo "NOTE: Argo CD status is not a full validation. Check critical apps independently."

# Flag apps with unknown health to reduce ambiguity.
if kubectl -n argocd get applications \
  -o custom-columns=NAME:.metadata.name,HEALTH:.status.health.status --no-headers | \
  awk '$2 == "Unknown" {print}' | grep -q .; then
  echo "Warning: Some Argo CD apps report HEALTH=Unknown. Review the status above." >&2
fi
