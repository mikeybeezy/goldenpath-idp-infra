#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# TEARDOWN V3 - Enhanced EKS Cluster Teardown Runner
# =============================================================================
#
# Version: 3.1.0
# Purpose: Reliable teardown of EKS clusters with proper resource ordering
#
# Key improvements over v2:
#   - Nodegroup deletion via AWS CLI works even when k8s API is unavailable
#   - Explicit step logging for every operation (no "unknown" steps)
#   - Proper LoadBalancer drain -> LB delete -> ENI cleanup ordering
#   - RDS instance cleanup support with fallback strategies
#   - Target group cleanup with multiple tag pattern matching
#   - Detailed break-glass logging for troubleshooting
#
# Key improvements in v3.1.0:
#   - ALB ENI handling (not just NLB)
#   - Classic ELB deletion support
#   - Broader target group tag search patterns
#   - Ingress finalizer removal
#   - Fargate profile deletion
#   - RDS fallback for missing BuildId (uses cluster name tags/patterns)
#
# Usage:
#   bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh <cluster-name> <region>
#
# Required:
#   TEARDOWN_CONFIRM=true
#
# Optional flags:
#   SKIP_DRAIN_NODEGROUPS=true|false (default false)
#   DELETE_NODEGROUPS=true|false (default true)
#   WAIT_FOR_NODEGROUP_DELETE=true|false (default true)
#   NODEGROUP_DELETE_TIMEOUT=<seconds> (default 600)
#   DELETE_FARGATE_PROFILES=true|false (default true)
#   WAIT_FOR_FARGATE_DELETE=true|false (default true)
#   FARGATE_PROFILE_DELETE_TIMEOUT=<seconds> (default 300)
#   DELETE_CLUSTER=true|false (default true, ignored when TF_DIR is set)
#   SUSPEND_ARGO_APP=true|false (default false)
#   DELETE_ARGO_APP=true|false (default true)
#   DELETE_KONG_RESOURCES=true|false (default true)
#   KONG_NAMESPACE=<namespace> (default kong-system)
#   KONG_RELEASE=<helm release> (default dev-kong)
#   DELETE_INGRESS_RESOURCES=true|false (default true)
#   FORCE_DELETE_INGRESS_FINALIZERS=true|false (default true)
#   SCALE_DOWN_LB_CONTROLLER=true|false (default true)
#   LB_CONTROLLER_NAMESPACE=<namespace> (default kube-system)
#   LB_CONTROLLER_DEPLOYMENT=<name> (default aws-load-balancer-controller)
#   LB_CLEANUP_ATTEMPTS=<count> (default 5)
#   LB_CLEANUP_INTERVAL=<seconds> (default 20)
#   LB_CLEANUP_MAX_WAIT=<seconds> (default 900)
#   WAIT_FOR_LB_ENIS=true|false (default true)
#   LB_ENI_WAIT_MAX=<seconds> (default LB_CLEANUP_MAX_WAIT)
#   FORCE_DELETE_LBS=true|false (default true, break glass)
#   FORCE_DELETE_LB_FINALIZERS=true|false (default true, break glass)
#   LB_FINALIZER_WAIT_MAX=<seconds> (default 300)
#   DELETE_TARGET_GROUPS=true|false (default true)
#   KUBECTL_REQUEST_TIMEOUT=<duration> (default 10s)
#   TF_DIR=<path> (if set, run terraform destroy instead of aws eks delete-cluster)
#   TF_AUTO_APPROVE=true (use -auto-approve with terraform destroy)
#   TF_DESTROY_MAX_WAIT=<seconds> (default 1200)
#   TF_DESTROY_RETRY_ON_LB_CLEANUP=true|false (default true)
#   REMOVE_K8S_SA_FROM_STATE=true|false (default true)
#   CLEANUP_ORPHANS=true BUILD_ID=<id> (run cleanup-orphans after teardown)
#   ORPHAN_CLEANUP_MODE=delete|dry_run|none (default delete)
#   DELETE_RDS_INSTANCES=true|false (default true)
#   RDS_SKIP_FINAL_SNAPSHOT=true|false (default true for ephemeral)
#   RDS_DELETE_AUTOMATED_BACKUPS=true|false (default true for ephemeral)
#
# =============================================================================

cluster_name="${1:-}"
region="${2:-}"

# =============================================================================
# VALIDATION
# =============================================================================

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
    echo "[FATAL] Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd aws
require_cmd kubectl
require_cmd date
require_cmd jq

# =============================================================================
# CONFIGURATION
# =============================================================================

script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "${script_root}" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${repo_root}" ]]; then
  repo_root="$(cd "${script_root}/../.." && pwd)"
fi

