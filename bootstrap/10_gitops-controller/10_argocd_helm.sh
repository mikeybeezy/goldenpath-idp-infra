#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-}"
region="${2:-}"
values_file="${3:-gitops/helm/argocd/values/dev.yaml}"

if [[ -z "${cluster_name}" || -z "${region}" ]]; then
  echo "Usage: $0 <cluster_name> <region> [values_file]" >&2
  exit 1
fi

# Ensure kubeconfig is pointed at the target cluster.
aws eks update-kubeconfig --region "${region}" --name "${cluster_name}"

# Add and update the Argo Helm repo.
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Create the namespace if it does not exist.
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade Argo CD using the provided values file.
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --values "${values_file}"

# Wait for the Argo CD server deployment to be ready.
kubectl -n argocd rollout status deployment/argocd-server --timeout=180s
kubectl -n argocd get svc
