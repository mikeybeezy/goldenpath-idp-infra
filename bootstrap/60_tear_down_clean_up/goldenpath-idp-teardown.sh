#!/usr/bin/env bash
set -euo pipefail

# Teardown runner for EKS clusters created by this repo.
# Usage:
#   bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh <cluster-name> <region>
#
# Required confirmation:
#   TEARDOWN_CONFIRM=true
#
# Optional flags:
#   SKIP_DRAIN_NODEGROUPS=true
#   DELETE_NODEGROUPS=true|false (default true)
#   WAIT_FOR_NODEGROUP_DELETE=true|false (default true)
#   DELETE_CLUSTER=true|false (default true, ignored when TF_DIR is set)
#   LB_CLEANUP_ATTEMPTS=<count> (default 5)
#   LB_CLEANUP_INTERVAL=<seconds> (default 20)
#   TF_DIR=<path> (if set, run terraform destroy instead of aws eks delete-cluster)
#   TF_AUTO_APPROVE=true (use -auto-approve with terraform destroy)
#   REMOVE_K8S_SA_FROM_STATE=true|false (default true)
#   CLEANUP_ORPHANS=true BUILD_ID=<id> (run cleanup-orphans after teardown)

cluster_name="${1:-}"
region="${2:-}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster-name> <region>" >&2
  exit 1
fi

if [[ "${TEARDOWN_CONFIRM:-false}" != "true" ]]; then
  echo "Set TEARDOWN_CONFIRM=true to run destructive teardown steps." >&2
  exit 1
fi

