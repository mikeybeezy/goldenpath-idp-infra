#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"
namespace="${3:-kong-system}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster_name> <region> [namespace]" >&2
  exit 1
fi

# Ensure kubeconfig is pointed at the target cluster.
aws eks update-kubeconfig --region "${region}" --name "${cluster_name}"

# Warn if the AWS Load Balancer Controller is not running.
if ! kubectl -n kube-system get deployment aws-load-balancer-controller >/dev/null 2>&1; then
  echo "Warning: aws-load-balancer-controller not detected. Kong LoadBalancer services may not provision as expected." >&2
fi

# Validate that Argo CD has reconciled Kong into the cluster.
if ! kubectl -n "${namespace}" get deployment -l app.kubernetes.io/name=kong >/dev/null 2>&1; then
  echo "Kong deployment not found in ${namespace}. Ensure the Argo CD app has synced." >&2
  exit 1
fi

# Wait for Kong deployments to be ready and print services.
kubectl -n "${namespace}" rollout status deployment -l app.kubernetes.io/name=kong --timeout=180s
kubectl -n "${namespace}" get svc