if [[ -n "${TF_DIR:-}" && "${TF_DIR}" != /* ]]; then
  TF_DIR="${repo_root}/${TF_DIR}"
fi

# ArgoCD settings
ARGO_APP_NAMESPACE="${ARGO_APP_NAMESPACE:-kong-system}"
ARGO_APP_NAME="${ARGO_APP_NAME:-dev-kong}"
SUSPEND_ARGO_APP="${SUSPEND_ARGO_APP:-false}"
DELETE_ARGO_APP="${DELETE_ARGO_APP:-true}"

# Kong settings
DELETE_KONG_RESOURCES="${DELETE_KONG_RESOURCES:-true}"
KONG_NAMESPACE="${KONG_NAMESPACE:-${ARGO_APP_NAMESPACE}}"
KONG_RELEASE="${KONG_RELEASE:-dev-kong}"

# LB Controller settings
SCALE_DOWN_LB_CONTROLLER="${SCALE_DOWN_LB_CONTROLLER:-true}"
LB_CONTROLLER_NAMESPACE="${LB_CONTROLLER_NAMESPACE:-kube-system}"
LB_CONTROLLER_DEPLOYMENT="${LB_CONTROLLER_DEPLOYMENT:-aws-load-balancer-controller}"

# LB cleanup settings
LB_CLEANUP_MAX_WAIT="${LB_CLEANUP_MAX_WAIT:-900}"
LB_CLEANUP_ATTEMPTS="${LB_CLEANUP_ATTEMPTS:-5}"
LB_CLEANUP_INTERVAL="${LB_CLEANUP_INTERVAL:-20}"
WAIT_FOR_LB_ENIS="${WAIT_FOR_LB_ENIS:-true}"
LB_ENI_WAIT_MAX="${LB_ENI_WAIT_MAX:-${LB_CLEANUP_MAX_WAIT}}"
FORCE_DELETE_LBS="${FORCE_DELETE_LBS:-true}"
FORCE_DELETE_LB_FINALIZERS="${FORCE_DELETE_LB_FINALIZERS:-true}"
LB_FINALIZER_WAIT_MAX="${LB_FINALIZER_WAIT_MAX:-300}"
DELETE_TARGET_GROUPS="${DELETE_TARGET_GROUPS:-true}"

# Nodegroup settings
NODEGROUP_DELETE_TIMEOUT="${NODEGROUP_DELETE_TIMEOUT:-600}"

# Terraform settings
TF_DESTROY_MAX_WAIT="${TF_DESTROY_MAX_WAIT:-1200}"
TF_DESTROY_RETRY_ON_LB_CLEANUP="${TF_DESTROY_RETRY_ON_LB_CLEANUP:-true}"

# Orphan cleanup settings
ORPHAN_CLEANUP_MODE="${ORPHAN_CLEANUP_MODE:-delete}"

# RDS settings
DELETE_RDS_INSTANCES="${DELETE_RDS_INSTANCES:-true}"
RDS_SKIP_FINAL_SNAPSHOT="${RDS_SKIP_FINAL_SNAPSHOT:-true}"
RDS_DELETE_AUTOMATED_BACKUPS="${RDS_DELETE_AUTOMATED_BACKUPS:-true}"

# Kubectl settings
KUBECTL_REQUEST_TIMEOUT="${KUBECTL_REQUEST_TIMEOUT:-10s}"

# Heartbeat interval
HEARTBEAT_INTERVAL="${HEARTBEAT_INTERVAL:-30}"

# =============================================================================
# LOGGING HELPERS
# =============================================================================

log_step() {
  local step_name="$1"
  local message="$2"
  echo "[STEP: ${step_name}] ${message}"
}

log_info() {
  echo "[INFO] $*"
}

log_warn() {
  echo "[WARN] $*" >&2
}

log_error() {
  echo "[ERROR] $*" >&2
}

log_breakglass() {
  echo "[BREAK-GLASS] $*"
}

stage_banner() {
  local stage_num="$1"
  local title="$2"
  echo ""
  echo "============================================================================="
  echo "STAGE ${stage_num}: ${title}"
  echo "============================================================================="
  echo "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""
}

stage_done() {
  local stage_num="$1"
  local title="$2"
  echo ""
  echo "------------- STAGE ${stage_num} COMPLETE: ${title} -------------"
  echo "Completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""
}

# =============================================================================
# CLEANUP ON EXIT
# =============================================================================

cleanup_on_exit() {
  local status=$?
  trap - EXIT

  if [[ -n "${TF_DIR:-}" && "${REMOVE_K8S_SA_FROM_STATE:-true}" == "true" ]]; then
    if command -v terraform >/dev/null 2>&1; then
      local cleanup_script="${repo_root}/bootstrap/60_tear_down_clean_up/remove-k8s-service-accounts-from-state.sh"
      if [[ -f "${cleanup_script}" ]]; then
        log_info "Exit cleanup: removing Kubernetes service accounts from Terraform state (best effort)."
        bash "${cleanup_script}" "${TF_DIR}" >/dev/null 2>&1 || true
      fi
    fi
  fi

  exit "${status}"
}

trap cleanup_on_exit EXIT

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

run_with_heartbeat() {
  local label="$1"
  shift
  local interval="${HEARTBEAT_INTERVAL}"

  log_info "${label} (heartbeat every ${interval}s)..."
  "$@" &
  local cmd_pid=$!

  while kill -0 "${cmd_pid}" >/dev/null 2>&1; do
    echo "  [HEARTBEAT] still in progress... $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    sleep "${interval}"
  done

  wait "${cmd_pid}"
}

wait_with_timeout() {
  local label="$1"
  local check_cmd="$2"
  local interval="${3:-${HEARTBEAT_INTERVAL}}"
  local max_wait_seconds="${4:-}"
  local start_epoch
  local now_epoch
  local elapsed

  log_info "${label} (checking every ${interval}s, max ${max_wait_seconds:-unlimited}s)..."
  start_epoch="$(date -u +%s)"

  while true; do
    if eval "${check_cmd}"; then
      log_info "${label} - condition met."
      return 0
    fi

    if [[ -n "${max_wait_seconds}" && "${max_wait_seconds}" -gt 0 ]]; then
      now_epoch="$(date -u +%s)"
      elapsed=$((now_epoch - start_epoch))
      if [[ "${elapsed}" -ge "${max_wait_seconds}" ]]; then
        log_error "Timed out after ${elapsed}s waiting for: ${label}"
        return 1
      fi
      echo "  [WAIT] ${elapsed}s/${max_wait_seconds}s elapsed... $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    else
      echo "  [WAIT] still waiting... $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    fi
    sleep "${interval}"
  done
}

ensure_kube_access() {
  if ! kubectl get ns >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

# =============================================================================
# LOADBALANCER FUNCTIONS
# =============================================================================

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
    log_info "  ${ns}/${name} deletionTimestamp=${deletion_ts:-none} finalizers=${finalizers:-none}"
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
      log_info "Service ${ns}/${name} not marked for deletion; skipping finalizer removal."
      continue
    fi
    log_breakglass "Removing finalizers from ${ns}/${name}..."
    kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" patch svc "${name}" \
      --type=merge -p '{"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
  done <<< "${services}"
}

# =============================================================================
# INGRESS CLEANUP FUNCTIONS
# =============================================================================

list_ingress_resources() {
  kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get ingress -A \
    -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' 2>/dev/null || true
}

delete_ingress_resources() {
  log_step "DELETE_INGRESSES" "Deleting Ingress resources..."

  local ingresses=""
  ingresses="$(list_ingress_resources)"

  if [[ -z "${ingresses}" ]]; then
    log_info "No Ingress resources found."
    return 0
  fi

  local deleted_count=0
  while read -r ing; do
    [[ -z "${ing}" ]] && continue
    local ns="${ing%%/*}"
    local name="${ing##*/}"
    log_step "DELETE_INGRESS" "Deleting Ingress ${ns}/${name}..."
    if kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" delete ingress "${name}" --wait=false --ignore-not-found 2>/dev/null; then
      log_info "  Deleted Ingress: ${ns}/${name}"
      deleted_count=$((deleted_count + 1))
    else
      log_warn "  Failed to delete Ingress: ${ns}/${name}"
    fi
  done <<< "${ingresses}"

  log_info "Deleted ${deleted_count} Ingress resources."
}

remove_ingress_finalizers() {
  log_step "REMOVE_INGRESS_FINALIZERS" "Checking for stuck Ingress finalizers..."

  local ingresses=""
  ingresses="$(list_ingress_resources)"

  if [[ -z "${ingresses}" ]]; then
    return 0
  fi

  while read -r ing; do
    [[ -z "${ing}" ]] && continue
    local ns="${ing%%/*}"
    local name="${ing##*/}"
    local deletion_ts=""
    local finalizers=""

    deletion_ts="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" get ingress "${name}" \
      -o jsonpath='{.metadata.deletionTimestamp}' 2>/dev/null || true)"
    finalizers="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" get ingress "${name}" \
      -o jsonpath='{.metadata.finalizers[*]}' 2>/dev/null || true)"

    if [[ -z "${finalizers}" ]]; then
      continue
    fi

    if [[ -z "${deletion_ts}" ]]; then
      log_info "Ingress ${ns}/${name} not marked for deletion; skipping finalizer removal."
      continue
    fi

    log_breakglass "Removing finalizers from Ingress ${ns}/${name}..."
    kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" patch ingress "${name}" \
      --type=merge -p '{"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
  done <<< "${ingresses}"
}

