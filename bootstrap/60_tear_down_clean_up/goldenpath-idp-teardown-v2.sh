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
#   SUSPEND_ARGO_APP=true|false (default false)
#   DELETE_KONG_RESOURCES=true|false (default true)
#   KONG_NAMESPACE=<namespace> (default kong-system)
#   KONG_RELEASE=<helm release> (default dev-kong)
#   SCALE_DOWN_LB_CONTROLLER=true|false (default true)
#   LB_CONTROLLER_NAMESPACE=<namespace> (default kube-system)
#   LB_CONTROLLER_DEPLOYMENT=<name> (default aws-load-balancer-controller)
#   LB_CLEANUP_ATTEMPTS=<count> (default 5)
#   LB_CLEANUP_INTERVAL=<seconds> (default 20)
#   WAIT_FOR_LB_ENIS=true|false (default true)
#   LB_ENI_WAIT_MAX=<seconds> (default LB_CLEANUP_MAX_WAIT)
#   FORCE_DELETE_LBS=true|false (default true, break glass)
#   FORCE_DELETE_LB_FINALIZERS=true|false (default false, break glass)
#   LB_FINALIZER_WAIT_MAX=<seconds> (default 300)
#   KUBECTL_REQUEST_TIMEOUT=<duration> (default 10s)
#   TF_DIR=<path> (if set, run terraform destroy instead of aws eks delete-cluster)
#   TF_AUTO_APPROVE=true (use -auto-approve with terraform destroy)
#   TF_DESTROY_MAX_WAIT=<seconds> (default 1200)
#   TF_DESTROY_RETRY_ON_LB_CLEANUP=true|false (default true)
#   REMOVE_K8S_SA_FROM_STATE=true|false (default true)
#   CLEANUP_ORPHANS=true BUILD_ID=<id> (run cleanup-orphans after teardown)
#   ORPHAN_CLEANUP_MODE=delete|dry_run|none (default delete)

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

ARGO_APP_NAMESPACE="${ARGO_APP_NAMESPACE:-kong-system}"
ARGO_APP_NAME="${ARGO_APP_NAME:-dev-kong}"
SUSPEND_ARGO_APP="${SUSPEND_ARGO_APP:-false}"
DELETE_ARGO_APP="${DELETE_ARGO_APP:-true}"
DELETE_KONG_RESOURCES="${DELETE_KONG_RESOURCES:-true}"
KONG_NAMESPACE="${KONG_NAMESPACE:-${ARGO_APP_NAMESPACE}}"
KONG_RELEASE="${KONG_RELEASE:-dev-kong}"
SCALE_DOWN_LB_CONTROLLER="${SCALE_DOWN_LB_CONTROLLER:-true}"
LB_CONTROLLER_NAMESPACE="${LB_CONTROLLER_NAMESPACE:-kube-system}"
LB_CONTROLLER_DEPLOYMENT="${LB_CONTROLLER_DEPLOYMENT:-aws-load-balancer-controller}"
LB_CLEANUP_MAX_WAIT="${LB_CLEANUP_MAX_WAIT:-900}"
WAIT_FOR_LB_ENIS="${WAIT_FOR_LB_ENIS:-true}"
LB_ENI_WAIT_MAX="${LB_ENI_WAIT_MAX:-${LB_CLEANUP_MAX_WAIT}}"
FORCE_DELETE_LBS="${FORCE_DELETE_LBS:-true}"
FORCE_DELETE_LB_FINALIZERS="${FORCE_DELETE_LB_FINALIZERS:-false}"
LB_FINALIZER_WAIT_MAX="${LB_FINALIZER_WAIT_MAX:-300}"
TF_DESTROY_MAX_WAIT="${TF_DESTROY_MAX_WAIT:-1200}"
TF_DESTROY_RETRY_ON_LB_CLEANUP="${TF_DESTROY_RETRY_ON_LB_CLEANUP:-true}"
ORPHAN_CLEANUP_MODE="${ORPHAN_CLEANUP_MODE:-delete}"
KUBECTL_REQUEST_TIMEOUT="${KUBECTL_REQUEST_TIMEOUT:-10s}"

