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
# Use EXCLUDE_APPS (comma-separated basenames) to skip specific apps.
apps_dir="${repo_root}/gitops/argocd/apps/${env_name}"
exclude_apps="${EXCLUDE_APPS:-}"

if [[ -z "${exclude_apps}" ]]; then
  kubectl apply -f "${apps_dir}"
else
  IFS=',' read -r -a exclude_list <<< "${exclude_apps}"
  for app_file in "${apps_dir}"/*.yaml; do
    app_name="$(basename "${app_file}" .yaml)"
    skip=false
    for exclude in "${exclude_list[@]}"; do
      if [[ "${app_name}" == "${exclude}" ]]; then
        skip=true
        break
      fi
    done
    if [[ "${skip}" == "true" ]]; then
      continue
    fi
    kubectl apply -f "${app_file}"
  done
fi

# Show the created Application resources for quick confirmation.
kubectl -n argocd get applications
