#!/usr/bin/env bash
# =============================================================================
# GoldenPath IDP Bootstrap v4 - ArgoCD-First Architecture
# =============================================================================
# Supersedes: v3 (goldenpath-idp-bootstrap-v3.sh)
# Implements: ADR-0180 (ArgoCD Orchestrator Contract)
#
# Key difference from v3:
#   v3: Terraform → Shell script orchestration → kubectl apply per app
#   v4: Terraform → ArgoCD orchestrates everything
#
# Terraform now deploys:
#   - EKS cluster
#   - ArgoCD (helm_release)
#   - AWS Load Balancer Controller (helm_release)
#   - All ArgoCD Applications (bootstrap_apps helm_release)
#
# This script is a thin wrapper that:
#   1. Runs Terraform apply
#   2. Waits for ArgoCD apps to sync
#   3. Runs validation checks
#
# Usage:
#   TF_DIR=envs/dev bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v4.sh
#   OR
#   make deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4
# =============================================================================
set -euo pipefail

script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "${script_root}" rev-parse --show-toplevel 2>/dev/null || pwd)"

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
TF_DIR="${TF_DIR:-envs/dev}"
REGION="${REGION:-eu-west-2}"
LIFECYCLE="${LIFECYCLE:-persistent}"
BUILD_ID="${BUILD_ID:-}"
TF_AUTO_APPROVE="${TF_AUTO_APPROVE:-false}"
SKIP_ARGO_SYNC_WAIT="${SKIP_ARGO_SYNC_WAIT:-false}"
ARGO_SYNC_TIMEOUT="${ARGO_SYNC_TIMEOUT:-600s}"