cleanup_on_exit() {
  local status=$?
  trap - EXIT

  if [[ -n "${TF_DIR:-}" && "${REMOVE_K8S_SA_FROM_STATE:-true}" == "true" ]]; then
    if command -v terraform >/dev/null 2>&1; then
      local cleanup_script="${repo_root}/bootstrap/60_tear_down_clean_up/remove-k8s-service-accounts-from-state.sh"
      if [[ -f "${cleanup_script}" ]]; then
        echo "Exit cleanup: removing Kubernetes service accounts from Terraform state (best effort)."
        bash "${cleanup_script}" "${TF_DIR}" >/dev/null 2>&1 || true
      fi
    fi
  fi

  exit "${status}"
}

trap cleanup_on_exit EXIT

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

run_tf_destroy() {
  local tf_dir="$1"
  shift
  local max_wait="${TF_DESTROY_MAX_WAIT:-}"
  if [[ -n "${max_wait}" && "${max_wait}" -gt 0 ]]; then
    if command -v timeout >/dev/null 2>&1; then
      run_with_heartbeat "Terraform destroy in ${tf_dir}" timeout "${max_wait}" "$@"
      return $?
    fi
    echo "Warning: timeout command not found; running terraform destroy without a max wait." >&2
  fi
  run_with_heartbeat "Terraform destroy in ${tf_dir}" "$@"
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
  local max_wait_seconds="${4:-}"
  local start_epoch
  local now_epoch
  local elapsed

  echo "${label} (heartbeat every ${interval}s)..."
  start_epoch="$(date -u +%s)"
  while true; do
    if eval "${check_cmd}"; then
      break
    fi
    if [[ -n "${max_wait_seconds}" && "${max_wait_seconds}" -gt 0 ]]; then
      now_epoch="$(date -u +%s)"
      elapsed=$((now_epoch - start_epoch))
      if [[ "${elapsed}" -ge "${max_wait_seconds}" ]]; then
        echo "Timed out after ${elapsed}s waiting for: ${label}" >&2
        return 1
      fi
    fi
    echo "  still in progress... $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    sleep "${interval}"
  done
}

list_lb_services() {
  kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get svc -A \
    -o jsonpath='{range .items[?(@.spec.type=="LoadBalancer")]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' 2>/dev/null || true
}

describe_lb_service_finalizers() {
  local services="$1"
  while read -r svc; do
    [[ -z "${svc}" ]] && continue
    local ns="${svc%%/*}"
    local name="${svc##*/}"
    local deletion_ts=""
    local finalizers=""
    deletion_ts="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" get svc "${name}" -o jsonpath='{.metadata.deletionTimestamp}' 2>/dev/null || true)"
    finalizers="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" get svc "${name}" -o jsonpath='{.metadata.finalizers[*]}' 2>/dev/null || true)"
    echo "  ${ns}/${name} deletionTimestamp=${deletion_ts:-none} finalizers=${finalizers:-none}"
  done <<< "${services}"
}

remove_lb_service_finalizers() {
  local services="$1"
  while read -r svc; do
    [[ -z "${svc}" ]] && continue
    local ns="${svc%%/*}"
    local name="${svc##*/}"
    local deletion_ts=""
    local finalizers=""
    deletion_ts="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" get svc "${name}" -o jsonpath='{.metadata.deletionTimestamp}' 2>/dev/null || true)"
    finalizers="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" get svc "${name}" -o jsonpath='{.metadata.finalizers[*]}' 2>/dev/null || true)"
    if [[ -z "${finalizers}" ]]; then
      continue
    fi
    if [[ -z "${deletion_ts}" ]]; then
      echo "Service ${ns}/${name} not marked for deletion; skipping finalizer removal."
      continue
    fi
    echo "Removing finalizers from ${ns}/${name}..."
    kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" patch svc "${name}" \
      --type=merge -p '{"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
  done <<< "${services}"
}