cleanup_ingress_resources() {
  if [[ "${DELETE_INGRESS_RESOURCES:-true}" != "true" ]]; then
    log_info "Skipping Ingress cleanup (DELETE_INGRESS_RESOURCES=false)."
    return 0
  fi

  delete_ingress_resources

  # Wait briefly for ingresses to be deleted
  sleep 5

  # Check for stuck ingresses and remove finalizers
  local remaining=""
  remaining="$(list_ingress_resources)"
  if [[ -n "${remaining}" ]]; then
    log_warn "Some Ingresses still present after deletion request."
    if [[ "${FORCE_DELETE_INGRESS_FINALIZERS:-true}" == "true" ]]; then
      remove_ingress_finalizers
    fi
  fi
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

  # List NLB ENIs
  local nlb_enis=""
  nlb_enis="$(aws ec2 describe-network-interfaces \
    --region "${region}" \
    --filters "Name=subnet-id,Values=${subnet_filter}" \
              "Name=interface-type,Values=network_load_balancer" \
              "Name=description,Values=ELB net/*" \
    --query 'NetworkInterfaces[].[NetworkInterfaceId,Description,Status]' \
    --output text 2>/dev/null || true)"

  # List ALB ENIs (interface-type is 'interface' for ALBs, filter by description)
  local alb_enis=""
  alb_enis="$(aws ec2 describe-network-interfaces \
    --region "${region}" \
    --filters "Name=subnet-id,Values=${subnet_filter}" \
              "Name=description,Values=ELB app/*" \
    --query 'NetworkInterfaces[].[NetworkInterfaceId,Description,Status]' \
    --output text 2>/dev/null || true)"

  # Combine results
  {
    [[ -n "${nlb_enis}" ]] && echo "${nlb_enis}"
    [[ -n "${alb_enis}" ]] && echo "${alb_enis}"
  } | grep -v '^$' || true
}

extract_lb_names_from_enis() {
  local enis="$1"
  declare -A lb_names=()
  local eni_id=""
  local desc=""
  local status=""

  while IFS=$'\t' read -r eni_id desc status; do
    [[ -z "${desc}" ]] && continue
    # Match NLB pattern: "ELB net/<lb-name>/<suffix>"
    if [[ "${desc}" =~ ^ELB\ net/([^/]+)/ ]]; then
      local lb_name="${BASH_REMATCH[1]}"
      if [[ "${lb_name}" == k8s-* ]]; then
        lb_names["${lb_name}"]=1
      fi
    # Match ALB pattern: "ELB app/<lb-name>/<suffix>"
    elif [[ "${desc}" =~ ^ELB\ app/([^/]+)/ ]]; then
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

# =============================================================================
# CLASSIC ELB FUNCTIONS
# =============================================================================

delete_classic_elbs_by_cluster_tag() {
  log_step "DELETE_CLASSIC_ELBS" "Scanning Classic load balancers by cluster tag..."

  local elb_names=""
  elb_names="$(aws elb describe-load-balancers \
    --region "${region}" \
    --query 'LoadBalancerDescriptions[].LoadBalancerName' \
    --output text 2>/dev/null || true)"

  if [[ -z "${elb_names}" ]]; then
    log_info "No Classic load balancers found."
    return 0
  fi

  local deleted_count=0
  for elb_name in ${elb_names}; do
    # Get tags for this ELB
    local cluster_tag=""
    cluster_tag="$(aws elb describe-tags \
      --region "${region}" \
      --load-balancer-names "${elb_name}" \
      --query 'TagDescriptions[0].Tags[?Key==`kubernetes.io/cluster/'"${cluster_name}"'`].Value | [0]' \
      --output text 2>/dev/null || true)"

    # Check for owned tag (value could be "owned" or just present)
    if [[ -z "${cluster_tag}" || "${cluster_tag}" == "None" ]]; then
      continue
    fi

    log_step "DELETE_CLASSIC_ELB" "Deleting Classic ELB: ${elb_name} (cluster tag present)"
    log_breakglass "Classic ELB Name: ${elb_name}"

    if aws elb delete-load-balancer --region "${region}" --load-balancer-name "${elb_name}" 2>/dev/null; then
      log_info "  Deleted Classic ELB: ${elb_name}"
      deleted_count=$((deleted_count + 1))
    else
      log_error "  Failed to delete Classic ELB: ${elb_name}"
    fi
  done

  log_info "Deleted ${deleted_count} Classic load balancers for cluster ${cluster_name}"
}

delete_target_groups_for_cluster() {
  log_step "DELETE_TARGET_GROUPS" "Listing target groups for cluster ${cluster_name}..."

  local tg_arns=""
  tg_arns="$(aws elbv2 describe-target-groups \
    --region "${region}" \
    --query 'TargetGroups[].TargetGroupArn' \
    --output text 2>/dev/null || true)"

  if [[ -z "${tg_arns}" ]]; then
    log_info "No target groups found in region."
    return 0
  fi

  local deleted_count=0
  for tg_arn in ${tg_arns}; do
    local should_delete="false"
    local match_reason=""

    # Get all tags for this target group
    local tags_json=""
    tags_json="$(aws elbv2 describe-tags \
      --region "${region}" \
      --resource-arns "${tg_arn}" \
      --query 'TagDescriptions[0].Tags' \
      --output json 2>/dev/null || echo "[]")"

    # Check multiple tag patterns for cluster ownership
    # Pattern 1: elbv2.k8s.aws/cluster = <cluster_name>
    local elbv2_cluster_tag=""
    elbv2_cluster_tag="$(echo "${tags_json}" | jq -r '.[] | select(.Key=="elbv2.k8s.aws/cluster") | .Value' 2>/dev/null || true)"
    if [[ "${elbv2_cluster_tag}" == "${cluster_name}" ]]; then
      should_delete="true"
      match_reason="elbv2.k8s.aws/cluster=${cluster_name}"
    fi

    # Pattern 2: kubernetes.io/cluster/<cluster_name> tag exists
    if [[ "${should_delete}" == "false" ]]; then
      local k8s_cluster_tag=""
      k8s_cluster_tag="$(echo "${tags_json}" | jq -r '.[] | select(.Key=="kubernetes.io/cluster/'"${cluster_name}"'") | .Value' 2>/dev/null || true)"
      if [[ -n "${k8s_cluster_tag}" ]]; then
        should_delete="true"
        match_reason="kubernetes.io/cluster/${cluster_name}"
      fi
    fi

    # Pattern 3: ingress.k8s.aws/cluster = <cluster_name>
    if [[ "${should_delete}" == "false" ]]; then
      local ingress_cluster_tag=""
      ingress_cluster_tag="$(echo "${tags_json}" | jq -r '.[] | select(.Key=="ingress.k8s.aws/cluster") | .Value' 2>/dev/null || true)"
      if [[ "${ingress_cluster_tag}" == "${cluster_name}" ]]; then
        should_delete="true"
        match_reason="ingress.k8s.aws/cluster=${cluster_name}"
      fi
    fi

    # Pattern 4: Name pattern matching k8s-<namespace>-<cluster>-*
    if [[ "${should_delete}" == "false" ]]; then
      local tg_name_check=""
      tg_name_check="$(aws elbv2 describe-target-groups \
        --region "${region}" \
        --target-group-arns "${tg_arn}" \
        --query 'TargetGroups[0].TargetGroupName' \
        --output text 2>/dev/null || true)"
      # Match pattern like k8s-<namespace>-<cluster_name_part>-<hash>
      if [[ "${tg_name_check}" =~ ^k8s-.*-${cluster_name##*-} ]]; then
        should_delete="true"
        match_reason="name-pattern=${tg_name_check}"
      fi
    fi

    if [[ "${should_delete}" == "false" ]]; then
      continue
    fi

    local tg_name=""
    tg_name="$(aws elbv2 describe-target-groups \
      --region "${region}" \
      --target-group-arns "${tg_arn}" \
      --query 'TargetGroups[0].TargetGroupName' \
      --output text 2>/dev/null || true)"

    log_step "DELETE_TARGET_GROUP" "Deleting target group: ${tg_name} (match: ${match_reason})"
    if aws elbv2 delete-target-group --region "${region}" --target-group-arn "${tg_arn}" 2>/dev/null; then
      log_info "  Deleted target group: ${tg_name}"
      deleted_count=$((deleted_count + 1))
    else
      log_warn "  Failed to delete target group: ${tg_name} (may be in use)"
    fi
  done

  log_info "Deleted ${deleted_count} target groups for cluster ${cluster_name}"
}

delete_lbs_by_cluster_tag() {
  log_step "DELETE_LBS_BY_TAG" "Scanning load balancers by cluster tag..."

  local lb_arns=""
  lb_arns="$(aws elbv2 describe-load-balancers \
    --region "${region}" \
    --query 'LoadBalancers[].LoadBalancerArn' \
    --output text 2>/dev/null || true)"

  if [[ -z "${lb_arns}" ]]; then
    log_info "No load balancers found for tag scan."
    return 0
  fi

  local deleted_count=0
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

    local lb_name=""
    lb_name="$(aws elbv2 describe-load-balancers \
      --region "${region}" \
      --load-balancer-arns "${lb_arn}" \
      --query 'LoadBalancers[0].LoadBalancerName' \
      --output text 2>/dev/null || true)"

    log_step "DELETE_LOAD_BALANCER" "Deleting load balancer: ${lb_name} (cluster tag: ${cluster_tag})"
    log_breakglass "LB ARN: ${lb_arn}"

    if aws elbv2 delete-load-balancer --region "${region}" --load-balancer-arn "${lb_arn}"; then
      log_info "  Deleted load balancer: ${lb_name}"
      deleted_count=$((deleted_count + 1))
    else
      log_error "  Failed to delete load balancer: ${lb_name}"
    fi
  done

  log_info "Deleted ${deleted_count} load balancers for cluster ${cluster_name}"
}

wait_for_lb_enis() {
  local subnet_filter="$1"
  local interval="${LB_CLEANUP_INTERVAL}"
  local max_wait="${LB_ENI_WAIT_MAX}"
  local start_epoch
  start_epoch="$(date -u +%s)"

  if [[ -z "${subnet_filter}" ]]; then
    log_info "Skipping LoadBalancer ENI wait (no subnet filter available)."
    return 0
  fi

  log_step "WAIT_LB_ENIS" "Waiting for LoadBalancer ENIs to be removed..."

  while true; do
    local enis=""
    enis="$(list_lb_enis "${subnet_filter}")"

    if [[ -z "${enis}" ]]; then
      log_info "No LoadBalancer ENIs remain."
      return 0
    fi

    log_info "LoadBalancer ENIs still present:"
    while IFS=$'\t' read -r eni_id desc status; do
      [[ -z "${eni_id}" ]] && continue
      log_breakglass "  ENI: ${eni_id} (${status}) ${desc}"
    done <<< "${enis}"

    if [[ -n "${max_wait}" && "${max_wait}" -gt 0 ]]; then
      local now_epoch
      now_epoch="$(date -u +%s)"
      local elapsed=$((now_epoch - start_epoch))
      if [[ "${elapsed}" -ge "${max_wait}" ]]; then
        log_error "Timed out after ${elapsed}s waiting for LoadBalancer ENIs."
        return 1
      fi
      log_info "  [WAIT] ${elapsed}s/${max_wait}s elapsed..."
    fi

    sleep "${interval}"
  done
}

# =============================================================================
# ARGOCD FUNCTIONS
# =============================================================================

suspend_argo_application() {
  if [[ "${SUSPEND_ARGO_APP}" != "true" ]]; then
    return 0
  fi

  log_step "SUSPEND_ARGO_APP" "Suspending Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME}..."

  if ! kubectl get crd applications.argoproj.io >/dev/null 2>&1; then
    log_info "Argo Application CRD not found; skipping."
    return 0
  fi

  if ! kubectl get ns "${ARGO_APP_NAMESPACE}" >/dev/null 2>&1; then
    log_info "Namespace ${ARGO_APP_NAMESPACE} not found; skipping."
    return 0
  fi

  if ! kubectl -n "${ARGO_APP_NAMESPACE}" get application "${ARGO_APP_NAME}" >/dev/null 2>&1; then
    log_info "Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME} not found; skipping."
    return 0
  fi

  kubectl -n "${ARGO_APP_NAMESPACE}" patch application "${ARGO_APP_NAME}" \
    --type merge \
    -p '{"spec":{"syncPolicy":null}}' >/dev/null 2>&1 || true
  log_info "Suspended Argo Application sync policy."
}

delete_argo_application() {
  if [[ "${SUSPEND_ARGO_APP}" == "true" ]]; then
    suspend_argo_application
  fi

  if [[ "${DELETE_ARGO_APP}" != "true" ]]; then
    log_info "Skipping Argo application deletion (DELETE_ARGO_APP=false)."
    return 0
  fi

  log_step "DELETE_ARGO_APP" "Deleting Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME}..."

  if [[ -z "${ARGO_APP_NAMESPACE}" || -z "${ARGO_APP_NAME}" ]]; then
    log_info "Skipping Argo application deletion (namespace/name not set)."
    return 0
  fi

  if ! kubectl get crd applications.argoproj.io >/dev/null 2>&1; then
    log_info "Argo Application CRD not found; skipping deletion."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get ns "${ARGO_APP_NAMESPACE}" >/dev/null 2>&1; then
    log_info "Namespace ${ARGO_APP_NAMESPACE} not found; skipping Argo application deletion."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ARGO_APP_NAMESPACE}" get application "${ARGO_APP_NAME}" >/dev/null 2>&1; then
    log_info "Argo application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME} not found; skipping deletion."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ARGO_APP_NAMESPACE}" delete application "${ARGO_APP_NAME}" --wait=false --ignore-not-found; then
    log_warn "Failed to delete Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME}."
  else
    log_info "Deleted Argo Application ${ARGO_APP_NAMESPACE}/${ARGO_APP_NAME}."
  fi
}

# =============================================================================
# KONG FUNCTIONS
# =============================================================================

delete_kong_resources() {
  if [[ "${DELETE_KONG_RESOURCES}" != "true" ]]; then
    log_info "Skipping Kong resource cleanup (DELETE_KONG_RESOURCES=false)."
    return 0
  fi

  log_step "DELETE_KONG" "Deleting Kong resources in ${KONG_NAMESPACE} (release=${KONG_RELEASE})..."

  if [[ -z "${KONG_NAMESPACE}" || -z "${KONG_RELEASE}" ]]; then
    log_info "Skipping Kong resource cleanup (namespace/release not set)."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get ns "${KONG_NAMESPACE}" >/dev/null 2>&1; then
    log_info "Namespace ${KONG_NAMESPACE} not found; skipping Kong resource cleanup."
    return 0
  fi

  local kong_resources=""
  kong_resources="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${KONG_NAMESPACE}" get deploy,sts,ds,svc,ingress \
    -l "app.kubernetes.io/instance=${KONG_RELEASE}" -o name 2>/dev/null || true)"

  if [[ -z "${kong_resources}" ]]; then
    log_info "No Kong resources found for release ${KONG_RELEASE}; skipping cleanup."
    return 0
  fi

  log_info "Found Kong resources:"
  echo "${kong_resources}" | while read -r res; do
    log_info "  ${res}"
  done

  kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${KONG_NAMESPACE}" delete deploy,sts,ds,svc,ingress \
    -l "app.kubernetes.io/instance=${KONG_RELEASE}" \
    --ignore-not-found --wait=false || true

  log_info "Deleted Kong resources."
}

# =============================================================================
# LB CONTROLLER FUNCTIONS
# =============================================================================

scale_down_lb_controller() {
  if [[ "${SCALE_DOWN_LB_CONTROLLER}" != "true" ]]; then
    log_info "Skipping LB controller scale down (SCALE_DOWN_LB_CONTROLLER=false)."
    return 0
  fi

  log_step "SCALE_DOWN_LB_CONTROLLER" "Scaling down ${LB_CONTROLLER_NAMESPACE}/${LB_CONTROLLER_DEPLOYMENT}..."

  if [[ -z "${LB_CONTROLLER_NAMESPACE}" || -z "${LB_CONTROLLER_DEPLOYMENT}" ]]; then
    log_info "Skipping LB controller scale down (namespace/deployment not set)."
    return 0
  fi

  if ! kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${LB_CONTROLLER_NAMESPACE}" get deploy "${LB_CONTROLLER_DEPLOYMENT}" >/dev/null 2>&1; then
    log_info "LB controller deployment not found; skipping scale down."
    return 0
  fi

  kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${LB_CONTROLLER_NAMESPACE}" scale deploy "${LB_CONTROLLER_DEPLOYMENT}" --replicas=0 || true
  log_info "Scaled down LB controller to prevent LB reprovision."
}

# =============================================================================
# LOADBALANCER SERVICE CLEANUP
# =============================================================================

cleanup_loadbalancer_services() {
  local attempt=1
  local max_attempts="${LB_CLEANUP_ATTEMPTS}"

  log_step "CLEANUP_LB_SERVICES" "Cleaning up LoadBalancer services..."

  while [[ "${attempt}" -le "${max_attempts}" ]]; do
    local services=""
    services="$(kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" get svc -A -o jsonpath='{range .items[?(@.spec.type=="LoadBalancer")]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' 2>/dev/null)"

    if [[ -z "${services}" ]]; then
      log_info "No LoadBalancer services remain."
      return 0
    fi

    log_info "LoadBalancer services still present (attempt ${attempt}/${max_attempts}):"
    echo "${services}" | while read -r svc; do
      log_info "  ${svc}"
    done

    while read -r svc; do
      [[ -z "${svc}" ]] && continue
      local ns="${svc%%/*}"
      local name="${svc##*/}"
      log_step "DELETE_LB_SERVICE" "Deleting LoadBalancer service ${ns}/${name}..."
      kubectl --request-timeout="${KUBECTL_REQUEST_TIMEOUT}" -n "${ns}" delete svc "${name}" --wait=false || true
    done <<< "${services}"

    log_info "Waiting ${LB_CLEANUP_INTERVAL}s for LoadBalancer services to be removed..."
    sleep "${LB_CLEANUP_INTERVAL}"
    attempt=$((attempt + 1))
  done

  log_warn "LoadBalancer services still present after ${max_attempts} attempts."
  return 1
}

