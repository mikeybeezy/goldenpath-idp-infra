#!/usr/bin/env bash
set -euo pipefail

# Remove Kubernetes service accounts from Terraform state so destroy can proceed
# after the cluster is gone.

tf_dir="${1:-}"

if [[ -z "${tf_dir}" ]]; then
  echo "Usage: $0 <terraform-dir>" >&2
  exit 1
fi

if ! command -v terraform >/dev/null; then
  echo "Missing required command: terraform" >&2
  exit 1
fi

state_items="$(terraform -chdir="${tf_dir}" state list 2>/dev/null | \
  grep -E '^(kubernetes_service_account_v1\.|module\.eks\\[0\\]\\.kubernetes_service_account_v1)')"

if [[ -z "${state_items}" ]]; then
  echo "No Kubernetes service accounts found in state."
  exit 0
fi

echo "Removing Kubernetes service accounts from Terraform state:"
echo "${state_items}"

while read -r addr; do
  if [[ -n "${addr}" ]]; then
    terraform -chdir="${tf_dir}" state rm "${addr}"
  fi
done <<< "${state_items}"

echo "Kubernetes service accounts removed from state."