delete_argo_application() {
  if [[ "${SUSPEND_ARGO_APP}" == "true" ]]; then
    suspend_argo_application
  fi

  if [[ "${DELETE_ARGO_APP}" != "true" ]]; then
    echo "Skipping Argo application deletion (DELETE_ARGO_APP=false)."
    return 0
  fi

  if [[ -z "${ARGO_APP_NAMESPACE}" || -z "${ARGO_APP_NAME}" ]]; then
    echo "Skipping Argo application deletion (namespace/name not set)."
    return 0
  fi

  if ! kubectl get crd applications.argoproj.io >/dev/null 2>&1; then
    echo "Argo Application CRD not found; skipping deletion."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get ns "${ARGO_APP_NAMESPACE}" >/dev/null 2>&1; then
    echo "Namespace ${ARGO_APP_NAMESPACE} not found; skipping Argo application deletion."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ARGO_APP_NAMESPACE}" get application "${ARGO_APP_NAME}" >/dev/null 2>&1; then
    echo "Argo application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME} not found; skipping deletion."
    return 0
  fi

  echo "Deleting Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME} (best effort)..."
  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ARGO_APP_NAMESPACE}" delete application "${ARGO_APP_NAME}" --wait=false --ignore-not-found; then
    echo "Warning: failed to delete Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME}." >&2
  fi
}

delete_kong_resources() {
  if [[ "${DELETE_KONG_RESOURCES}" != "true" ]]; then
    echo "Skipping Kong resource cleanup (DELETE_KONG_RESOURCES=false)."
    return 0
  fi

  if [[ -z "${KONG_NAMESPACE}" || -z "${KONG_RELEASE}" ]]; then
    echo "Skipping Kong resource cleanup (namespace/release not set)."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get ns "${KONG_NAMESPACE}" >/dev/null 2>&1; then
    echo "Namespace ${KONG_NAMESPACE} not found; skipping Kong resource cleanup."
    return 0
  fi

  kong_resources="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${KONG_NAMESPACE}" get deploy,sts,ds,svc,ingress \
    -l "app.kubernetes.io/instance=${KONG_RELEASE}" -o name 2>/dev/null || true)"
  if [[ -z "${kong_resources}" ]]; then
    echo "No Kong resources found for release ${KONG_RELEASE}; skipping cleanup."
    return 0
  fi

  echo "Deleting Kong resources in ${KONG_NAMESPACE} (release=${KONG_RELEASE})..."
  kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${KONG_NAMESPACE}" delete deploy,sts,ds,svc,ingress \
    -l "app.kubernetes.io/instance=${KONG_RELEASE}" \
    --ignore-not-found --wait=false || true
}

scale_down_lb_controller() {
  if [[ "${SCALE_DOWN_LB_CONTROLLER}" != "true" ]]; then
    echo "Skipping LB controller scale down (SCALE_DOWN_LB_CONTROLLER=false)."
    return 0
  fi

  if [[ -z "${LB_CONTROLLER_NAMESPACE}" || -z "${LB_CONTROLLER_DEPLOYMENT}" ]]; then
    echo "Skipping LB controller scale down (namespace/deployment not set)."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${LB_CONTROLLER_NAMESPACE}" get deploy "${LB_CONTROLLER_DEPLOYMENT}" >/dev/null 2>&1; then
    echo "LB controller deployment not found; skipping scale down."
    return 0
  fi

  echo "Scaling down ${LB_CONTROLLER_NAMESPACE}/${LB_CONTROLLER_DEPLOYMENT} to stop LB reprovision."
  kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${LB_CONTROLLER_NAMESPACE}" scale deploy "${LB_CONTROLLER_DEPLOYMENT}" --replicas=0 || true
}

suspend_argo_application() {
  if [[ "${SUSPEND_ARGO_APP}" != "true" ]]; then
    return 0
  fi

  if [[ -z "${ARGO_APP_NAMESPACE}" || -z "${ARGO_APP_NAME}" ]]; then
    return 0
  fi

  if ! kubectl get crd applications.argoproj.io >/dev/null 2>&1; then
    return 0
  fi

  if ! kubectl get ns "${ARGO_APP_NAMESPACE}" >/dev/null 2>&1; then
    return 0
  fi

  if ! kubectl -n "${ARGO_APP_NAMESPACE}" get application "${ARGO_APP_NAME}" >/dev/null 2>&1; then
    return 0
  fi

  echo "Suspending Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME} to stop reprovision."
  kubectl -n "${ARGO_APP_NAMESPACE}" patch application "${ARGO_APP_NAME}" \
    --type merge \
    -p '{"spec":{"syncPolicy":null}}' >/dev/null 2>&1 || true
}