# =============================================================================
# RDS FUNCTIONS
# =============================================================================

delete_rds_instances_for_build() {
  if [[ "${DELETE_RDS_INSTANCES}" != "true" ]]; then
    log_info "Skipping RDS instance deletion (DELETE_RDS_INSTANCES=false)."
    return 0
  fi

  local build_id="${BUILD_ID:-}"
  local rds_arns=""

  # Strategy 1: Search by BuildId tag if available
  if [[ -n "${build_id}" ]]; then
    log_step "DELETE_RDS" "Searching for RDS instances with BuildId=${build_id}..."

    rds_arns="$(aws resourcegroupstaggingapi get-resources \
      --tag-filters "Key=BuildId,Values=${build_id}" \
      --resource-type-filters "rds:db" \
      --region "${region}" \
      --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)"
  fi

  # Strategy 2: Fallback to cluster name tag if no BuildId or no results
  if [[ -z "${rds_arns}" ]]; then
    log_step "DELETE_RDS_FALLBACK" "Searching for RDS instances with kubernetes.io/cluster/${cluster_name} tag..."

    rds_arns="$(aws resourcegroupstaggingapi get-resources \
      --tag-filters "Key=kubernetes.io/cluster/${cluster_name},Values=owned" \
      --resource-type-filters "rds:db" \
      --region "${region}" \
      --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)"

    # Also try ClusterName tag
    if [[ -z "${rds_arns}" ]]; then
      rds_arns="$(aws resourcegroupstaggingapi get-resources \
        --tag-filters "Key=ClusterName,Values=${cluster_name}" \
        --resource-type-filters "rds:db" \
        --region "${region}" \
        --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)"
    fi
  fi

  # Strategy 3: Search by name pattern if no tags found
  if [[ -z "${rds_arns}" ]]; then
    log_step "DELETE_RDS_PATTERN" "Searching for RDS instances by name pattern..."

    # Extract cluster identifier suffix (last part after dash)
    local cluster_suffix="${cluster_name##*-}"
    local all_instances=""
    all_instances="$(aws rds describe-db-instances \
      --region "${region}" \
      --query "DBInstances[?contains(DBInstanceIdentifier, '${cluster_suffix}')].DBInstanceArn" \
      --output text 2>/dev/null || true)"

    if [[ -n "${all_instances}" ]]; then
      log_info "Found RDS instances by name pattern containing '${cluster_suffix}'"
      rds_arns="${all_instances}"
    fi
  fi

  if [[ -z "${rds_arns}" ]]; then
    log_info "No RDS instances found for cluster ${cluster_name}."
    return 0
  fi

  for arn in ${rds_arns}; do
    local db_identifier=""
    db_identifier="${arn##*:db:}"

    log_step "DELETE_RDS_INSTANCE" "Deleting RDS instance: ${db_identifier}"
    log_breakglass "RDS ARN: ${arn}"

    local delete_args="--db-instance-identifier ${db_identifier} --region ${region}"

    if [[ "${RDS_SKIP_FINAL_SNAPSHOT}" == "true" ]]; then
      delete_args="${delete_args} --skip-final-snapshot"
      log_info "  Skipping final snapshot (RDS_SKIP_FINAL_SNAPSHOT=true)"
    else
      local snapshot_id="${db_identifier}-final-$(date +%Y%m%d%H%M%S)"
      delete_args="${delete_args} --final-db-snapshot-identifier ${snapshot_id}"
      log_info "  Creating final snapshot: ${snapshot_id}"
    fi

    if [[ "${RDS_DELETE_AUTOMATED_BACKUPS}" == "true" ]]; then
      delete_args="${delete_args} --delete-automated-backups"
      log_info "  Deleting automated backups"
    fi

    if aws rds delete-db-instance ${delete_args} 2>/dev/null; then
      log_info "  Initiated deletion of RDS instance: ${db_identifier}"
    else
      log_warn "  Failed to delete RDS instance: ${db_identifier} (may already be deleting)"
    fi
  done

  # Delete RDS subnet groups (search by build_id or cluster name pattern)
  log_step "DELETE_RDS_SUBNET_GROUPS" "Searching for RDS subnet groups..."
  local subnet_groups=""
  local cluster_suffix="${cluster_name##*-}"

  # Try build_id first, then cluster name pattern
  if [[ -n "${build_id}" ]]; then
    subnet_groups="$(aws rds describe-db-subnet-groups \
      --region "${region}" \
      --query "DBSubnetGroups[?contains(DBSubnetGroupName, '${build_id}')].DBSubnetGroupName" \
      --output text 2>/dev/null || true)"
  fi

  if [[ -z "${subnet_groups}" ]]; then
    subnet_groups="$(aws rds describe-db-subnet-groups \
      --region "${region}" \
      --query "DBSubnetGroups[?contains(DBSubnetGroupName, '${cluster_suffix}')].DBSubnetGroupName" \
      --output text 2>/dev/null || true)"
  fi

  for sg in ${subnet_groups}; do
    log_step "DELETE_RDS_SUBNET_GROUP" "Deleting RDS subnet group: ${sg}"
    aws rds delete-db-subnet-group --db-subnet-group-name "${sg}" --region "${region}" 2>/dev/null || \
      log_warn "  Failed to delete subnet group: ${sg} (may be in use)"
  done

  # Delete RDS parameter groups (search by build_id or cluster name pattern)
  log_step "DELETE_RDS_PARAM_GROUPS" "Searching for RDS parameter groups..."
  local param_groups=""

  if [[ -n "${build_id}" ]]; then
    param_groups="$(aws rds describe-db-parameter-groups \
      --region "${region}" \
      --query "DBParameterGroups[?contains(DBParameterGroupName, '${build_id}')].DBParameterGroupName" \
      --output text 2>/dev/null || true)"
  fi

  if [[ -z "${param_groups}" ]]; then
    param_groups="$(aws rds describe-db-parameter-groups \
      --region "${region}" \
      --query "DBParameterGroups[?contains(DBParameterGroupName, '${cluster_suffix}')].DBParameterGroupName" \
      --output text 2>/dev/null || true)"
  fi

  for pg in ${param_groups}; do
    # Skip default parameter groups
    if [[ "${pg}" == default.* ]]; then
      continue
    fi
    log_step "DELETE_RDS_PARAM_GROUP" "Deleting RDS parameter group: ${pg}"
    aws rds delete-db-parameter-group --db-parameter-group-name "${pg}" --region "${region}" 2>/dev/null || \
      log_warn "  Failed to delete parameter group: ${pg} (may be in use)"
  done
}

