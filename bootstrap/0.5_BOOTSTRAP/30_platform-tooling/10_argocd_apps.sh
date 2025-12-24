#!/usr/bin/env bash
set -euo pipefail

env_name="${1:-}"

if [[ -z "${env_name}" ]]; then
  echo "Usage: $0 <env>" >&2
  exit 1
fi

script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "${script_root}" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${repo_root}" ]]; then
  repo_root="$(cd "${script_root}/../../.." && pwd)"
fi

# Apply Argo CD Application manifests for the chosen environment.
kubectl apply -f "${repo_root}/gitops/argocd/apps/${env_name}"

# Show the created Application resources for quick confirmation.
kubectl -n argocd get applications