cleanup_loadbalancer_services() {
  local attempt=1
  local max_attempts="${LB_CLEANUP_ATTEMPTS:-5}"

  while [[ "${attempt}" -le "${max_attempts}" ]]; do
    services="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get svc -A -o jsonpath='{range .items[?(@.spec.type=="LoadBalancer")]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' 2>/dev/null)"
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
      kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" delete svc "${name}" --wait=false || true
    done <<< "${services}"

    echo "Waiting for LoadBalancer services to be removed..."
    sleep "${LB_CLEANUP_INTERVAL:-20}"
    attempt=$((attempt + 1))
  done

  echo "LoadBalancer services still present after ${max_attempts} attempts." >&2
  return 1
}

get_cluster_subnet_filter() {
  local subnet_ids=""
  subnet_ids="$(aws eks describe-cluster \
    --name "${cluster_name}" \
    --region "${region}" \
    --query 'cluster.resourcesVpcConfig.subnetIds' \
    --output text 2>/dev/null || true)"
  if [[ -z "${subnet_ids}" ]]; then
    return 1
  fi
  echo "${subnet_ids}" | tr ' ' ','
}

list_lb_enis() {
  local subnet_filter="$1"
  if [[ -z "${subnet_filter}" ]]; then
    return 0
  fi
  aws ec2 describe-network-interfaces \
    --region "${region}" \
    --filters "Name=subnet-id,Values=${subnet_filter}" \
              "Name=interface-type,Values=network_load_balancer" \
              "Name=description,Values=ELB net/*" \
    --query 'NetworkInterfaces[].[NetworkInterfaceId,Description,Status]' \
    --output text 2>/dev/null || true
}

extract_lb_names_from_enis() {
  local enis="$1"
  declare -A lb_names=()
  local eni_id=""
  local desc=""
  local status=""

  while IFS=$'\t' read -r eni_id desc status; do
    [[ -z "${desc}" ]] && continue
    if [[ "${desc}" =~ ^ELB\ net/([^/]+)/ ]]; then
      local lb_name="${BASH_REMATCH[1]}"
      if [[ "${lb_name}" == k8s-* ]]; then
        lb_names["${lb_name}"]=1
      fi
    fi
  done <<< "${enis}"

  for lb_name in "${!lb_names[@]}"; do
    echo "${lb_name}"
  done
}

delete_lbs_for_enis() {
  local enis="$1"
  local lb_names=""
  lb_names="$(extract_lb_names_from_enis "${enis}")"
  if [[ -z "${lb_names}" ]]; then
    echo "No Kubernetes load balancers found in ENI descriptions; falling back to tag scan."
    delete_lbs_by_cluster_tag
    return $?
  fi

  while IFS= read -r lb_name; do
    [[ -z "${lb_name}" ]] && continue
    local lb_arn=""
    lb_arn="$(aws elbv2 describe-load-balancers \
      --region "${region}" \
      --names "${lb_name}" \
      --query 'LoadBalancers[0].LoadBalancerArn' \
      --output text 2>/dev/null || true)"
    if [[ -z "${lb_arn}" || "${lb_arn}" == "None" ]]; then
      echo "Load balancer ${lb_name} not found; skipping."
      continue
    fi
    local cluster_tag=""
    cluster_tag="$(aws elbv2 describe-tags \
      --region "${region}" \
      --resource-arns "${lb_arn}" \
      --query 'TagDescriptions[0].Tags[?Key==`elbv2.k8s.aws/cluster`].Value | [0]' \
      --output text 2>/dev/null || true)"
    if [[ "${cluster_tag}" != "${cluster_name}" ]]; then
      echo "Skipping load balancer ${lb_name}; cluster tag '${cluster_tag}' does not match ${cluster_name}."
      continue
    fi
    local service_tag=""
    service_tag="$(aws elbv2 describe-tags \
      --region "${region}" \
      --resource-arns "${lb_arn}" \
      --query 'TagDescriptions[0].Tags[?Key==`kubernetes.io/service-name` || Key==`service.k8s.aws/resource` || Key==`service.k8s.aws/stack`].Key | [0]' \
      --output text 2>/dev/null || true)"
    if [[ -z "${service_tag}" || "${service_tag}" == "None" ]]; then
      echo "Skipping load balancer ${lb_name}; missing Kubernetes service tag."
      continue
    fi
    echo "Deleting load balancer ${lb_name} (${lb_arn})"
    aws elbv2 delete-load-balancer --region "${region}" --load-balancer-arn "${lb_arn}" || true
  done <<< "${lb_names}"
}

