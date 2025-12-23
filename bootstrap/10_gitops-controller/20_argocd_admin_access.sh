#!/usr/bin/env bash
set -euo pipefail

action="${1:-}"
namespace="${2:-argocd}"

# Validate action input early for clear usage errors.
if [[ "${action}" != "disable" && "${action}" != "enable" ]]; then
  echo "Usage: $0 <disable|enable> [namespace]" >&2
  exit 1
fi

# Write a small audit log alongside other smoke-test artifacts.
timestamp="$(date -u +"%Y%m%dT%H%M%SZ")"
out_dir="bootstrap/40_smoke-tests/audit"
mkdir -p "${out_dir}"
log_file="${out_dir}/argocd-admin-${timestamp}.log"

if [[ "${action}" == "disable" ]]; then
  # Patch Argo CD config to disable the admin account.
  kubectl -n "${namespace}" patch cm argocd-cm \
    --type merge \
    -p '{"data":{"admin.enabled":"false"}}' \
    | tee -a "${log_file}"

  # Record the action for later audits.
  echo "Argo CD admin account disabled at ${timestamp}" | tee -a "${log_file}"
else
  # Patch Argo CD config to re-enable the admin account.
  kubectl -n "${namespace}" patch cm argocd-cm \
    --type merge \
    -p '{"data":{"admin.enabled":"true"}}' \
    | tee -a "${log_file}"

  # Record the action for later audits.
  echo "Argo CD admin account enabled at ${timestamp}" | tee -a "${log_file}"
fi

# Point the operator to the audit log location.
echo "Audit log written to ${log_file}"