# Resolve TF_DIR to absolute path
if [[ "${TF_DIR}" != /* ]]; then
  TF_DIR="${repo_root}/${TF_DIR}"
fi

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
err() { log "ERROR: $*" >&2; }
die() { err "$*"; exit 1; }

require_cmd() {
  command -v "$1" >/dev/null || die "Required command not found: $1"
}

# -----------------------------------------------------------------------------
# Preflight
# -----------------------------------------------------------------------------
log "=== GoldenPath IDP Bootstrap v4 ==="
log "TF_DIR: ${TF_DIR}"
log "LIFECYCLE: ${LIFECYCLE}"
log "BUILD_ID: ${BUILD_ID:-<none>}"
log "REGION: ${REGION}"

require_cmd terraform
require_cmd kubectl
require_cmd aws

[[ -d "${TF_DIR}" ]] || die "TF_DIR does not exist: ${TF_DIR}"

# -----------------------------------------------------------------------------
# Stage 1: Terraform Apply (Two-Pass for Fresh Deployments)
# -----------------------------------------------------------------------------
log "=== Stage 1: Terraform Apply ==="

# Base vars for all applies
tf_base_vars=()
tf_base_vars+=(-var="cluster_lifecycle=${LIFECYCLE}")
if [[ -n "${BUILD_ID}" ]]; then
  tf_base_vars+=(-var="build_id=${BUILD_ID}")
else
  tf_base_vars+=(-var="build_id=")
fi

tf_approve_flag=""
if [[ "${TF_AUTO_APPROVE}" == "true" ]]; then
  tf_approve_flag="-auto-approve"
fi

# Determine cluster name based on lifecycle and build_id
if [[ "${LIFECYCLE}" == "ephemeral" && -n "${BUILD_ID}" ]]; then
  EXPECTED_CLUSTER="goldenpath-dev-eks-${BUILD_ID}"
else
  EXPECTED_CLUSTER="goldenpath-dev-eks"
fi

# Check if EKS cluster exists in AWS
log "Checking if EKS cluster ${EXPECTED_CLUSTER} exists..."
if aws eks describe-cluster --name "${EXPECTED_CLUSTER}" --region "${REGION}" &>/dev/null; then
  log "Cluster exists - single-pass apply with K8s resources enabled"
  CLUSTER_EXISTS=true
else
  log "Cluster does not exist - will use two-pass apply"
  CLUSTER_EXISTS=false
fi

if [[ "${CLUSTER_EXISTS}" == "false" ]]; then
  # -------------------------------------------------------------------------
  # Pass 1: Create EKS cluster using -target (avoids K8s provider evaluation)
  # The K8s/Helm/kubectl providers depend on EKS outputs, so we must create
  # EKS first using -target to prevent "values cannot be determined" errors.
  # -------------------------------------------------------------------------
  log "=== Pass 1/2: Creating EKS cluster (using -target) ==="
  tf_vars_pass1=("${tf_base_vars[@]}")
  tf_vars_pass1+=(-var="apply_kubernetes_addons=false")
  tf_vars_pass1+=(-var="enable_k8s_resources=false")

  # Target foundation resources that don't require K8s providers
  tf_targets=(
    -target=module.vpc
    -target=module.subnets
    -target=module.public_route_table
    -target=module.private_route_table
    -target=aws_eip.nat
    -target=aws_nat_gateway.this
    -target=module.web_security_group
    -target=module.compute
    -target=module.eks
    -target=module.iam
    -target=module.ecr_repositories
    -target=module.app_secrets
    -target=module.route53
  )

  log "Running: terraform -chdir=${TF_DIR} apply ${tf_approve_flag} ${tf_targets[*]} ${tf_vars_pass1[*]}"
  terraform -chdir="${TF_DIR}" apply ${tf_approve_flag} "${tf_targets[@]}" "${tf_vars_pass1[@]}"
  log "Pass 1 complete - EKS cluster created."

  # -------------------------------------------------------------------------
  # Pass 2: Create K8s resources (full apply, EKS now exists)
  # -------------------------------------------------------------------------
  log "=== Pass 2/2: Creating K8s resources (ArgoCD, addons) ==="
  tf_vars_pass2=("${tf_base_vars[@]}")
  tf_vars_pass2+=(-var="apply_kubernetes_addons=true")
  tf_vars_pass2+=(-var="enable_k8s_resources=true")

  log "Running: terraform -chdir=${TF_DIR} apply ${tf_approve_flag} ${tf_vars_pass2[*]}"
  terraform -chdir="${TF_DIR}" apply ${tf_approve_flag} "${tf_vars_pass2[@]}"
  log "Pass 2 complete - K8s resources created."
else
  # -------------------------------------------------------------------------
  # Single Pass: Cluster exists, apply everything
  # -------------------------------------------------------------------------
  tf_vars=("${tf_base_vars[@]}")
  tf_vars+=(-var="apply_kubernetes_addons=true")
  tf_vars+=(-var="enable_k8s_resources=true")

  log "Running: terraform -chdir=${TF_DIR} apply ${tf_approve_flag} ${tf_vars[*]}"
  terraform -chdir="${TF_DIR}" apply ${tf_approve_flag} "${tf_vars[@]}"
fi

log "Terraform apply complete."

# -----------------------------------------------------------------------------
# Stage 2: Get Cluster Context
# -----------------------------------------------------------------------------
log "=== Stage 2: Cluster Context ==="

# Extract cluster name from Terraform output
CLUSTER_NAME=$(terraform -chdir="${TF_DIR}" output -raw cluster_name 2>/dev/null || echo "")
if [[ -z "${CLUSTER_NAME}" ]]; then
  die "Could not determine cluster name from Terraform output"
fi

log "Cluster: ${CLUSTER_NAME}"
log "Updating kubeconfig..."
aws eks update-kubeconfig --name "${CLUSTER_NAME}" --region "${REGION}"

# Verify connectivity
kubectl cluster-info || die "Cannot connect to cluster"
log "Cluster context ready."

# -----------------------------------------------------------------------------
# Stage 3: Wait for ArgoCD Apps to Sync
# -----------------------------------------------------------------------------
log "=== Stage 3: ArgoCD Sync Wait ==="

if [[ "${SKIP_ARGO_SYNC_WAIT}" == "true" ]]; then
  log "Skipping ArgoCD sync wait (SKIP_ARGO_SYNC_WAIT=true)"
else
  log "Waiting for ArgoCD apps to become Healthy (timeout: ${ARGO_SYNC_TIMEOUT})..."

  # Wait for ArgoCD to be ready first
  kubectl -n argocd rollout status deployment/argocd-server --timeout=300s || \
    die "ArgoCD server not ready"

  # List apps
  log "ArgoCD Applications:"
  kubectl -n argocd get applications -o wide || true

  # Wait for all apps to be healthy
  # Note: This may timeout if some apps have issues, which is expected behavior
  if kubectl -n argocd wait --for=jsonpath='{.status.health.status}'=Healthy \
      application --all --timeout="${ARGO_SYNC_TIMEOUT}" 2>/dev/null; then
    log "All ArgoCD apps are Healthy."
  else
    log "WARNING: Some apps may not be Healthy yet. Check ArgoCD UI for details."
    kubectl -n argocd get applications \
      -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status
  fi
fi

# -----------------------------------------------------------------------------
# Stage 4: Validation
# -----------------------------------------------------------------------------
log "=== Stage 4: Validation ==="

log "Nodes:"
kubectl get nodes -o wide

log ""
log "ArgoCD Applications:"
kubectl -n argocd get applications \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status

log ""
log "Kong Services:"
kubectl -n kong-system get svc 2>/dev/null || log "Kong namespace not found (may be expected for Tier 0-1)"

# Run audit script if it exists
AUDIT_SCRIPT="${repo_root}/bootstrap/50_smoke-tests/20_audit.sh"
if [[ -x "${AUDIT_SCRIPT}" ]]; then
  log ""
  log "Running audit checks..."
  bash "${AUDIT_SCRIPT}" "${CLUSTER_NAME}" "${REGION}" || log "Audit completed with warnings"
fi

# -----------------------------------------------------------------------------
# Complete
# -----------------------------------------------------------------------------
log "=== Bootstrap v4 Complete ==="
log ""
log "Summary:"
log "  Cluster: ${CLUSTER_NAME}"
log "  Lifecycle: ${LIFECYCLE}"
log "  Region: ${REGION}"
log ""
log "Next steps:"
log "  - Check ArgoCD UI for app status"
log "  - Verify DNS records in Route53"
log "  - Test service endpoints"
log ""
log "Quick checks:"
log "  kubectl -n argocd get applications"
log "  kubectl get nodes"
log "  kubectl -n kong-system get svc"
