#!/usr/bin/env bash
set -euo pipefail

# Full bootstrap runner for a new EKS cluster.
# This orchestrates the repo bootstrap scripts in a safe, deterministic order.
# Usage:
#   bootstrap-scripts/helm-bootstrap.sh <cluster-name> <region> [kong-namespace]
#
# Optional cleanup mode:
#   CLEANUP_ON_FAILURE=true BUILD_ID=<id> DRY_RUN=false bootstrap-scripts/cleanup-orphans.sh <build-id> <region>
#
# Optional scale-down after bootstrap (Terraform required):
#   SCALE_DOWN_AFTER_BOOTSTRAP=true TF_DIR=goldenpath-idp-infra/envs/dev bash bootstrap-scripts/helm-bootstrap.sh <cluster> <region>

cluster_name="${1:-}"
region="${2:-}"
kong_namespace="${3:-kong}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster-name> <region> [kong-namespace]" >&2
  exit 1
fi

script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_root}/.." && pwd)"

require_cmd() {
  if ! command -v "$1" >/dev/null; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

# Preflight checks for required CLIs.
require_cmd aws
require_cmd kubectl
require_cmd helm

echo "Bootstrap starting for cluster ${cluster_name} in ${region}"

# Ensure kubeconfig is set for the target cluster.
aws eks update-kubeconfig --name "${cluster_name}" --region "${region}"

# Verify tools and basic access.
bash "${repo_root}/bootstrap/00_prereqs/00_check_tools.sh"

# Preflight for node group creation (mandatory).
vpc_id="$(aws eks describe-cluster --name "${cluster_name}" --region "${region}" --query 'cluster.resourcesVpcConfig.vpcId' --output text)"
node_role_arn="$(aws iam get-role --role-name "${cluster_name}-node-role" --query 'Role.Arn' --output text)"
private_subnets="$(aws eks describe-cluster --name "${cluster_name}" --region "${region}" --query 'cluster.resourcesVpcConfig.subnetIds' --output text | tr '\t' ',')"
instance_type="${NODE_INSTANCE_TYPE:-}"
if [[ -z "${instance_type}" ]]; then
  echo "NODE_INSTANCE_TYPE is required for preflight (example: NODE_INSTANCE_TYPE=t2.small)." >&2
  exit 1
fi
bash "${repo_root}/bootstrap/00_prereqs/10_eks_preflight.sh" "${cluster_name}" "${region}" "${vpc_id}" "${private_subnets}" "${node_role_arn}" "${instance_type}"

# Preflight: ensure enough Ready nodes for a full bootstrap.
ready_nodes="$(kubectl get nodes --no-headers 2>/dev/null | awk '$2 == "Ready" {count++} END {print count+0}')"
if [[ "${ready_nodes}" -lt 3 ]]; then
  echo "Insufficient node capacity (${ready_nodes} Ready). Enable bootstrap_mode or scale nodes before running full bootstrap." >&2
  exit 1
fi

# Install Argo CD and (optionally) show admin access helper instructions.
bash "${repo_root}/bootstrap/10_gitops-controller/10_argocd_helm.sh" "${cluster_name}" "${region}" "${repo_root}/gitops/helm/argocd/values/dev.yaml"

# Validate core add-ons that are expected to exist.
bash "${repo_root}/bootstrap/20_core-addons/10_aws_lb_controller.sh" "${cluster_name}" "${region}" "${vpc_id}"
bash "${repo_root}/bootstrap/20_core-addons/20_cert_manager.sh" "${cluster_name}" "${region}"

# Apply platform tooling via Argo CD.
bash "${repo_root}/bootstrap/30_platform-tooling/10_argocd_apps.sh"
bash "${repo_root}/bootstrap/30_platform-tooling/20_kong_ingress.sh" "${cluster_name}" "${region}" "${kong_namespace}"

# Post-bootstrap sanity checks and audit output.
bash "${repo_root}/bootstrap/40_smoke-tests/10_kubeconfig.sh" "${cluster_name}" "${region}"
bash "${repo_root}/bootstrap/40_smoke-tests/20_audit.sh"

# Optional: scale down after bootstrap by re-applying Terraform with bootstrap_mode=false.
if [[ "${SCALE_DOWN_AFTER_BOOTSTRAP:-false}" == "true" ]]; then
  if [[ -z "${TF_DIR:-}" ]]; then
    echo "SCALE_DOWN_AFTER_BOOTSTRAP is true but TF_DIR is not set." >&2
    exit 1
  fi
  echo "Scaling down via Terraform (bootstrap_mode=false) in ${TF_DIR}"
  terraform -chdir="${TF_DIR}" apply -var="bootstrap_mode=false"
fi

cat <<NOTE
Bootstrap complete.
Sanity checks:
  kubectl get nodes
  kubectl top nodes
  kubectl -n argocd get applications
  kubectl -n ${kong_namespace} get svc
NOTE