wait_for_rds_deletion() {
  local build_id="${BUILD_ID:-}"
  if [[ -z "${build_id}" ]]; then
    return 0
  fi

  log_step "WAIT_RDS_DELETION" "Waiting for RDS instances to be deleted..."

  local max_wait=600
  local interval=30
  local start_epoch
  start_epoch="$(date -u +%s)"

  while true; do
    local rds_instances=""
    rds_instances="$(aws resourcegroupstaggingapi get-resources \
      --tag-filters "Key=BuildId,Values=${build_id}" \
      --resource-type-filters "rds:db" \
      --region "${region}" \
      --query "ResourceTagMappingList[].ResourceARN" --output text 2>/dev/null || true)"

    if [[ -z "${rds_instances}" ]]; then
      log_info "All RDS instances deleted."
      return 0
    fi

    local now_epoch
    now_epoch="$(date -u +%s)"
    local elapsed=$((now_epoch - start_epoch))

    if [[ "${elapsed}" -ge "${max_wait}" ]]; then
      log_warn "Timed out waiting for RDS deletion after ${elapsed}s. Continuing..."
      return 0
    fi

    log_info "RDS instances still deleting (${elapsed}s/${max_wait}s)..."
    for arn in ${rds_instances}; do
      local db_id="${arn##*:db:}"
      local status=""
      status="$(aws rds describe-db-instances \
        --db-instance-identifier "${db_id}" \
        --region "${region}" \
        --query 'DBInstances[0].DBInstanceStatus' \
        --output text 2>/dev/null || echo "unknown")"
      log_info "  ${db_id}: ${status}"
    done

    sleep "${interval}"
  done
}

