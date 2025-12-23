#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"
values_file="${3:-}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster_name> <region> [values_file]" >&2
  exit 1
fi

# Ensure kubeconfig is pointed at the target cluster.
aws eks update-kubeconfig --region "${region}" --name "${cluster_name}"

# Warn if the AWS Load Balancer Controller is not running.
if ! kubectl -n kube-system get deployment aws-load-balancer-controller >/dev/null 2>&1; then
  echo "Warning: aws-load-balancer-controller not detected. Kong LoadBalancer services may not provision as expected." >&2
fi

# Add and update the Kong Helm repo.
helm repo add kong https://charts.konghq.com
helm repo update

# Create the namespace if it does not exist.
kubectl create namespace kong --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade Kong, using a values file if provided.
if [[ -n "${values_file}" ]]; then
  helm upgrade --install kong kong/kong \
    --namespace kong \
    --values "${values_file}"
else
  helm upgrade --install kong kong/kong \
    --namespace kong
fi

# Wait for the controller deployment to be ready and print services.
kubectl -n kong rollout status deployment/kong-controller --timeout=180s
kubectl -n kong get svc