require_cmd() {
  if ! command -v "$1" >/dev/null; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd aws
require_cmd kubectl
require_cmd date

script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "${script_root}" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${repo_root}" ]]; then
  repo_root="$(cd "${script_root}/../.." && pwd)"
fi

if [[ -n "${TF_DIR:-}" && "${TF_DIR}" != /* ]]; then
  TF_DIR="${repo_root}/${TF_DIR}"
fi

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
  "$@"
}

run_with_heartbeat() {
  local label="$1"
  shift
  local interval="${HEARTBEAT_INTERVAL:-30}"

  echo "${label} (heartbeat every ${interval}s)..."
  "$@" &
  local cmd_pid=$!

  while kill -0 "${cmd_pid}" >/dev/null 2>&1; do
    echo "  still in progress... $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    sleep "${interval}"
  done

  wait "${cmd_pid}"
}

ensure_kube_access() {
  if ! kubectl get ns >/dev/null 2>&1; then
    echo "Kubernetes API is not reachable. Terraform destroy needs a live cluster for k8s resources." >&2
    echo "Re-run after restoring kubeconfig or remove k8s resources from state." >&2
    return 1
  fi
  return 0
}

remove_k8s_service_accounts_from_state() {
  if [[ -z "${TF_DIR:-}" ]]; then
    return 0
  fi

  echo "Removing Kubernetes service accounts from Terraform state..."
  run_cmd bash "${repo_root}/bootstrap/60_tear_down_clean_up/remove-k8s-service-accounts-from-state.sh" "${TF_DIR}"
}

wait_with_heartbeat() {
  local label="$1"
  local check_cmd="$2"
  local interval="${3:-${HEARTBEAT_INTERVAL:-30}}"

  echo "${label} (heartbeat every ${interval}s)..."
  while true; do
    if eval "${check_cmd}"; then
      break
    fi
    echo "  still in progress... $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    sleep "${interval}"
  done
}

cleanup_loadbalancer_services() {
  local attempt=1
  local max_attempts="${LB_CLEANUP_ATTEMPTS:-5}"

  while [[ "${attempt}" -le "${max_attempts}" ]]; do
    services="$(kubectl get svc -A -o jsonpath='{range .items[?(@.spec.type=="LoadBalancer")]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' 2>/dev/null)"
    if [[ -z "${services}" ]]; then
      echo "No LoadBalancer services remain."
      return 0
    fi

    echo "LoadBalancer services still present (attempt ${attempt}/${max_attempts}):"
    echo "${services}"
    while read -r svc; do
      ns="${svc%%/*}"
      name="${svc##*/}"
      echo "Deleting ${ns}/${name}"
      kubectl -n "${ns}" delete svc "${name}" || true
    done <<< "${services}"

    echo "Waiting for LoadBalancer services to be removed..."
    sleep "${LB_CLEANUP_INTERVAL:-20}"
    attempt=$((attempt + 1))
  done

  echo "LoadBalancer services still present after ${max_attempts} attempts." >&2
  return 1
}

echo "Teardown starting for cluster ${cluster_name} in ${region}"

stage_banner "STAGE 1: CLUSTER CONTEXT"
echo "Updating kubeconfig for ${cluster_name} (${region})..."
run_cmd aws eks update-kubeconfig --name "${cluster_name}" --region "${region}"
stage_done "STAGE 1"

stage_banner "STAGE 2: PRE-DESTROY CLEANUP"
echo "Removing LoadBalancer services to release AWS resources..."
run_cmd bash "${repo_root}/bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh" "${cluster_name}" "${region}" --yes
cleanup_loadbalancer_services || true
wait_with_heartbeat \
  "Waiting for LoadBalancer services to be removed" \
  "test -z \"\$(kubectl get svc -A -o jsonpath='{range .items[?(@.spec.type==\"LoadBalancer\")]}{.metadata.namespace}/{.metadata.name}{\"\\n\"}{end}' 2>/dev/null)\""
stage_done "STAGE 2"

stage_banner "STAGE 3: DRAIN NODEGROUPS"
if [[ "${SKIP_DRAIN_NODEGROUPS:-false}" == "true" ]]; then
  echo "Skipping nodegroup drain (SKIP_DRAIN_NODEGROUPS=true)."
else
  nodegroups="$(aws eks list-nodegroups --cluster-name "${cluster_name}" --region "${region}" --query 'nodegroups[]' --output text)"
  if [[ -z "${nodegroups}" ]]; then
    echo "No nodegroups found."
  else
    for ng in ${nodegroups}; do
      echo "Draining nodegroup ${ng}..."
      RELAX_PDB="${RELAX_PDB:-true}" run_cmd bash "${repo_root}/bootstrap/60_tear_down_clean_up/drain-nodegroup.sh" "${ng}"
    done
  fi
fi
stage_done "STAGE 3"

stage_banner "STAGE 4: DELETE NODEGROUPS"
if [[ "${DELETE_NODEGROUPS:-true}" == "true" ]]; then
  nodegroups="$(aws eks list-nodegroups --cluster-name "${cluster_name}" --region "${region}" --query 'nodegroups[]' --output text)"
  if [[ -z "${nodegroups}" ]]; then
    echo "No nodegroups found."
  else
    for ng in ${nodegroups}; do
      echo "Deleting nodegroup ${ng}..."
      run_cmd aws eks delete-nodegroup --cluster-name "${cluster_name}" --nodegroup-name "${ng}" --region "${region}"
      if [[ "${WAIT_FOR_NODEGROUP_DELETE:-true}" == "true" ]]; then
        run_with_heartbeat \
          "Waiting for nodegroup ${ng} to delete" \
          aws eks wait nodegroup-deleted --cluster-name "${cluster_name}" --nodegroup-name "${ng}" --region "${region}"
      fi
    done
  fi
else
  echo "Skipping nodegroup deletion (DELETE_NODEGROUPS=false)."
fi
stage_done "STAGE 4"

stage_banner "STAGE 5: DESTROY CLUSTER"
if [[ -n "${TF_DIR:-}" ]]; then
  require_cmd terraform
  tf_failed=false
  if [[ "${REMOVE_K8S_SA_FROM_STATE:-true}" == "true" ]]; then
    if ensure_kube_access; then
      echo "Kubernetes API reachable; removing TF-managed service accounts to avoid destroy failures."
    else
      echo "Kubernetes API not reachable; removing TF-managed service accounts before destroy."
    fi
    if ! remove_k8s_service_accounts_from_state; then
      echo "Failed to remove Kubernetes service accounts from state." >&2
      tf_failed=true
    fi
  fi
  if [[ "${REQUIRE_KUBE_FOR_TF_DESTROY:-true}" == "true" ]]; then
    echo "Validating Kubernetes access before terraform destroy..."
    if ! ensure_kube_access; then
      if [[ "${REMOVE_K8S_SA_FROM_STATE:-true}" != "true" ]]; then
        tf_failed=true
      fi
    fi
  fi

  if [[ "${tf_failed}" == "false" ]]; then
    echo "Destroying via Terraform in ${TF_DIR}..."
    if [[ "${TF_AUTO_APPROVE:-false}" == "true" ]]; then
      run_with_heartbeat "Terraform destroy in ${TF_DIR}" terraform -chdir="${TF_DIR}" destroy -auto-approve || tf_failed=true
    else
      run_with_heartbeat "Terraform destroy in ${TF_DIR}" terraform -chdir="${TF_DIR}" destroy || tf_failed=true
    fi
  fi

  if [[ "${tf_failed}" == "true" && "${TF_DESTROY_FALLBACK_AWS:-false}" == "true" ]]; then
    echo "Terraform destroy failed or was skipped. Falling back to AWS cluster deletion..." >&2
    DELETE_CLUSTER=true
  fi
fi

if [[ "${TF_DESTROY_FALLBACK_AWS:-false}" == "true" && "${DELETE_CLUSTER:-true}" == "true" ]]; then
  echo "Deleting EKS cluster ${cluster_name}..."
  run_cmd aws eks delete-cluster --name "${cluster_name}" --region "${region}"
  run_with_heartbeat \
    "Waiting for cluster ${cluster_name} to delete" \
    aws eks wait cluster-deleted --name "${cluster_name}" --region "${region}"
else
  echo "Skipping cluster deletion (DELETE_CLUSTER=false)."
fi
stage_done "STAGE 5"

stage_banner "STAGE 6: OPTIONAL ORPHAN CLEANUP"
if [[ "${CLEANUP_ORPHANS:-false}" == "true" ]]; then
  if [[ -z "${BUILD_ID:-}" ]]; then
    echo "CLEANUP_ORPHANS=true but BUILD_ID is not set." >&2
    exit 1
  fi
  echo "Cleaning resources tagged with BuildId=${BUILD_ID}..."
  DRY_RUN=false run_with_heartbeat "Orphan cleanup for BuildId=${BUILD_ID}" \
    bash "${repo_root}/bootstrap/60_tear_down_clean_up/cleanup-orphans.sh" "${BUILD_ID}" "${region}"
else
  echo "Skipping orphan cleanup (CLEANUP_ORPHANS=false)."
fi
stage_done "STAGE 6"

stage_banner "STAGE 7: TEARDOWN COMPLETE"
echo "Teardown complete."
stage_done "STAGE 7"