# =============================================================================
# TERRAFORM FUNCTIONS
# =============================================================================

remove_k8s_service_accounts_from_state() {
  if [[ -z "${TF_DIR:-}" ]]; then
    return 0
  fi

  log_step "REMOVE_K8S_SA_FROM_STATE" "Removing Kubernetes service accounts from Terraform state..."
  bash "${repo_root}/bootstrap/60_tear_down_clean_up/remove-k8s-service-accounts-from-state.sh" "${TF_DIR}"
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
    log_warn "timeout command not found; running terraform destroy without a max wait."
  fi
  run_with_heartbeat "Terraform destroy in ${tf_dir}" "$@"
}

# =============================================================================
# FARGATE PROFILE FUNCTIONS
# =============================================================================

delete_fargate_profiles() {
  log_step "DELETE_FARGATE_PROFILES" "Listing Fargate profiles for cluster ${cluster_name}..."

  local profiles=""
  profiles="$(aws eks list-fargate-profiles \
    --cluster-name "${cluster_name}" \
    --region "${region}" \
    --query 'fargateProfileNames[]' \
    --output text 2>/dev/null || true)"

  if [[ -z "${profiles}" ]]; then
    log_info "No Fargate profiles found for cluster ${cluster_name}."
    return 0
  fi

  for profile in ${profiles}; do
    log_step "DELETE_FARGATE_PROFILE" "Deleting Fargate profile: ${profile}"

    if aws eks delete-fargate-profile \
        --cluster-name "${cluster_name}" \
        --fargate-profile-name "${profile}" \
        --region "${region}" 2>/dev/null; then
      log_info "  Initiated deletion of Fargate profile: ${profile}"
    else
      log_warn "  Failed to delete Fargate profile: ${profile} (may already be deleting)"
    fi
  done
}

wait_for_fargate_profile_deletion() {
  log_step "WAIT_FARGATE_PROFILES" "Waiting for Fargate profiles to be deleted..."

  local max_wait="${FARGATE_PROFILE_DELETE_TIMEOUT:-300}"
  local interval=15
  local start_epoch
  start_epoch="$(date -u +%s)"

  while true; do
    local profiles=""
    profiles="$(aws eks list-fargate-profiles \
      --cluster-name "${cluster_name}" \
      --region "${region}" \
      --query 'fargateProfileNames[]' \
      --output text 2>/dev/null || true)"

    if [[ -z "${profiles}" ]]; then
      log_info "All Fargate profiles deleted."
      return 0
    fi

    local now_epoch
    now_epoch="$(date -u +%s)"
    local elapsed=$((now_epoch - start_epoch))

    if [[ "${elapsed}" -ge "${max_wait}" ]]; then
      log_warn "Timed out waiting for Fargate profile deletion after ${elapsed}s. Continuing..."
      log_breakglass "Remaining Fargate profiles: ${profiles}"
      return 0
    fi

    log_info "Fargate profiles still deleting (${elapsed}s/${max_wait}s):"
    for profile in ${profiles}; do
      local status=""
      status="$(aws eks describe-fargate-profile \
        --cluster-name "${cluster_name}" \
        --fargate-profile-name "${profile}" \
        --region "${region}" \
        --query 'fargateProfile.status' \
        --output text 2>/dev/null || echo "UNKNOWN")"
      log_info "  ${profile}: ${status}"
    done

    sleep "${interval}"
  done
}

# =============================================================================
# NODEGROUP FUNCTIONS
# =============================================================================

delete_nodegroups_via_aws() {
  log_step "DELETE_NODEGROUPS_AWS" "Deleting nodegroups via AWS CLI..."

  local nodegroups=""
  nodegroups="$(aws eks list-nodegroups \
    --cluster-name "${cluster_name}" \
    --region "${region}" \
    --query 'nodegroups[]' \
    --output text 2>/dev/null || true)"

  if [[ -z "${nodegroups}" ]]; then
    log_info "No nodegroups found for cluster ${cluster_name}."
    return 0
  fi

  for ng in ${nodegroups}; do
    log_step "DELETE_NODEGROUP" "Deleting nodegroup: ${ng}"

    if aws eks delete-nodegroup \
        --cluster-name "${cluster_name}" \
        --nodegroup-name "${ng}" \
        --region "${region}" 2>/dev/null; then
      log_info "  Initiated deletion of nodegroup: ${ng}"
    else
      log_warn "  Failed to initiate nodegroup deletion: ${ng} (may already be deleting)"
    fi
  done
}