delete_lbs_by_cluster_tag() {
  local lb_arns=""
  lb_arns="$(aws elbv2 describe-load-balancers \
    --region "${region}" \
    --query 'LoadBalancers[].LoadBalancerArn' \
    --output text 2>/dev/null || true)"
  if [[ -z "${lb_arns}" ]]; then
    echo "No load balancers found for tag scan."
    return 0
  fi

  for lb_arn in ${lb_arns}; do
    local cluster_tag=""
    cluster_tag="$(aws elbv2 describe-tags \
      --region "${region}" \
      --resource-arns "${lb_arn}" \
      --query 'TagDescriptions[0].Tags[?Key==`elbv2.k8s.aws/cluster`].Value | [0]' \
      --output text 2>/dev/null || true)"
    if [[ "${cluster_tag}" != "${cluster_name}" ]]; then
      continue
    fi
    local service_tag=""
    service_tag="$(aws elbv2 describe-tags \
      --region "${region}" \
      --resource-arns "${lb_arn}" \
      --query 'TagDescriptions[0].Tags[?Key==`kubernetes.io/service-name` || Key==`service.k8s.aws/resource` || Key==`service.k8s.aws/stack`].Key | [0]' \
      --output text 2>/dev/null || true)"
    if [[ -z "${service_tag}" || "${service_tag}" == "None" ]]; then
      continue
    fi
    echo "Deleting load balancer ${lb_arn} (cluster tag ${cluster_tag})."
    aws elbv2 delete-load-balancer --region "${region}" --load-balancer-arn "${lb_arn}" || true
  done
}

wait_for_lb_enis() {
  local subnet_filter="$1"
  local interval="${LB_ENI_WAIT_INTERVAL:-30}"
  local max_wait="${LB_ENI_WAIT_MAX}"
  local start_epoch
  start_epoch="$(date -u +%s)"

  if [[ -z "${subnet_filter}" ]]; then
    echo "Skipping LoadBalancer ENI wait (no subnet filter available)."
    return 0
  fi

  echo "Waiting for LoadBalancer ENIs to be removed (heartbeat every ${interval}s)..."
  while true; do
    local enis=""
    enis="$(list_lb_enis "${subnet_filter}")"
    if [[ -z "${enis}" ]]; then
      echo "No LoadBalancer ENIs remain."
      return 0
    fi

    echo "LoadBalancer ENIs still present:"
    echo "${enis}"

    if [[ -n "${max_wait}" && "${max_wait}" -gt 0 ]]; then
      local now_epoch
      now_epoch="$(date -u +%s)"
      local elapsed=$((now_epoch - start_epoch))
      if [[ "${elapsed}" -ge "${max_wait}" ]]; then
        echo "Timed out after ${elapsed}s waiting for LoadBalancer ENIs." >&2
        return 1
      fi
    fi

    sleep "${interval}"
  done
}

echo "Teardown starting for cluster ${cluster_name} in ${region}"
cluster_exists="true"
kube_access="true"

stage_banner "STAGE 1: CLUSTER CONTEXT"
echo "Validating cluster ${cluster_name} exists..."
if ! aws eks describe-cluster --name "${cluster_name}" --region "${region}" >/dev/null 2>&1; then
  echo "Cluster ${cluster_name} not found; skipping Kubernetes cleanup stages."
  cluster_exists="false"
else
  echo "Updating kubeconfig for ${cluster_name} (${region})..."
  run_cmd aws eks update-kubeconfig --name "${cluster_name}" --region "${region}"
  if ! kubectl get ns >/dev/null 2>&1; then
    echo "Kubernetes API not reachable or unauthorized; skipping Kubernetes cleanup stages."
    kube_access="false"
    REQUIRE_KUBE_FOR_TF_DESTROY="false"
  fi
fi
stage_done "STAGE 1"

