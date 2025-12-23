#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"
namespace="${3:-cert-manager}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster_name> <region> [namespace]" >&2
  exit 1
fi

# Ensure kubeconfig is pointed at the target cluster.
aws eks update-kubeconfig --region "${region}" --name "${cluster_name}"

# Validate that Argo CD has reconciled cert-manager into the cluster.
if ! kubectl -n "${namespace}" get deployment cert-manager >/dev/null 2>&1; then
  echo "cert-manager deployment not found in ${namespace}. Ensure the Argo CD app has synced." >&2
  exit 1
fi

# Wait for cert-manager to be ready.
kubectl -n "${namespace}" rollout status deployment/cert-manager --timeout=180s
kubectl -n "${namespace}" rollout status deployment/cert-manager-webhook --timeout=180s