wait_for_nodegroup_deletion() {
  log_step "WAIT_NODEGROUPS" "Waiting for nodegroups to be deleted..."

  local max_wait="${NODEGROUP_DELETE_TIMEOUT}"
  local interval=30
  local start_epoch
  start_epoch="$(date -u +%s)"

  while true; do
    local nodegroups=""
    nodegroups="$(aws eks list-nodegroups \
      --cluster-name "${cluster_name}" \
      --region "${region}" \
      --query 'nodegroups[]' \
      --output text 2>/dev/null || true)"

    if [[ -z "${nodegroups}" ]]; then
      log_info "All nodegroups deleted."
      return 0
    fi

    local now_epoch
    now_epoch="$(date -u +%s)"
    local elapsed=$((now_epoch - start_epoch))

    if [[ "${elapsed}" -ge "${max_wait}" ]]; then
      log_error "Timed out waiting for nodegroup deletion after ${elapsed}s."
      log_breakglass "Remaining nodegroups: ${nodegroups}"
      return 1
    fi

    log_info "Nodegroups still deleting (${elapsed}s/${max_wait}s):"
    for ng in ${nodegroups}; do
      local status=""
      status="$(aws eks describe-nodegroup \
        --cluster-name "${cluster_name}" \
        --nodegroup-name "${ng}" \
        --region "${region}" \
        --query 'nodegroup.status' \
        --output text 2>/dev/null || echo "UNKNOWN")"
      log_info "  ${ng}: ${status}"
    done

    sleep "${interval}"
  done
}

# =============================================================================
# MAIN TEARDOWN SEQUENCE
# =============================================================================

log_info "============================================================================="
log_info "TEARDOWN V3 STARTING"
log_info "============================================================================="
log_info "Cluster: ${cluster_name}"
log_info "Region: ${region}"
log_info "Build ID: ${BUILD_ID:-unset}"
log_info "Terraform Dir: ${TF_DIR:-unset}"
log_info "Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
log_info "============================================================================="

cluster_exists="true"
kube_access="true"

# =============================================================================
# STAGE 1: CLUSTER VALIDATION
# =============================================================================

stage_banner "1" "CLUSTER VALIDATION"

log_step "VALIDATE_CLUSTER" "Checking if cluster ${cluster_name} exists..."
if ! aws eks describe-cluster --name "${cluster_name}" --region "${region}" >/dev/null 2>&1; then
  log_warn "Cluster ${cluster_name} not found in AWS."
  cluster_exists="false"
else
  log_info "Cluster ${cluster_name} exists."

  log_step "UPDATE_KUBECONFIG" "Updating kubeconfig for ${cluster_name}..."
  if aws eks update-kubeconfig --name "${cluster_name}" --region "${region}" 2>/dev/null; then
    log_info "Kubeconfig updated."

    log_step "VALIDATE_KUBE_ACCESS" "Validating Kubernetes API access..."
    if kubectl get ns >/dev/null 2>&1; then
      log_info "Kubernetes API is accessible."
    else
      log_warn "Kubernetes API not reachable or unauthorized."
      kube_access="false"
    fi
  else
    log_warn "Failed to update kubeconfig."
    kube_access="false"
  fi
fi

log_info "Cluster status: exists=${cluster_exists}, kube_access=${kube_access}"

stage_done "1" "CLUSTER VALIDATION"

# =============================================================================
# STAGE 2: PRE-DESTROY CLEANUP (K8S RESOURCES)
# =============================================================================

stage_banner "2" "PRE-DESTROY CLEANUP"

if [[ "${cluster_exists}" == "false" ]]; then
  log_info "Cluster does not exist; skipping Kubernetes pre-destroy cleanup."
elif [[ "${kube_access}" == "false" ]]; then
  log_warn "Kubernetes API not accessible; skipping k8s-based cleanup."
  log_info "Will attempt AWS-based LoadBalancer cleanup instead."

  if [[ "${WAIT_FOR_LB_ENIS}" == "true" ]]; then
    subnet_filter="$(get_cluster_subnet_filter || true)"
    if [[ "${FORCE_DELETE_LBS}" == "true" ]]; then
      log_step "AWS_LB_CLEANUP" "Attempting AWS-only LoadBalancer cleanup..."
      delete_lbs_by_cluster_tag || true
      delete_classic_elbs_by_cluster_tag || true
      if [[ "${DELETE_TARGET_GROUPS}" == "true" ]]; then
        delete_target_groups_for_cluster || true
      fi
    fi
    wait_for_lb_enis "${subnet_filter}" || true
  fi
else
  # Full k8s-based cleanup
  delete_argo_application
  delete_kong_resources

  # Clean up Ingress resources before LoadBalancer services
  cleanup_ingress_resources

  log_step "RUN_PRE_DESTROY_SCRIPT" "Running pre-destroy cleanup script..."
  if [[ -f "${repo_root}/bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh" ]]; then
    bash "${repo_root}/bootstrap/60_tear_down_clean_up/pre-destroy-cleanup.sh" "${cluster_name}" "${region}" --yes || true
  fi

  cleanup_loadbalancer_services || true

  # Wait for LB services to be removed
  log_step "WAIT_LB_SERVICES" "Waiting for LoadBalancer services to be removed..."
  lb_wait_rc=0
  wait_with_timeout \
    "LoadBalancer services removal" \
    "test -z \"\$(list_lb_services)\"" \
    "${HEARTBEAT_INTERVAL}" \
    "${LB_CLEANUP_MAX_WAIT}" || lb_wait_rc=$?

  if [[ "${lb_wait_rc}" -ne 0 ]]; then
    remaining_services="$(list_lb_services)"
    if [[ -z "${remaining_services}" ]]; then
      log_info "No LoadBalancer services remain after wait timeout."
    else
      log_warn "LoadBalancer services still present after wait:"
      describe_lb_service_finalizers "${remaining_services}"

      if [[ "${FORCE_DELETE_LB_FINALIZERS}" == "true" ]]; then
        log_breakglass "Removing stuck LoadBalancer service finalizers..."
        remove_lb_service_finalizers "${remaining_services}"

        wait_with_timeout \
          "LoadBalancer services after finalizer removal" \
          "test -z \"\$(list_lb_services)\"" \
          "${HEARTBEAT_INTERVAL}" \
          "${LB_FINALIZER_WAIT_MAX}" || true
      fi
    fi
  fi

  scale_down_lb_controller

  # Wait for LB ENIs
  if [[ "${WAIT_FOR_LB_ENIS}" == "true" ]]; then
    subnet_filter="$(get_cluster_subnet_filter || true)"
    if ! wait_for_lb_enis "${subnet_filter}"; then
      if [[ "${FORCE_DELETE_LBS}" == "true" ]]; then
        log_breakglass "Force deleting remaining load balancers..."
        delete_lbs_by_cluster_tag || true
        delete_classic_elbs_by_cluster_tag || true

        if [[ "${DELETE_TARGET_GROUPS}" == "true" ]]; then
          delete_target_groups_for_cluster || true
        fi

        remaining_enis="$(list_lb_enis "${subnet_filter}")"
        if [[ -n "${remaining_enis}" ]]; then
          log_breakglass "ENIs still present after LB deletion. Waiting..."
          wait_for_lb_enis "${subnet_filter}" || true
        fi
      fi
    fi
  fi
fi

stage_done "2" "PRE-DESTROY CLEANUP"

# =============================================================================
# STAGE 3: DRAIN NODEGROUPS (K8S-BASED)
# =============================================================================

stage_banner "3" "DRAIN NODEGROUPS"

if [[ "${cluster_exists}" == "false" ]]; then
  log_info "Cluster does not exist; skipping nodegroup drain."
elif [[ "${kube_access}" == "false" ]]; then
  log_info "Kubernetes API not accessible; skipping nodegroup drain (will delete via AWS)."
elif [[ "${SKIP_DRAIN_NODEGROUPS:-false}" == "true" ]]; then
  log_info "Skipping nodegroup drain (SKIP_DRAIN_NODEGROUPS=true)."