stage_banner "STAGE 2: PRE-DESTROY CLEANUP"
if [[ "${cluster_exists}" == "false" || "${kube_access}" == "false" ]]; then
  echo "Skipping Kubernetes pre-destroy cleanup (cluster not reachable)."
  if [[ "${WAIT_FOR_LB_ENIS}" == "true" ]]; then
    subnet_filter="$(get_cluster_subnet_filter || true)"
    echo "Attempting AWS-only LoadBalancer cleanup."
    if [[ "${FORCE_DELETE_LBS}" == "true" ]]; then
      delete_lbs_by_cluster_tag || true
      remaining_enis="$(list_lb_enis "${subnet_filter}")"
      if [[ -n "${remaining_enis}" ]]; then
        delete_lbs_for_enis "${remaining_enis}"
      fi
    fi
    wait_for_lb_enis "${subnet_filter}" || true
  fi
else
  delete_argo_application
  delete_kong_resources
  echo "Removing LoadBalancer services to release AWS resources..."
  run_cmd bash "${repo_root}/bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh" "${cluster_name}" "${region}" --yes
  cleanup_loadbalancer_services || true
  lb_wait_rc=0
  wait_with_heartbeat \
    "Waiting for LoadBalancer services to be removed" \
    "test -z \"\$(list_lb_services)\"" \
    "${HEARTBEAT_INTERVAL:-30}" \
    "${LB_CLEANUP_MAX_WAIT}" || lb_wait_rc=$?
  if [[ "${lb_wait_rc}" -ne 0 ]]; then
    remaining_services="$(list_lb_services)"
    if [[ -z "${remaining_services}" ]]; then
      echo "No LoadBalancer services remain after wait timeout; continuing."
    else
      echo "LoadBalancer services still present after wait:"
      echo "${remaining_services}"
      echo "Finalizer status:"
      describe_lb_service_finalizers "${remaining_services}"
      if [[ "${FORCE_DELETE_LB_FINALIZERS}" == "true" ]]; then
        echo "Removing stuck LoadBalancer service finalizers (FORCE_DELETE_LB_FINALIZERS=true)."
        remove_lb_service_finalizers "${remaining_services}"
        wait_with_heartbeat \
          "Waiting for LoadBalancer services after finalizer removal" \
          "test -z \"\$(list_lb_services)\"" \
          "${HEARTBEAT_INTERVAL:-30}" \
          "${LB_FINALIZER_WAIT_MAX}"
      else
        echo "LoadBalancer services still present. Set FORCE_DELETE_LB_FINALIZERS=true to remove stuck finalizers." >&2
        exit 1
      fi
    fi
  fi

  scale_down_lb_controller

  if [[ "${WAIT_FOR_LB_ENIS}" == "true" ]]; then
    subnet_filter="$(get_cluster_subnet_filter || true)"
    if ! wait_for_lb_enis "${subnet_filter}"; then
      if [[ "${FORCE_DELETE_LBS}" == "true" ]]; then
        echo "Attempting to delete remaining load balancers (FORCE_DELETE_LBS=true)."
        delete_lbs_by_cluster_tag || true
        remaining_enis="$(list_lb_enis "${subnet_filter}")"
        if [[ -n "${remaining_enis}" ]]; then
          delete_lbs_for_enis "${remaining_enis}"
        fi
        wait_for_lb_enis "${subnet_filter}"
      else
        echo "LoadBalancer ENIs still present. Set FORCE_DELETE_LBS=true to attempt deletion." >&2
        exit 1
      fi
    fi
  fi
fi
stage_done "STAGE 2"

stage_banner "STAGE 3: DRAIN NODEGROUPS"
if [[ "${cluster_exists}" == "false" || "${kube_access}" == "false" ]]; then
  echo "Skipping nodegroup drain (cluster not found)."
elif [[ "${SKIP_DRAIN_NODEGROUPS:-false}" == "true" ]]; then
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
if [[ "${cluster_exists}" == "false" || "${kube_access}" == "false" ]]; then
  echo "Skipping nodegroup deletion (cluster not found)."
