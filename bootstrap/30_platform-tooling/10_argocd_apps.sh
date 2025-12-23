#!/usr/bin/env bash
set -euo pipefail

env_name="${1:-}"

if [[ -z "${env_name}" ]]; then
  echo "Usage: $0 <env>" >&2
  exit 1
fi

# Apply Argo CD Application manifests for the chosen environment.
kubectl apply -f "gitops/argocd/apps/${env_name}"

# Show the created Application resources for quick confirmation.
kubectl -n argocd get applications