else
  nodegroups="$(aws eks list-nodegroups --cluster-name "${cluster_name}" --region "${region}" --query 'nodegroups[]' --output text 2>/dev/null || true)"
  if [[ -z "${nodegroups}" ]]; then
    log_info "No nodegroups found."
  else
    for ng in ${nodegroups}; do
      log_step "DRAIN_NODEGROUP" "Draining nodegroup ${ng}..."
      RELAX_PDB="${RELAX_PDB:-true}" bash "${repo_root}/bootstrap/60_tear_down_clean_up/drain-nodegroup.sh" "${ng}" || \
        log_warn "Failed to drain nodegroup ${ng}; continuing..."
    done
  fi
fi

stage_done "3" "DRAIN NODEGROUPS"

# =============================================================================
# STAGE 4: DELETE NODEGROUPS (AWS-BASED)
# =============================================================================

stage_banner "4" "DELETE NODEGROUPS"

# KEY FIX: Delete nodegroups via AWS CLI even when k8s API is unavailable
# Only skip if cluster doesn't exist
if [[ "${cluster_exists}" == "false" ]]; then
  log_info "Cluster does not exist; skipping nodegroup and Fargate profile deletion."
elif [[ "${DELETE_NODEGROUPS:-true}" != "true" ]]; then
  log_info "Skipping nodegroup deletion (DELETE_NODEGROUPS=false)."
else
  # Delete Fargate profiles first (they can block cluster deletion)
  if [[ "${DELETE_FARGATE_PROFILES:-true}" == "true" ]]; then
    delete_fargate_profiles
    if [[ "${WAIT_FOR_FARGATE_DELETE:-true}" == "true" ]]; then
      wait_for_fargate_profile_deletion
    fi
  fi

  delete_nodegroups_via_aws

  if [[ "${WAIT_FOR_NODEGROUP_DELETE:-true}" == "true" ]]; then
    wait_for_nodegroup_deletion
  fi
fi

stage_done "4" "DELETE NODEGROUPS"

# =============================================================================
# STAGE 5: DELETE RDS INSTANCES
# =============================================================================

stage_banner "5" "DELETE RDS INSTANCES"

if [[ "${DELETE_RDS_INSTANCES}" == "true" ]]; then
  # The function now has fallback logic for missing BUILD_ID
  delete_rds_instances_for_build
  # Don't wait for RDS deletion - it can take a long time
  # Orphan cleanup will catch any remaining instances
else
  log_info "Skipping RDS cleanup (DELETE_RDS_INSTANCES=${DELETE_RDS_INSTANCES})."
fi

stage_done "5" "DELETE RDS INSTANCES"

# =============================================================================
# STAGE 6: TERRAFORM DESTROY
# =============================================================================

stage_banner "6" "TERRAFORM DESTROY"

if [[ -n "${TF_DIR:-}" ]]; then
  require_cmd terraform
  tf_failed=false

  if [[ "${REMOVE_K8S_SA_FROM_STATE:-true}" == "true" ]]; then
    log_step "REMOVE_K8S_SA" "Removing Kubernetes service accounts from state..."
    if ! remove_k8s_service_accounts_from_state; then
      log_warn "Failed to remove Kubernetes service accounts from state."
    fi
  fi

  log_step "TF_DESTROY" "Running terraform destroy in ${TF_DIR}..."
  destroy_rc=0
  if [[ "${TF_AUTO_APPROVE:-false}" == "true" ]]; then
    run_tf_destroy "${TF_DIR}" terraform -chdir="${TF_DIR}" destroy -auto-approve || destroy_rc=$?
  else
    run_tf_destroy "${TF_DIR}" terraform -chdir="${TF_DIR}" destroy || destroy_rc=$?
  fi

  if [[ "${destroy_rc}" -ne 0 ]]; then
    log_warn "Terraform destroy failed with exit code ${destroy_rc}."
    tf_failed=true

    # Retry after LB cleanup if enabled
    if [[ "${TF_DESTROY_RETRY_ON_LB_CLEANUP}" == "true" && "${WAIT_FOR_LB_ENIS}" == "true" ]]; then
      subnet_filter="$(get_cluster_subnet_filter || true)"
      if [[ -n "${subnet_filter}" ]]; then
        remaining_enis="$(list_lb_enis "${subnet_filter}")"
        if [[ -n "${remaining_enis}" ]]; then
          log_breakglass "Terraform failed; attempting LB cleanup and retry..."

          if [[ "${FORCE_DELETE_LBS}" == "true" ]]; then
            delete_lbs_by_cluster_tag || true
            delete_classic_elbs_by_cluster_tag || true
            if [[ "${DELETE_TARGET_GROUPS}" == "true" ]]; then
              delete_target_groups_for_cluster || true
            fi
          fi

          wait_for_lb_enis "${subnet_filter}" || true

          log_step "TF_DESTROY_RETRY" "Retrying terraform destroy..."
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

  if [[ "${tf_failed}" == "true" ]]; then
    log_error "Terraform destroy ultimately failed."
  else
    log_info "Terraform destroy completed successfully."
  fi
else
  # No TF_DIR - delete cluster via AWS CLI if requested
  if [[ "${DELETE_CLUSTER:-true}" == "true" && "${cluster_exists}" == "true" ]]; then
    log_step "DELETE_CLUSTER_AWS" "Deleting EKS cluster via AWS CLI..."

    if aws eks delete-cluster --name "${cluster_name}" --region "${region}" 2>/dev/null; then
      log_info "Initiated cluster deletion."

      log_step "WAIT_CLUSTER_DELETED" "Waiting for cluster to be deleted..."
      run_with_heartbeat "Cluster deletion" \
        aws eks wait cluster-deleted --name "${cluster_name}" --region "${region}" || \
        log_warn "Cluster deletion wait timed out; continuing..."
    else
      log_warn "Failed to delete cluster (may already be deleted)."
    fi
  else
    log_info "Skipping cluster deletion (DELETE_CLUSTER=false or cluster doesn't exist)."
  fi
fi

stage_done "6" "TERRAFORM DESTROY"

# =============================================================================
# STAGE 7: ORPHAN CLEANUP
# =============================================================================

stage_banner "7" "ORPHAN CLEANUP"

if [[ "${CLEANUP_ORPHANS:-false}" != "true" ]]; then
  log_info "Skipping orphan cleanup (CLEANUP_ORPHANS=false)."
elif [[ "${ORPHAN_CLEANUP_MODE}" == "none" ]]; then
  log_info "Skipping orphan cleanup (ORPHAN_CLEANUP_MODE=none)."
elif [[ -z "${BUILD_ID:-}" ]]; then
  log_error "ORPHAN_CLEANUP_MODE=${ORPHAN_CLEANUP_MODE} but BUILD_ID is not set."
  exit 1
else
  cleanup_dry_run="false"
  if [[ "${ORPHAN_CLEANUP_MODE}" == "dry_run" ]]; then
    cleanup_dry_run="true"
  fi

  log_step "ORPHAN_CLEANUP" "Running orphan cleanup (mode=${ORPHAN_CLEANUP_MODE}, dry_run=${cleanup_dry_run})..."

  DRY_RUN="${cleanup_dry_run}" run_with_heartbeat "Orphan cleanup for BuildId=${BUILD_ID}" \
    bash "${repo_root}/bootstrap/60_tear_down_clean_up/cleanup-orphans.sh" "${BUILD_ID}" "${region}"
fi

stage_done "7" "ORPHAN CLEANUP"

# =============================================================================
# STAGE 8: TEARDOWN COMPLETE
# =============================================================================

stage_banner "8" "TEARDOWN COMPLETE"

log_info "============================================================================="
log_info "TEARDOWN V3 COMPLETED SUCCESSFULLY"
log_info "============================================================================="
log_info "Cluster: ${cluster_name}"
log_info "Region: ${region}"
log_info "Completed: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
log_info "============================================================================="

stage_done "8" "TEARDOWN COMPLETE"