elif [[ "${DELETE_NODEGROUPS:-true}" == "true" ]]; then
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
    destroy_rc=0
    if [[ "${TF_AUTO_APPROVE:-false}" == "true" ]]; then
      run_tf_destroy "${TF_DIR}" terraform -chdir="${TF_DIR}" destroy -auto-approve || destroy_rc=$?
    else
      run_tf_destroy "${TF_DIR}" terraform -chdir="${TF_DIR}" destroy || destroy_rc=$?
    fi
    if [[ "${destroy_rc}" -ne 0 ]]; then
      tf_failed=true
      tf_destroy_timed_out=false
      if [[ "${destroy_rc}" -eq 124 ]]; then
        tf_destroy_timed_out=true
      fi
      if [[ "${TF_DESTROY_RETRY_ON_LB_CLEANUP}" == "true" ]]; then
        retry_needed="${tf_destroy_timed_out}"
        if [[ "${WAIT_FOR_LB_ENIS}" == "true" ]]; then
          subnet_filter="$(get_cluster_subnet_filter || true)"
          if [[ -n "${subnet_filter}" ]]; then
            remaining_enis="$(list_lb_enis "${subnet_filter}")"
            if [[ -n "${remaining_enis}" ]]; then
              retry_needed="true"
              if [[ "${FORCE_DELETE_LBS}" == "true" ]]; then
                echo "Terraform destroy failed; re-checking LoadBalancer ENIs and deleting remaining LBs."
                lb_names="$(extract_lb_names_from_enis "${remaining_enis}")"
                echo "Forced cleanup summary (before retry):"
                while IFS=$'\t' read -r eni_id desc status; do
                  [[ -z "${eni_id}" ]] && continue
                  echo "  ENI: ${eni_id} (${status}) ${desc}"
                done <<< "${remaining_enis}"
                if [[ -n "${lb_names}" ]]; then
                  while IFS= read -r lb_name; do
                    [[ -z "${lb_name}" ]] && continue
                    echo "  LB: ${lb_name}"
                  done <<< "${lb_names}"
                fi
                delete_lbs_for_enis "${remaining_enis}"
                wait_for_lb_enis "${subnet_filter}" || true
              else
                echo "LoadBalancer ENIs still present. Set FORCE_DELETE_LBS=true to attempt deletion." >&2
              fi
            fi
          fi
        fi
        if [[ "${retry_needed}" == "true" ]]; then
          echo "Retrying Terraform destroy after LoadBalancer cleanup."
          destroy_retry_rc=0
          if [[ "${TF_AUTO_APPROVE:-false}" == "true" ]]; then
            run_tf_destroy "${TF_DIR}" terraform -chdir="${TF_DIR}" destroy -auto-approve || destroy_retry_rc=$?
          else
            run_tf_destroy "${TF_DIR}" terraform -chdir="${TF_DIR}" destroy || destroy_retry_rc=$?
          fi
          if [[ "${destroy_retry_rc}" -eq 0 ]]; then
            tf_failed=false
          fi
        fi
      fi
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
if [[ "${CLEANUP_ORPHANS:-false}" != "true" ]]; then
  echo "Skipping orphan cleanup (CLEANUP_ORPHANS=false)."
  stage_done "STAGE 6"
else
  case "${ORPHAN_CLEANUP_MODE}" in
    none)
      echo "Skipping orphan cleanup (ORPHAN_CLEANUP_MODE=none)."
      stage_done "STAGE 6"
      ;;
    dry_run|delete)
      if [[ -z "${BUILD_ID:-}" ]]; then
        echo "ORPHAN_CLEANUP_MODE=${ORPHAN_CLEANUP_MODE} but BUILD_ID is not set." >&2
        exit 1
      fi
      if [[ "${ORPHAN_CLEANUP_MODE}" == "dry_run" ]]; then
        cleanup_dry_run="true"
      else
        cleanup_dry_run="false"
      fi
      echo "Orphan cleanup (mode=${ORPHAN_CLEANUP_MODE}, dry_run=${cleanup_dry_run}) for BuildId=${BUILD_ID}..."
      DRY_RUN="${cleanup_dry_run}" run_with_heartbeat "Orphan cleanup for BuildId=${BUILD_ID}" \
        bash "${repo_root}/bootstrap/60_tear_down_clean_up/cleanup-orphans.sh" "${BUILD_ID}" "${region}"
      stage_done "STAGE 6"
      ;;
    *)
      echo "Unsupported ORPHAN_CLEANUP_MODE=${ORPHAN_CLEANUP_MODE}." >&2
      exit 1
      ;;
  esac
fi

stage_banner "STAGE 7: TEARDOWN COMPLETE"
echo "Teardown complete."
stage_done "STAGE 7"
