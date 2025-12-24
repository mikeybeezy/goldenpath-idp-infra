#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster_name> <region>" >&2
  exit 1
fi

# Update kubeconfig to target the cluster and verify node readiness.
aws eks update-kubeconfig --region "${region}" --name "${cluster_name}"
kubectl get nodes

# Install Metrics Server and wait for it to become ready.
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system rollout status deployment/metrics-server --timeout=120s

# Print node metrics as a quick validation.
kubectl top nodes
